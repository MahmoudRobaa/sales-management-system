#!/bin/bash
# ============================================
# Database Backup Script
# Usage: ./scripts/backup.sh [backup_dir]
# ============================================

set -euo pipefail

# Configuration
CONTAINER_NAME="sales_db_dev"
DB_NAME="sales_management"
DB_USER="salesadmin"
BACKUP_DIR="${1:-./backups}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/backup_${TIMESTAMP}.sql.gz"
MAX_BACKUPS=30  # Keep last 30 backups

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}=== Sales Management System - Database Backup ===${NC}"
echo "Timestamp: ${TIMESTAMP}"

# Create backup directory
mkdir -p "${BACKUP_DIR}"

# Check if container is running
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${RED}ERROR: Container '${CONTAINER_NAME}' is not running.${NC}"
    echo "Start the containers with: docker compose up -d"
    exit 1
fi

# Perform backup
echo -e "${YELLOW}Creating backup...${NC}"
docker exec "${CONTAINER_NAME}" pg_dump \
    -U "${DB_USER}" \
    -d "${DB_NAME}" \
    --no-owner \
    --no-privileges \
    --format=plain \
    | gzip > "${BACKUP_FILE}"

# Verify backup
if [ -f "${BACKUP_FILE}" ] && [ -s "${BACKUP_FILE}" ]; then
    SIZE=$(du -h "${BACKUP_FILE}" | cut -f1)
    echo -e "${GREEN}Backup created successfully!${NC}"
    echo "  File: ${BACKUP_FILE}"
    echo "  Size: ${SIZE}"
else
    echo -e "${RED}ERROR: Backup file is empty or missing.${NC}"
    exit 1
fi

# Rotate old backups (keep last N)
BACKUP_COUNT=$(find "${BACKUP_DIR}" -name "backup_*.sql.gz" -type f | wc -l)
if [ "${BACKUP_COUNT}" -gt "${MAX_BACKUPS}" ]; then
    echo -e "${YELLOW}Rotating old backups (keeping last ${MAX_BACKUPS})...${NC}"
    find "${BACKUP_DIR}" -name "backup_*.sql.gz" -type f \
        | sort \
        | head -n -"${MAX_BACKUPS}" \
        | xargs rm -f
    DELETED=$((BACKUP_COUNT - MAX_BACKUPS))
    echo "  Deleted ${DELETED} old backup(s)"
fi

echo -e "${GREEN}=== Backup Complete ===${NC}"
