"""
Tests for authentication and user management endpoints.
"""
import pytest


class TestLogin:
    """Tests for POST /api/auth/login"""

    def test_login_success(self, client, admin_user):
        response = client.post(
            "/api/auth/login",
            data={"username": "admin_test", "password": "Admin123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["username"] == "admin_test"
        assert data["user"]["role"] == "admin"

    def test_login_wrong_password(self, client, admin_user):
        response = client.post(
            "/api/auth/login",
            data={"username": "admin_test", "password": "WrongPass1"},
        )
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        response = client.post(
            "/api/auth/login",
            data={"username": "nobody", "password": "Whatever1"},
        )
        assert response.status_code == 401

    def test_login_inactive_user(self, client, db):
        import models
        from auth import get_password_hash

        user = models.User(
            username="inactive_user",
            password_hash=get_password_hash("Inactive1"),
            full_name="Inactive User",
            role="cashier",
            is_active=False,
        )
        db.add(user)
        db.commit()

        response = client.post(
            "/api/auth/login",
            data={"username": "inactive_user", "password": "Inactive1"},
        )
        assert response.status_code == 401


class TestMe:
    """Tests for GET /api/auth/me"""

    def test_get_me_authenticated(self, client, admin_headers, admin_user):
        response = client.get("/api/auth/me", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "admin_test"
        assert data["role"] == "admin"

    def test_get_me_no_token(self, client):
        response = client.get("/api/auth/me")
        assert response.status_code == 401


class TestLogout:
    """Tests for POST /api/auth/logout"""

    def test_logout_success(self, client, admin_headers, admin_user):
        response = client.post("/api/auth/logout", headers=admin_headers)
        assert response.status_code == 200

    def test_logout_no_token(self, client):
        response = client.post("/api/auth/logout")
        assert response.status_code == 401


class TestUserManagement:
    """Tests for /api/users endpoints (admin only)."""

    def test_list_users_admin(self, client, admin_headers, admin_user):
        response = client.get("/api/users", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_list_users_cashier_forbidden(self, client, cashier_headers, cashier_user):
        response = client.get("/api/users", headers=cashier_headers)
        assert response.status_code == 403

    def test_create_user_admin(self, client, admin_headers, admin_user):
        response = client.post(
            "/api/users",
            json={
                "username": "newuser",
                "password": "NewPass123",
                "full_name": "New User",
                "role": "cashier",
            },
            headers=admin_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "newuser"
        assert data["role"] == "cashier"

    def test_create_user_duplicate_username(self, client, admin_headers, admin_user):
        # Create first user
        client.post(
            "/api/users",
            json={
                "username": "duplicate",
                "password": "Pass1234",
                "full_name": "First",
                "role": "cashier",
            },
            headers=admin_headers,
        )
        # Try duplicate
        response = client.post(
            "/api/users",
            json={
                "username": "duplicate",
                "password": "Pass1234",
                "full_name": "Second",
                "role": "cashier",
            },
            headers=admin_headers,
        )
        assert response.status_code == 400

    def test_create_user_weak_password(self, client, admin_headers, admin_user):
        response = client.post(
            "/api/users",
            json={
                "username": "weakuser",
                "password": "short",
                "full_name": "Weak",
                "role": "cashier",
            },
            headers=admin_headers,
        )
        assert response.status_code == 400

    def test_update_user(self, client, admin_headers, admin_user, cashier_user):
        response = client.put(
            f"/api/users/{cashier_user.id}",
            json={"full_name": "Updated Cashier"},
            headers=admin_headers,
        )
        assert response.status_code == 200
        assert response.json()["full_name"] == "Updated Cashier"

    def test_update_user_password(self, client, admin_headers, admin_user, cashier_user):
        response = client.put(
            f"/api/users/{cashier_user.id}",
            json={"password": "UpdatedPass1"},
            headers=admin_headers,
        )
        assert response.status_code == 200

    def test_update_user_weak_password_rejected(
        self, client, admin_headers, admin_user, cashier_user
    ):
        response = client.put(
            f"/api/users/{cashier_user.id}",
            json={"password": "weak"},
            headers=admin_headers,
        )
        assert response.status_code == 400

    def test_delete_user(self, client, admin_headers, admin_user, db):
        import models
        from auth import get_password_hash

        victim = models.User(
            username="to_delete",
            password_hash=get_password_hash("Delete123"),
            full_name="Delete Me",
            role="cashier",
            is_active=True,
        )
        db.add(victim)
        db.commit()
        db.refresh(victim)

        response = client.delete(
            f"/api/users/{victim.id}", headers=admin_headers
        )
        assert response.status_code == 200

    def test_delete_user_not_found(self, client, admin_headers, admin_user):
        response = client.delete("/api/users/99999", headers=admin_headers)
        assert response.status_code == 404

    def test_create_user_no_auth(self, client):
        response = client.post(
            "/api/users",
            json={
                "username": "noauth",
                "password": "NoAuth123",
                "full_name": "No Auth",
                "role": "cashier",
            },
        )
        assert response.status_code == 401
