# Sales Management System | نظام إدارة المبيعات

A full-stack sales management system with React frontend and FastAPI backend.

## Features

- **Dashboard**: Real-time statistics, low stock alerts, recent sales
- **Products**: Full CRUD with category and supplier management
- **Customers**: Customer management with balance tracking
- **Suppliers**: Supplier management
- **Sales**: Multi-item invoices with automatic inventory updates
- **Purchases**: Purchase tracking with inventory integration
- **Inventory**: Stock adjustments with movement history
- **Settings**: Store configuration

## Tech Stack

- **Frontend**: React + Vite
- **Backend**: FastAPI + SQLAlchemy
- **Database**: PostgreSQL
- **Containerization**: Docker & Docker Compose

## Prerequisites

- Node.js 18+
- Python 3.10+
- Docker & Docker Compose

## Quick Start

### 1. Start Database
```bash
docker-compose up -d
```

### 2. Start Backend
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

### 3. Start Frontend
```bash
cd frontend
npm install
npm run dev
```

### 4. Access Application
- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs
- **pgAdmin**: http://localhost:5050 (admin@admin.com / admin123)

## Project Structure

```
├── backend/
│   ├── main.py          # FastAPI application
│   ├── models.py        # SQLAlchemy models
│   ├── schemas.py       # Pydantic schemas
│   ├── crud.py          # Database operations
│   └── database.py      # DB connection
├── frontend/
│   ├── src/
│   │   ├── components/  # React components
│   │   └── services/    # API service layer
│   └── index.html
├── database/
│   ├── schema.sql       # DB schema
│   └── seed_data.sql    # Sample data
└── docker-compose.yml
```

## API Endpoints

| Resource | Endpoints |
|----------|-----------|
| Categories | GET, POST, PUT, DELETE /api/categories |
| Products | GET, POST, PUT, DELETE /api/products |
| Customers | GET, POST, PUT, DELETE /api/customers |
| Suppliers | GET, POST, PUT, DELETE /api/suppliers |
| Sales | GET, POST, DELETE /api/sales |
| Purchases | GET, POST, DELETE /api/purchases |
| Inventory | GET /api/inventory/movements, POST /api/inventory/adjust |
| Dashboard | GET /api/dashboard/stats, /api/dashboard/low-stock |

## License

MIT
