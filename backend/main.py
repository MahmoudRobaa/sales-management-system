"""
Sales Management System - FastAPI Backend
نظام إدارة المبيعات - الواجهة الخلفية
"""
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os

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


