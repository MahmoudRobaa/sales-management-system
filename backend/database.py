"""
Database connection and session management
"""
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import logging
import time
from dotenv import load_dotenv

load_dotenv()

# Configure SQL query logger
sql_logger = logging.getLogger("sqlalchemy.engine")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# In development, log slow queries; in production, only warnings
if ENVIRONMENT == "development":
    sql_logger.setLevel(logging.INFO)
else:
    sql_logger.setLevel(logging.WARNING)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL environment variable is required. "
        "Example: postgresql://user:password@host:5432/dbname"
    )

# Detect test/SQLite mode
is_sqlite = DATABASE_URL.startswith("sqlite")

engine_kwargs = {
    "pool_pre_ping": True,  # Verify connections before use
}

if not is_sqlite:
    engine_kwargs.update({
        "pool_size": 10,           # Persistent connections
        "max_overflow": 20,        # Extra connections under load
        "pool_timeout": 30,        # Wait time for a connection
        "pool_recycle": 1800,      # Recycle connections every 30 min
        "echo": ENVIRONMENT == "development",  # SQL logging in dev
    })

engine = create_engine(DATABASE_URL, **engine_kwargs)


# ============================================
# SLOW QUERY LOGGING
# ============================================
slow_query_logger = logging.getLogger("sales.slow_queries")
SLOW_QUERY_THRESHOLD = float(os.getenv("SLOW_QUERY_THRESHOLD", "0.5"))  # seconds


@event.listens_for(engine, "before_cursor_execute")
def _before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault("query_start_time", []).append(time.perf_counter())


@event.listens_for(engine, "after_cursor_execute")
def _after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.perf_counter() - conn.info["query_start_time"].pop(-1)
    if total >= SLOW_QUERY_THRESHOLD:
        slow_query_logger.warning(
            "Slow query (%.3fs): %s", total, statement[:500]
        )


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
