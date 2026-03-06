# System Architecture & Technical Specifications
# البنية التقنية والمواصفات الفنية

**Project:** Sales Management System  
**Version:** 2.0.0  
**Date:** March 2026  
**Status:** Reverse-Engineered from Codebase

---

## 1. High-Level Architecture | نظرة عامة

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    React 19 SPA (Vite 5)                            │   │
│  │  - Dashboard, Products, Sales, Purchases, Inventory, Reports       │   │
│  │  - Recharts for data visualization                                  │   │
│  │  - Axios for API communication                                      │   │
│  │  - JWT token storage in localStorage                               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │ HTTP/HTTPS (JSON)
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PROXY LAYER (Production)                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         Nginx Reverse Proxy                         │   │
│  │  - Static file serving for frontend                                │   │
│  │  - API proxying to backend (/api/*)                                │   │
│  │  - Port 80/8888 → Backend :8000                                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              API LAYER                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    FastAPI (Python 3.11+)                           │   │
│  │  - RESTful JSON API                                                 │   │
│  │  - JWT Authentication (python-jose)                                 │   │
│  │  - Password hashing (bcrypt)                                        │   │
│  │  - Pydantic schemas for validation                                  │   │
│  │  - SQLAlchemy ORM                                                   │   │
│  │  - Uvicorn ASGI server                                              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │ TCP/IP (SQLAlchemy)
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                             DATA LAYER                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    PostgreSQL 15 (Alpine)                           │   │
│  │  - 14 tables with relationships                                     │   │
│  │  - Indexed for performance                                          │   │
│  │  - Auto-updated timestamps via triggers                             │   │
│  │  - Volume-persisted data                                            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Technology Stack | المكدس التقني

### 2.1 Frontend Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| React | 19.2.0 | UI component framework |
| Vite | 5.4.21 | Build tool and dev server |
| Axios | 1.13.2 | HTTP client for API calls |
| Recharts | 3.6.0 | Data visualization charts |
| React Router DOM | 7.11.0 | Client-side routing (available but unused) |
| Font Awesome | CDN | Icons |
| Noto Sans Arabic | CDN | Arabic font |

### 2.2 Backend Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11+ | Runtime |
| FastAPI | 0.104.1 | Web framework |
| Uvicorn | 0.24.0 | ASGI server |
| SQLAlchemy | 2.0.23 | ORM |
| Pydantic | 2.5.2 | Data validation |
| python-jose | 3.5.0 | JWT tokens |
| bcrypt | via passlib 1.7.4 | Password hashing |
| psycopg2-binary | 2.9.9 | PostgreSQL driver |
| python-dotenv | 1.0.0 | Environment variables |
| slowapi | 0.1.9 | Rate limiting (available but unused) |

### 2.3 Database

| Technology | Version | Purpose |
|------------|---------|---------|
| PostgreSQL | 15-alpine | Primary database |
| UUID extension | Built-in | Optional UUID support |

### 2.4 DevOps

| Technology | Purpose |
|------------|---------|
| Docker | Containerization |
| Docker Compose | Container orchestration |
| Nginx | Reverse proxy & static serving |

---

## 3. Project Structure | هيكل المشروع

```
sales-management-system/
├── backend/
│   ├── main.py              # FastAPI app, all endpoints (~1080 lines)
│   ├── models.py            # SQLAlchemy ORM models (241 lines)
│   ├── schemas.py           # Pydantic request/response schemas (490 lines)
│   ├── crud.py              # Database operations (1263 lines)
│   ├── auth.py              # JWT authentication (158 lines)
│   ├── database.py          # DB connection setup (27 lines)
│   ├── requirements.txt     # Python dependencies
│   ├── Dockerfile           # Backend container
│   └── wait-for-db.py       # DB readiness checker
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main app + routing (351 lines)
│   │   ├── main.jsx         # React entry point
│   │   ├── index.css        # Global styles (1815 lines)
│   │   ├── App.css          # App-specific styles
│   │   ├── components/
│   │   │   ├── Dashboard.jsx    # KPIs & charts (529 lines)
│   │   │   ├── Products.jsx     # Product CRUD (410 lines)
│   │   │   ├── Sales.jsx        # Sales invoices (621 lines)
│   │   │   ├── Purchases.jsx    # Purchase invoices
│   │   │   ├── Customers.jsx    # Customer management
│   │   │   ├── Suppliers.jsx    # Supplier management
│   │   │   ├── Inventory.jsx    # Stock management (269 lines)
│   │   │   ├── Settings.jsx     # System settings (342 lines)
│   │   │   ├── Reports.jsx      # Financial reports (309 lines)
│   │   │   └── Login.jsx        # Authentication
│   │   └── services/
│   │       └── api.js           # Axios API client (165 lines)
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   ├── nginx.conf
│   └── Dockerfile
│
├── database/
│   └── schema.sql           # PostgreSQL schema (322 lines)
│
├── docker-compose.yml       # Development setup
├── docker-compose.prod.yml  # Production setup
├── start.bat                # Windows startup script
├── README.md
├── DEPLOYMENT.md
└── FEATURE_LIST.md
```

---

## 4. API Architecture | بنية الـ API

### 4.1 RESTful Design Pattern

The API follows REST conventions:
- **Resources**: `/api/{resource}` (plural nouns)
- **CRUD**: GET (read), POST (create), PUT (update), DELETE (remove)
- **Nesting**: Minimal (flat structure preferred)
- **Versioning**: Not implemented (single version)

### 4.2 Request/Response Flow

```
Client Request
     │
     ▼
┌─────────────────┐
│  CORS Middleware │ ← Validates origin
└────────┬────────┘
         ▼
┌─────────────────┐
│  OAuth2 Scheme  │ ← Extracts JWT token (optional)
└────────┬────────┘
         ▼
┌─────────────────┐
│ Route Handler   │ ← FastAPI endpoint function
└────────┬────────┘
         ▼
┌─────────────────┐
│ Auth Dependency │ ← get_current_user, require_admin, etc.
└────────┬────────┘
         ▼
┌─────────────────┐
│ Pydantic Schema │ ← Request validation
└────────┬────────┘
         ▼
┌─────────────────┐
│   CRUD Layer    │ ← Business logic & DB operations
└────────┬────────┘
         ▼
┌─────────────────┐
│  SQLAlchemy ORM │ ← Database queries
└────────┬────────┘
         ▼
┌─────────────────┐
│  PostgreSQL     │ ← Data persistence
└─────────────────┘
```

### 4.3 Authentication Flow

```
Login Request (username, password)
           │
           ▼
┌─────────────────────────┐
│  Query User by Username │
└───────────┬─────────────┘
            ▼
┌─────────────────────────┐
│    bcrypt.checkpw()     │ ← Verify password hash
└───────────┬─────────────┘
            ▼
┌─────────────────────────┐
│  jwt.encode() Token     │ ← Create JWT with username + role
└───────────┬─────────────┘
            ▼
┌─────────────────────────┐
│  Return Token + User    │ ← 24-hour expiration
└─────────────────────────┘

Protected Request (with Bearer token)
           │
           ▼
┌─────────────────────────┐
│  OAuth2PasswordBearer   │ ← Extract token from header
└───────────┬─────────────┘
            ▼
┌─────────────────────────┐
│  jwt.decode() Token     │ ← Verify signature + expiration
└───────────┬─────────────┘
            ▼
┌─────────────────────────┐
│  Return TokenData       │ ← {username, role}
└─────────────────────────┘
```

---

## 5. Database Design | تصميم قاعدة البيانات

### 5.1 Connection Configuration

```python
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://salesadmin:salespass123@localhost:5432/sales_management"
)
```

### 5.2 Session Management

- **Session Factory**: `sessionmaker(autocommit=False, autoflush=False)`
- **Dependency Injection**: `get_db()` yields session per request
- **Cleanup**: Session closed in `finally` block

### 5.3 ORM Patterns

- **Declarative Base**: All models inherit from `Base`
- **Relationships**: Defined with `relationship()` and `ForeignKey`
- **Cascade**: `cascade="all, delete-orphan"` for child items
- **Soft Delete**: Not implemented (hard delete only)

---

## 6. Frontend Architecture | بنية الواجهة

### 6.1 Component Structure

```
App.jsx (Root)
├── Login.jsx (Conditional - unauthenticated)
├── Sidebar (Navigation)
└── Main Content (Active Section)
    ├── Dashboard.jsx
    ├── Products.jsx
    ├── Sales.jsx
    ├── Purchases.jsx
    ├── Customers.jsx
    ├── Suppliers.jsx
    ├── Inventory.jsx
    ├── Settings.jsx
    ├── Reports.jsx
    └── UserManagement (Admin only)
```

### 6.2 State Management

- **Pattern**: Local component state with `useState`
- **Data Fetching**: `useEffect` on mount
- **No Global Store**: No Redux/Context (each component manages own state)
- **Token Storage**: `localStorage` for JWT persistence

### 6.3 API Communication

```javascript
// Axios instance with interceptors
const api = axios.create({ baseURL: '/api' });

// Auto-attach JWT token
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
});

// Auto-logout on 401
api.interceptors.response.use(
    response => response,
    error => {
        if (error.response?.status === 401) {
            localStorage.removeItem('token');
            window.location.reload();
        }
        return Promise.reject(error);
    }
);
```

---

## 7. Deployment Architecture | بنية النشر

### 7.1 Docker Compose Services

```yaml
services:
  postgres:     # Database
    - Port: 5432 (internal)
    - Volume: postgres_data
    
  backend:      # FastAPI
    - Port: 8000
    - Depends: postgres (healthy)
    
  frontend:     # Nginx + React
    - Port: 80 (dev) / 8888 (prod)
    - Depends: backend
```

### 7.2 Network Configuration

- **Network**: `sales_network` (bridge driver)
- **Service Discovery**: Container names as hostnames
- **Internal Communication**: postgres:5432, backend:8000

### 7.3 Production Nginx Config

```nginx
location /api {
    proxy_pass http://backend:8000;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

---

## 8. Security Architecture | بنية الأمان

### 8.1 Authentication

| Mechanism | Implementation |
|-----------|----------------|
| Token Type | JWT (Bearer) |
| Algorithm | HS256 |
| Expiration | 24 hours |
| Secret Key | Environment variable (should be 32+ chars) |

### 8.2 Authorization Roles

| Role | Permissions |
|------|-------------|
| admin | All operations + user management |
| manager | Sales, purchases, reports (no user management) |
| cashier | Create sales only |

### 8.3 Password Security

- **Hashing**: bcrypt with automatic salt
- **Rounds**: 12 (default bcrypt)
- **Verification**: Constant-time comparison

### 8.4 API Security

- **CORS**: Whitelist origins (configurable via env)
- **SQL Injection**: Prevented via SQLAlchemy ORM
- **Input Validation**: Pydantic schemas
- **Rate Limiting**: slowapi available (not configured)

---

## 9. Configuration | التهيئة

### 9.1 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | postgresql://... | Database connection string |
| `SECRET_KEY` | hardcoded | JWT signing key |
| `ALLOWED_ORIGINS` | localhost:5173,... | CORS whitelist |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 1440 (24hrs) | Token lifetime |

### 9.2 Default Credentials

```
Admin:    admin / admin123
```

---

## 10. Technical Debt Notes | ملاحظات الديون التقنية

- SECRET_KEY is hardcoded in source code
- No rate limiting configured
- No request logging middleware
- Single monolithic main.py (1080 lines)
- No database migrations tool (Alembic)
- No automated tests
- No CI/CD pipeline defined

---

*Document reverse-engineered from codebase analysis - March 2026*
