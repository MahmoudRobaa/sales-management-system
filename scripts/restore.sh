#!/bin/bash
# ============================================
# Database Restore Script
# Usage: ./scripts/restore.sh <backup_file>
# ============================================

set -euo pipefail

# Configuration
CONTAINER_NAME="sales_db_dev"
DB_NAME="sales_management"
DB_USER="salesadmin"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}=== Sales Management System - Database Restore ===${NC}"

# Check arguments
if [ $# -lt 1 ]; then
    echo -e "${RED}Usage: $0 <backup_file>${NC}"
    echo ""
    echo "Available backups:"
    if [ -d "./backups" ]; then
        ls -lh ./backups/backup_*.sql.gz 2>/dev/null || echo "  No backups found"
    else
        echo "  No backups directory found"
    fi
    exit 1
fi

BACKUP_FILE="$1"

# Validate backup file
if [ ! -f "${BACKUP_FILE}" ]; then
    echo -e "${RED}ERROR: Backup file '${BACKUP_FILE}' not found.${NC}"
    exit 1
fi

# Check if container is running
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${RED}ERROR: Container '${CONTAINER_NAME}' is not running.${NC}"
    echo "Start the containers with: docker compose up -d"
    exit 1
fi

# Confirmation prompt
echo -e "${YELLOW}WARNING: This will REPLACE the current database with the backup.${NC}"
echo "  Backup file: ${BACKUP_FILE}"
echo "  Database: ${DB_NAME}"
echo ""
read -p "Are you sure you want to continue? (yes/no): " CONFIRM

if [ "${CONFIRM}" != "yes" ]; then
    echo "Restore cancelled."
    exit 0
fi

# Create a safety backup before restore
echo -e "${YELLOW}Creating safety backup before restore...${NC}"
SAFETY_DIR="./backups"
mkdir -p "${SAFETY_DIR}"
SAFETY_FILE="${SAFETY_DIR}/pre_restore_$(date +%Y%m%d_%H%M%S).sql.gz"
docker exec "${CONTAINER_NAME}" pg_dump \
    -U "${DB_USER}" \
    -d "${DB_NAME}" \
    --no-owner \
    --no-privileges \
    --format=plain \
    | gzip > "${SAFETY_FILE}"
echo "  Safety backup: ${SAFETY_FILE}"

# Drop and recreate database
echo -e "${YELLOW}Dropping and recreating database...${NC}"
docker exec "${CONTAINER_NAME}" psql -U "${DB_USER}" -d postgres -c "
    SELECT pg_terminate_backend(pid) FROM pg_stat_activity
    WHERE datname = '${DB_NAME}' AND pid <> pg_backend_pid();
"
docker exec "${CONTAINER_NAME}" psql -U "${DB_USER}" -d postgres -c "DROP DATABASE IF EXISTS ${DB_NAME};"
docker exec "${CONTAINER_NAME}" psql -U "${DB_USER}" -d postgres -c "CREATE DATABASE ${DB_NAME} OWNER ${DB_USER};"

# Restore from backup
echo -e "${YELLOW}Restoring from backup...${NC}"
if [[ "${BACKUP_FILE}" == *.gz ]]; then
    gunzip -c "${BACKUP_FILE}" | docker exec -i "${CONTAINER_NAME}" psql -U "${DB_USER}" -d "${DB_NAME}" --quiet
else
    docker exec -i "${CONTAINER_NAME}" psql -U "${DB_USER}" -d "${DB_NAME}" --quiet < "${BACKUP_FILE}"
fi

# Stamp Alembic to current head
echo -e "${YELLOW}Updating Alembic migration state...${NC}"
cd "$(dirname "$0")/../backend"
if command -v python3 &> /dev/null; then
    python3 -m alembic stamp head 2>/dev/null || echo "  Alembic stamp skipped (not in Python env)"
elif command -v python &> /dev/null; then
    python -m alembic stamp head 2>/dev/null || echo "  Alembic stamp skipped (not in Python env)"
fi

echo -e "${GREEN}=== Restore Complete ===${NC}"
echo "Database has been restored from: ${BACKUP_FILE}"
echo "Please restart the backend: docker compose restart backend"
