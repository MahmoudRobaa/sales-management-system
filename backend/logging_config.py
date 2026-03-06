"""
Structured logging configuration for the Sales Management System.

- Development: human-readable coloured logs
- Production: JSON-formatted logs for log aggregation (ELK, CloudWatch, etc.)
"""
import logging
import json
import os
import sys
from datetime import datetime, timezone


ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


class JSONFormatter(logging.Formatter):
    """Format log records as single-line JSON for production log aggregation."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if record.exc_info and record.exc_info[1]:
            log_entry["exception"] = self.formatException(record.exc_info)
        # Allow extra structured fields
        for key in ("request_id", "method", "path", "status_code", "duration_ms", "user"):
            if hasattr(record, key):
                log_entry[key] = getattr(record, key)
        return json.dumps(log_entry, ensure_ascii=False)


class DevFormatter(logging.Formatter):
    """Readable coloured formatter for development."""

    COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[41m",  # Red BG
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)
        ts = datetime.now().strftime("%H:%M:%S")
        msg = record.getMessage()
        base = f"{color}{ts} [{record.levelname:>7}]{self.RESET} {record.name}: {msg}"
        if record.exc_info and record.exc_info[1]:
            base += "\n" + self.formatException(record.exc_info)
        return base


def setup_logging() -> None:
    """Configure root and application loggers."""
    root = logging.getLogger()
    root.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

    # Remove existing handlers
    root.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    if ENVIRONMENT == "production":
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(DevFormatter())
    root.addHandler(handler)

    # Quiet noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if ENVIRONMENT == "development" else logging.WARNING
    )

    logging.getLogger("sales").info(
        "Logging configured — env=%s level=%s", ENVIRONMENT, LOG_LEVEL
    )
