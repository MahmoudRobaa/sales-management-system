"""
Pytest configuration and shared fixtures.

Sets up an in-memory SQLite database so tests run fast and without
needing a real PostgreSQL server.
"""
import os

# ── Set required env vars BEFORE any application imports ──
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-at-least-32-characters-long!!")
os.environ.setdefault("ENVIRONMENT", "testing")

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from database import Base, get_db
from auth import get_password_hash

# ── SQLite in-memory engine for tests ──
SQLALCHEMY_TEST_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_TEST_URL,
    connect_args={"check_same_thread": False},
)

# SQLite doesn't enforce FK constraints by default
@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ============================================
# FIXTURES
# ============================================

@pytest.fixture(scope="session", autouse=True)
def create_tables():
    """Create all tables once per test session."""
    import models  # noqa: F401 – registers all models with Base
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    # Clean up test.db file (ignore if still locked on Windows)
    try:
        if os.path.exists("test.db"):
            os.remove("test.db")
    except PermissionError:
        pass


@pytest.fixture()
def db():
    """Provide a transactional database session that rolls back after each test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    # Seed initial cash balance so purchase cash-check passes
    import models
    cash = models.CashTransaction(
        transaction_type="DEPOSIT",
        amount=0,
        balance_before=0,
        balance_after=100000,
        description="رصيد افتتاحي للاختبار",
    )
    session.add(cash)
    session.flush()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db):
    """FastAPI TestClient with the DB dependency overridden and rate limiter disabled."""
    from main import app
    from routers.auth_router import limiter as auth_limiter

    def _override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db

    # Disable rate-limiting during tests so login fixtures don't get throttled
    main_limiter = app.state.limiter
    main_limiter.enabled = False
    auth_limiter.enabled = False

    with TestClient(app) as c:
        yield c

    main_limiter.enabled = True
    auth_limiter.enabled = True
    app.dependency_overrides.clear()


@pytest.fixture()
def admin_user(db):
    """Create an admin user and return the ORM object."""
    import models
    user = models.User(
        username="admin_test",
        password_hash=get_password_hash("Admin123"),
        full_name="Test Admin",
        role="admin",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture()
def manager_user(db):
    """Create a manager user and return the ORM object."""
    import models
    user = models.User(
        username="manager_test",
        password_hash=get_password_hash("Manager123"),
        full_name="Test Manager",
        role="manager",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture()
def cashier_user(db):
    """Create a cashier user and return the ORM object."""
    import models
    user = models.User(
        username="cashier_test",
        password_hash=get_password_hash("Cashier123"),
        full_name="Test Cashier",
        role="cashier",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture()
def admin_token(client, admin_user):
    """Get a valid JWT token for the admin user."""
    response = client.post(
        "/api/auth/login",
        data={"username": "admin_test", "password": "Admin123"},
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json()["access_token"]


@pytest.fixture()
def admin_headers(admin_token):
    """Authorization headers for admin user."""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture()
def manager_token(client, manager_user):
    """Get a valid JWT token for the manager user."""
    response = client.post(
        "/api/auth/login",
        data={"username": "manager_test", "password": "Manager123"},
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json()["access_token"]


@pytest.fixture()
def manager_headers(manager_token):
    """Authorization headers for manager user."""
    return {"Authorization": f"Bearer {manager_token}"}


@pytest.fixture()
def cashier_token(client, cashier_user):
    """Get a valid JWT token for the cashier user."""
    response = client.post(
        "/api/auth/login",
        data={"username": "cashier_test", "password": "Cashier123"},
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json()["access_token"]


@pytest.fixture()
def cashier_headers(cashier_token):
    """Authorization headers for cashier user."""
    return {"Authorization": f"Bearer {cashier_token}"}


@pytest.fixture()
def sample_supplier(db):
    """Create a sample supplier."""
    import models
    supplier = models.Supplier(
        code="SUP-TEST-001",
        name="Test Supplier",
        phone="01234567890",
    )
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier


@pytest.fixture()
def sample_customer(db):
    """Create a sample customer."""
    import models
    customer = models.Customer(
        code="CUS-TEST-001",
        name="Test Customer",
        phone="09876543210",
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


@pytest.fixture()
def sample_category(db):
    """Create a sample category."""
    import models
    category = models.Category(
        code="CAT-TEST-001",
        name="Test Category",
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@pytest.fixture()
def sample_product(db, sample_supplier, sample_category):
    """Create a sample product with supplier and category."""
    import models
    product = models.Product(
        code="PRD-TEST-001",
        name="Test Product",
        category_id=sample_category.id,
        supplier_id=sample_supplier.id,
        purchase_price=50.00,
        sale_price=100.00,
        quantity=100,
        min_quantity=5,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product
