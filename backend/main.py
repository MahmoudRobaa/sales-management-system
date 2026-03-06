"""
Sales Management System - FastAPI Backend
نظام إدارة المبيعات - الواجهة الخلفية
"""
import time
import logging

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os

from logging_config import setup_logging

# Initialise structured logging before anything else
setup_logging()
logger = logging.getLogger("sales.api")

from database import engine
import models

# Import routers
from routers.auth_router import router as auth_router
from routers.users import router as users_router
from routers.suppliers import router as suppliers_router
from routers.customers import router as customers_router
from routers.products import router as products_router
from routers.sales import router as sales_router
from routers.purchases import router as purchases_router
from routers.inventory import router as inventory_router
from routers.settings import router as settings_router
from routers.analytics import router as analytics_router
from routers.cash import router as cash_router
# Sprint 5 routers
from routers.returns import router as returns_router
from routers.shifts import router as shifts_router
from routers.variants import router as variants_router
from routers.installments import router as installments_router
from routers.batches import router as batches_router
from routers.stocktake import router as stocktake_router
from routers.einvoice import router as einvoice_router
from routers.reports import router as reports_router
from routers.invoicing import router as invoicing_router
from routers.backup import router as backup_router

# Create database tables (if not exists)
models.Base.metadata.create_all(bind=engine)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Sales Management System API",
    description="نظام إدارة المبيعات - API",
    version="2.0.0",
)

# Attach rate limiter to app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# CORS middleware for frontend access
if ENVIRONMENT == "production":
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",")
    ALLOWED_ORIGINS = [o.strip() for o in ALLOWED_ORIGINS if o.strip()]
    if not ALLOWED_ORIGINS:
        raise RuntimeError("ALLOWED_ORIGINS must be set in production")
else:
    ALLOWED_ORIGINS = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:5173,http://localhost:5174,http://127.0.0.1:5173,http://127.0.0.1:5174",
    ).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in ALLOWED_ORIGINS],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


# ============================================
# SECURITY HEADERS MIDDLEWARE
# ============================================
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to every response."""
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if ENVIRONMENT == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


# ============================================
# REQUEST METRICS MIDDLEWARE
# ============================================
request_logger = logging.getLogger("sales.requests")


@app.middleware("http")
async def log_request_metrics(request: Request, call_next):
    """Log request method, path, status code, and duration."""
    start = time.perf_counter()
    response: Response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000

    request_logger.info(
        "%s %s → %s (%.1fms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration_ms, 2),
        },
    )
    # Expose timing header for clients / monitoring
    response.headers["X-Response-Time"] = f"{duration_ms:.1f}ms"
    return response


# ============================================
# REGISTER ROUTERS
# ============================================
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(suppliers_router)
app.include_router(customers_router)
app.include_router(products_router)
app.include_router(sales_router)
app.include_router(purchases_router)
app.include_router(inventory_router)
app.include_router(settings_router)
app.include_router(analytics_router)
app.include_router(cash_router)
# Sprint 5 routers
app.include_router(returns_router)
app.include_router(shifts_router)
app.include_router(variants_router)
app.include_router(installments_router)
app.include_router(batches_router)
app.include_router(stocktake_router)
app.include_router(einvoice_router)
app.include_router(reports_router)
app.include_router(invoicing_router)
app.include_router(backup_router)


# ============================================
# ROOT & HEALTH CHECK
# ============================================
@app.get("/")
@limiter.limit("100/minute")
def read_root(request: Request):
    return {"message": "Sales Management System API", "version": "2.0.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


