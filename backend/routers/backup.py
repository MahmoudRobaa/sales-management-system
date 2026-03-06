"""
Backup / Restore UI endpoints (5.27)
Provides database backup download and restore upload via the admin UI.
"""
import os
import subprocess
import tempfile
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse

from auth import require_admin, TokenData

router = APIRouter(prefix="/api/backup", tags=["Backup & Restore"])


def _get_db_url_parts() -> dict:
    """Parse DATABASE_URL env var."""
    url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5433/sales_db")
    # postgresql://user:pass@host:port/dbname
    from urllib.parse import urlparse
    parsed = urlparse(url)
    return {
        "host": parsed.hostname or "localhost",
        "port": str(parsed.port or 5433),
        "user": parsed.username or "postgres",
        "password": parsed.password or "postgres",
        "dbname": parsed.path.lstrip("/") or "sales_db",
    }


@router.get("/download")
def download_backup(current_user: TokenData = Depends(require_admin)):
    """Download a pg_dump SQL backup of the database (admin only)."""
    parts = _get_db_url_parts()
    env = os.environ.copy()
    env["PGPASSWORD"] = parts["password"]

    try:
        result = subprocess.run(
            [
                "pg_dump",
                "-h", parts["host"],
                "-p", parts["port"],
                "-U", parts["user"],
                "-d", parts["dbname"],
                "--no-owner",
                "--no-acl",
                "-F", "c",  # custom format for compression
            ],
            capture_output=True,
            env=env,
            timeout=120,
        )
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="pg_dump not found on server")
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="Backup timed out")

    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=f"pg_dump failed: {result.stderr.decode()}")

    filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.dump"
    import io
    buf = io.BytesIO(result.stdout)
    return StreamingResponse(
        buf,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.post("/restore")
def restore_backup(
    file: UploadFile = File(...),
    current_user: TokenData = Depends(require_admin),
):
    """Restore database from an uploaded pg_dump file (admin only). USE WITH CAUTION."""
    parts = _get_db_url_parts()
    env = os.environ.copy()
    env["PGPASSWORD"] = parts["password"]

    # Save uploaded file to temp
    with tempfile.NamedTemporaryFile(delete=False, suffix=".dump") as tmp:
        tmp.write(file.file.read())
        tmp_path = tmp.name

    try:
        result = subprocess.run(
            [
                "pg_restore",
                "-h", parts["host"],
                "-p", parts["port"],
                "-U", parts["user"],
                "-d", parts["dbname"],
                "--clean",
                "--if-exists",
                "--no-owner",
                "--no-acl",
                tmp_path,
            ],
            capture_output=True,
            env=env,
            timeout=300,
        )
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="pg_restore not found on server")
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="Restore timed out")
    finally:
        os.unlink(tmp_path)

    if result.returncode != 0:
        stderr = result.stderr.decode()
        # pg_restore often returns non-zero for warnings, check if it's critical
        if "FATAL" in stderr or "could not connect" in stderr:
            raise HTTPException(status_code=500, detail=f"Restore failed: {stderr}")

    return {"message": "Database restored successfully", "warnings": result.stderr.decode()[:500] if result.stderr else None}


@router.get("/info")
def backup_info(current_user: TokenData = Depends(require_admin)):
    """Get current database connection info (admin only)."""
    parts = _get_db_url_parts()
    return {
        "host": parts["host"],
        "port": parts["port"],
        "database": parts["dbname"],
        "user": parts["user"],
    }
