"""
Tests for CRUD operations: suppliers, customers, products.
"""
import pytest


# ============================================
# SUPPLIER TESTS
# ============================================
class TestSuppliers:
    """Tests for /api/suppliers endpoints."""

    def test_list_suppliers_empty(self, client):
        response = client.get("/api/suppliers")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_create_supplier(self, client):
        response = client.post(
            "/api/suppliers",
            json={
                "code": "SUP-001",
                "name": "Acme Supplies",
                "phone": "0123456789",
                "email": "info@acme.com",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "SUP-001"
        assert data["name"] == "Acme Supplies"
        assert data["id"] is not None

    def test_create_supplier_duplicate_code(self, client, sample_supplier):
        response = client.post(
            "/api/suppliers",
            json={"code": sample_supplier.code, "name": "Duplicate"},
        )
        assert response.status_code == 400

    def test_get_supplier_by_id(self, client, sample_supplier):
        response = client.get(f"/api/suppliers/{sample_supplier.id}")
        assert response.status_code == 200
        assert response.json()["code"] == sample_supplier.code

    def test_get_supplier_not_found(self, client):
        response = client.get("/api/suppliers/99999")
        assert response.status_code == 404

    def test_update_supplier(self, client, sample_supplier):
        response = client.put(
            f"/api/suppliers/{sample_supplier.id}",
            json={"name": "Updated Supplier"},
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Supplier"

    def test_delete_supplier(self, client, sample_supplier):
        response = client.delete(f"/api/suppliers/{sample_supplier.id}")
        assert response.status_code == 200
        # Verify it is gone
        get_resp = client.get(f"/api/suppliers/{sample_supplier.id}")
        assert get_resp.status_code == 404

    def test_delete_supplier_not_found(self, client):
        response = client.delete("/api/suppliers/99999")
        assert response.status_code == 404

    def test_generate_supplier_code(self, client):
        response = client.get("/api/suppliers/generate-code")
        assert response.status_code == 200
        assert "code" in response.json()


# ============================================
# CUSTOMER TESTS
# ============================================
class TestCustomers:
    """Tests for /api/customers endpoints."""

    def test_list_customers_empty(self, client):
        response = client.get("/api/customers")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_create_customer(self, client):
        response = client.post(
            "/api/customers",
            json={
                "code": "CUS-001",
                "name": "John Doe",
                "phone": "9876543210",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "CUS-001"
        assert data["name"] == "John Doe"

    def test_create_customer_duplicate_code(self, client, sample_customer):
        response = client.post(
            "/api/customers",
            json={"code": sample_customer.code, "name": "Dup"},
        )
        assert response.status_code == 400

    def test_get_customer_by_id(self, client, sample_customer):
        response = client.get(f"/api/customers/{sample_customer.id}")
        assert response.status_code == 200
        assert response.json()["code"] == sample_customer.code

    def test_get_customer_not_found(self, client):
        response = client.get("/api/customers/99999")
        assert response.status_code == 404

    def test_update_customer(self, client, sample_customer):
        response = client.put(
            f"/api/customers/{sample_customer.id}",
            json={"name": "Updated Customer"},
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Customer"

    def test_delete_customer(self, client, sample_customer):
        response = client.delete(f"/api/customers/{sample_customer.id}")
        assert response.status_code == 200

    def test_generate_customer_code(self, client):
        response = client.get("/api/customers/generate-code")
        assert response.status_code == 200
        assert "code" in response.json()


# ============================================
# PRODUCT TESTS
# ============================================
class TestProducts:
    """Tests for /api/products endpoints."""

    def test_list_products_empty(self, client):
        response = client.get("/api/products")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_create_product(self, client, sample_supplier, sample_category):
        response = client.post(
            "/api/products",
            json={
                "code": "PRD-NEW-001",
                "name": "New Widget",
                "category_id": sample_category.id,
                "supplier_id": sample_supplier.id,
                "purchase_price": 25.00,
                "sale_price": 50.00,
                "quantity": 200,
                "min_quantity": 10,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "PRD-NEW-001"
        assert data["name"] == "New Widget"
        assert float(data["sale_price"]) == 50.00

    def test_create_product_duplicate_code(self, client, sample_product):
        response = client.post(
            "/api/products",
            json={
                "code": sample_product.code,
                "name": "Dup Product",
                "purchase_price": 10,
                "sale_price": 20,
                "quantity": 1,
            },
        )
        assert response.status_code == 400

    def test_get_product_by_id(self, client, sample_product):
        response = client.get(f"/api/products/{sample_product.id}")
        assert response.status_code == 200
        assert response.json()["code"] == sample_product.code

    def test_get_product_not_found(self, client):
        response = client.get("/api/products/99999")
        assert response.status_code == 404

    def test_update_product(self, client, sample_product):
        response = client.put(
            f"/api/products/{sample_product.id}",
            json={"name": "Updated Product", "sale_price": 150.00},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Product"

    def test_delete_product(self, client, sample_product):
        response = client.delete(f"/api/products/{sample_product.id}")
        assert response.status_code == 200

    def test_generate_product_code(self, client):
        response = client.get("/api/products/generate-code")
        assert response.status_code == 200
        assert "code" in response.json()

    def test_export_products_csv(self, client, sample_product):
        response = client.get("/api/products/export-csv")
        assert response.status_code == 200
        assert "text/csv" in response.headers.get("content-type", "")
