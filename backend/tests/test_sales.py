"""
Tests for sales and purchase flow — including inventory impact.
"""
import pytest


class TestSalesFlow:
    """End-to-end sales workflow tests."""

    def test_create_sale(self, client, sample_product):
        """Create a sale and verify the response."""
        response = client.post(
            "/api/sales",
            json={
                "customer_name": "Walk-in Customer",
                "discount": 0,
                "paid": 100,
                "payment_method": "كاش",
                "items": [
                    {
                        "product_id": sample_product.id,
                        "quantity": 1,
                        "unit_price": 100,
                    }
                ],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["invoice_no"] is not None
        assert float(data["total"]) == 100.0
        assert len(data["items"]) == 1

    def test_create_sale_reduces_inventory(self, client, db, sample_product):
        """Selling a product should reduce its stock quantity."""
        original_qty = sample_product.quantity
        qty_to_sell = 3

        response = client.post(
            "/api/sales",
            json={
                "paid": 300,
                "items": [
                    {
                        "product_id": sample_product.id,
                        "quantity": qty_to_sell,
                        "unit_price": 100,
                    }
                ],
            },
        )
        assert response.status_code == 200

        # Refresh product from DB
        db.refresh(sample_product)
        assert sample_product.quantity == original_qty - qty_to_sell

    def test_create_sale_insufficient_stock(self, client, sample_product):
        """Attempting to sell more than available stock should fail."""
        response = client.post(
            "/api/sales",
            json={
                "paid": 0,
                "items": [
                    {
                        "product_id": sample_product.id,
                        "quantity": sample_product.quantity + 999,
                        "unit_price": 100,
                    }
                ],
            },
        )
        assert response.status_code == 400

    def test_create_sale_invalid_product(self, client):
        """Selling a non-existent product should fail."""
        response = client.post(
            "/api/sales",
            json={
                "paid": 0,
                "items": [
                    {"product_id": 99999, "quantity": 1, "unit_price": 100}
                ],
            },
        )
        assert response.status_code == 400

    def test_list_sales(self, client, sample_product):
        """Create a sale then list sales."""
        client.post(
            "/api/sales",
            json={
                "paid": 50,
                "items": [
                    {
                        "product_id": sample_product.id,
                        "quantity": 1,
                        "unit_price": 50,
                    }
                ],
            },
        )
        response = client.get("/api/sales")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) >= 1

    def test_get_sale_by_id(self, client, sample_product):
        """Retrieve a specific sale."""
        create_resp = client.post(
            "/api/sales",
            json={
                "paid": 100,
                "items": [
                    {
                        "product_id": sample_product.id,
                        "quantity": 1,
                        "unit_price": 100,
                    }
                ],
            },
        )
        sale_id = create_resp.json()["id"]
        response = client.get(f"/api/sales/{sale_id}")
        assert response.status_code == 200
        assert response.json()["id"] == sale_id

    def test_get_sale_not_found(self, client):
        response = client.get("/api/sales/99999")
        assert response.status_code == 404

    def test_delete_sale_requires_manager(self, client, sample_product, cashier_headers, cashier_user):
        """Cashiers should not be able to delete sales."""
        create_resp = client.post(
            "/api/sales",
            json={
                "paid": 100,
                "items": [
                    {
                        "product_id": sample_product.id,
                        "quantity": 1,
                        "unit_price": 100,
                    }
                ],
            },
        )
        sale_id = create_resp.json()["id"]
        response = client.delete(
            f"/api/sales/{sale_id}", headers=cashier_headers
        )
        assert response.status_code == 403

    def test_delete_sale_manager(self, client, sample_product, admin_headers, admin_user):
        """Admin/manager should be able to delete sales."""
        create_resp = client.post(
            "/api/sales",
            json={
                "paid": 100,
                "items": [
                    {
                        "product_id": sample_product.id,
                        "quantity": 1,
                        "unit_price": 100,
                    }
                ],
            },
        )
        sale_id = create_resp.json()["id"]
        response = client.delete(
            f"/api/sales/{sale_id}", headers=admin_headers
        )
        assert response.status_code == 200

    def test_sale_with_customer(self, client, sample_product, sample_customer):
        """Sale linked to a customer."""
        response = client.post(
            "/api/sales",
            json={
                "customer_id": sample_customer.id,
                "paid": 50,
                "discount": 10,
                "items": [
                    {
                        "product_id": sample_product.id,
                        "quantity": 2,
                        "unit_price": 100,
                    }
                ],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["customer_id"] == sample_customer.id
        assert float(data["discount"]) == 10.0


class TestPurchasesFlow:
    """End-to-end purchase workflow tests."""

    def test_create_purchase(self, client, sample_product):
        """Create a purchase and verify response."""
        response = client.post(
            "/api/purchases",
            json={
                "supplier_name": "Test Supplier",
                "paid": 500,
                "items": [
                    {
                        "product_id": sample_product.id,
                        "quantity": 10,
                        "unit_price": 50,
                    }
                ],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["invoice_no"] is not None
        assert float(data["total"]) == 500.0

    def test_create_purchase_increases_inventory(self, client, db, sample_product):
        """Purchasing a product should increase its stock quantity."""
        original_qty = sample_product.quantity
        qty_to_buy = 20

        response = client.post(
            "/api/purchases",
            json={
                "paid": 1000,
                "items": [
                    {
                        "product_id": sample_product.id,
                        "quantity": qty_to_buy,
                        "unit_price": 50,
                    }
                ],
            },
        )
        assert response.status_code == 200

        db.refresh(sample_product)
        assert sample_product.quantity == original_qty + qty_to_buy

    def test_list_purchases(self, client, sample_product):
        """Create a purchase then list purchases."""
        client.post(
            "/api/purchases",
            json={
                "paid": 100,
                "items": [
                    {
                        "product_id": sample_product.id,
                        "quantity": 2,
                        "unit_price": 50,
                    }
                ],
            },
        )
        response = client.get("/api/purchases")
        assert response.status_code == 200
        assert len(response.json()) >= 1

    def test_get_purchase_by_id(self, client, sample_product):
        """Retrieve a specific purchase."""
        create_resp = client.post(
            "/api/purchases",
            json={
                "paid": 250,
                "items": [
                    {
                        "product_id": sample_product.id,
                        "quantity": 5,
                        "unit_price": 50,
                    }
                ],
            },
        )
        purchase_id = create_resp.json()["id"]
        response = client.get(f"/api/purchases/{purchase_id}")
        assert response.status_code == 200
        assert response.json()["id"] == purchase_id

    def test_get_purchase_not_found(self, client):
        response = client.get("/api/purchases/99999")
        assert response.status_code == 404

    def test_delete_purchase_requires_manager(
        self, client, sample_product, cashier_headers, cashier_user
    ):
        """Cashiers should not be able to delete purchases."""
        create_resp = client.post(
            "/api/purchases",
            json={
                "paid": 100,
                "items": [
                    {
                        "product_id": sample_product.id,
                        "quantity": 2,
                        "unit_price": 50,
                    }
                ],
            },
        )
        purchase_id = create_resp.json()["id"]
        response = client.delete(
            f"/api/purchases/{purchase_id}", headers=cashier_headers
        )
        assert response.status_code == 403

    def test_delete_purchase_admin(
        self, client, sample_product, admin_headers, admin_user
    ):
        """Admin should be able to delete purchases."""
        create_resp = client.post(
            "/api/purchases",
            json={
                "paid": 100,
                "items": [
                    {
                        "product_id": sample_product.id,
                        "quantity": 2,
                        "unit_price": 50,
                    }
                ],
            },
        )
        purchase_id = create_resp.json()["id"]
        response = client.delete(
            f"/api/purchases/{purchase_id}", headers=admin_headers
        )
        assert response.status_code == 200


class TestRootAndHealth:
    """Smoke tests for root and health-check endpoints."""

    def test_root(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert "Sales Management System" in response.json()["message"]

    def test_health(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
