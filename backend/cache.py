"""
Redis cache layer for the Sales Management System.

Provides a thin wrapper around Redis with JSON serialization,
TTL management, and graceful fallback when Redis is unavailable.
"""
import json
import os
import logging
from typing import Optional, Any
from decimal import Decimal
from datetime import date, datetime

logger = logging.getLogger("sales.cache")

REDIS_URL = os.getenv("REDIS_URL", "")

# Default TTLs (seconds)
TTL_DASHBOARD = 300      # 5 minutes
TTL_ANALYTICS = 600      # 10 minutes
TTL_SHORT = 60           # 1 minute


class _DecimalDateEncoder(json.JSONEncoder):
    """JSON encoder that handles Decimal, date, and datetime objects."""

    def default(self, o: Any) -> Any:
        if isinstance(o, Decimal):
            return float(o)
        if isinstance(o, (date, datetime)):
            return o.isoformat()
        return super().default(o)


def _get_redis():
    """Lazy-initialise the Redis connection (singleton)."""
    if not REDIS_URL:
        return None
    try:
        import redis
        return redis.Redis.from_url(REDIS_URL, decode_responses=True, socket_timeout=2)
    except Exception as e:
        logger.warning("Redis connection failed: %s", e)
        return None


_redis_client = None


def _client():
    global _redis_client
    if _redis_client is None:
        _redis_client = _get_redis()
    return _redis_client


# ============================================
# PUBLIC API
# ============================================

def get(key: str) -> Optional[Any]:
    """Get a value from cache. Returns None on miss or error."""
    r = _client()
    if r is None:
        return None
    try:
        raw = r.get(key)
        if raw is None:
            return None
        return json.loads(raw)
    except Exception as e:
        logger.warning("Cache GET error for key '%s': %s", key, e)
        return None


def set(key: str, value: Any, ttl: int = TTL_SHORT) -> bool:
    """Set a value in cache with TTL. Returns False on error."""
    r = _client()
    if r is None:
        return False
    try:
        raw = json.dumps(value, cls=_DecimalDateEncoder)
        r.setex(key, ttl, raw)
        return True
    except Exception as e:
        logger.warning("Cache SET error for key '%s': %s", key, e)
        return False


def delete(key: str) -> bool:
    """Delete a key from cache."""
    r = _client()
    if r is None:
        return False
    try:
        r.delete(key)
        return True
    except Exception as e:
        logger.warning("Cache DELETE error for key '%s': %s", key, e)
        return False


def invalidate_pattern(pattern: str) -> int:
    """Delete all keys matching a glob pattern (e.g. 'dashboard:*')."""
    r = _client()
    if r is None:
        return 0
    try:
        keys = r.keys(pattern)
        if keys:
            return r.delete(*keys)
        return 0
    except Exception as e:
        logger.warning("Cache INVALIDATE error for pattern '%s': %s", pattern, e)
        return 0


# ============================================
# CACHE KEY CONSTANTS
# ============================================
KEY_DASHBOARD_STATS = "dashboard:stats"
KEY_LOW_STOCK = "dashboard:low_stock"
KEY_INVENTORY_VALUE = "analytics:inventory_value"
KEY_BUSINESS_KPIS = "analytics:kpis"


def key_financial_report(period: str) -> str:
    return f"analytics:financial:{period}"


def key_sales_trend(period: str, days: int) -> str:
    return f"analytics:trend:{period}:{days}"


def key_top_products(limit: int) -> str:
    return f"analytics:top_products:{limit}"


def key_top_customers(limit: int) -> str:
    return f"analytics:top_customers:{limit}"


def key_profit_report(from_date: str, to_date: str) -> str:
    return f"analytics:profit:{from_date}:{to_date}"
