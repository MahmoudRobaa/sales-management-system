"""
Application constants and enumerations.
نظام إدارة المبيعات - الثوابت والتعدادات
"""
from enum import Enum


# ============================================
# USER ROLES
# ============================================
class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    CASHIER = "cashier"

    @classmethod
    def values(cls) -> list[str]:
        return [e.value for e in cls]


# Role hierarchy helpers
ADMIN_ROLES: list[str] = [UserRole.ADMIN]
MANAGER_ROLES: list[str] = [UserRole.ADMIN, UserRole.MANAGER]
ALL_ROLES: list[str] = [UserRole.ADMIN, UserRole.MANAGER, UserRole.CASHIER]


# ============================================
# PAYMENT METHODS
# ============================================
class PaymentMethod(str, Enum):
    CASH = "كاش"
    CREDIT = "آجل"
    BANK_TRANSFER = "تحويل بنكي"
    CHECK = "شيك"


DEFAULT_PAYMENT_METHOD: str = PaymentMethod.CASH


# ============================================
# TRANSACTION / INVOICE STATUS
# ============================================
class InvoiceStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    PARTIAL = "partial"


DEFAULT_INVOICE_STATUS: str = InvoiceStatus.PENDING


# ============================================
# INVENTORY MOVEMENT TYPES
# ============================================
class MovementType(str, Enum):
    SALE = "sale"
    PURCHASE = "purchase"
    ADJUSTMENT = "adjustment"
    RETURN = "return"


# ============================================
# INVENTORY ADJUSTMENT TYPES
# ============================================
class AdjustmentType(str, Enum):
    ADD = "add"
    SUBTRACT = "subtract"
    SET = "set"


# ============================================
# PAYMENT / REFERENCE TYPES
# ============================================
class ReferenceType(str, Enum):
    SALE = "sale"
    PURCHASE = "purchase"
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"


# ============================================
# ACTIVITY LOG ACTIONS
# ============================================
class ActivityAction(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    IMPORT = "import"
    EXPORT = "export"


# ============================================
# ENTITY TYPES (for activity logs)
# ============================================
class EntityType(str, Enum):
    AUTH = "auth"
    USER = "user"
    PRODUCT = "product"
    CATEGORY = "category"
    SUPPLIER = "supplier"
    CUSTOMER = "customer"
    SALE = "sale"
    PURCHASE = "purchase"
    INVENTORY = "inventory"
    SETTING = "setting"
    CASH = "cash"


# ============================================
# CASH TRANSACTION TYPES
# ============================================
class CashTransactionType(str, Enum):
    SALE = "sale"
    PURCHASE = "purchase"
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"
    ADJUSTMENT = "adjustment"


# ============================================
# PASSWORD POLICY
# ============================================
MIN_PASSWORD_LENGTH: int = 8


# ============================================
# PAGINATION DEFAULTS
# ============================================
DEFAULT_PAGE_SKIP: int = 0
DEFAULT_PAGE_LIMIT: int = 100
MAX_PAGE_LIMIT: int = 10000


# ============================================
# CODE PREFIXES
# ============================================
class CodePrefix(str, Enum):
    PRODUCT = "PRD"
    SUPPLIER = "SUP"
    CUSTOMER = "CUS"
    SALE_INVOICE = "INV"
    PURCHASE_INVOICE = "PUR"


# ============================================
# STOCK STATUS THRESHOLDS
# ============================================
class StockStatus(str, Enum):
    GOOD = "good"
    LOW = "low"
    OUT_OF_STOCK = "out"

DEFAULT_MIN_QUANTITY: int = 5


# ============================================
# API VERSION
# ============================================
API_VERSION: str = "2.0.0"
API_TITLE: str = "Sales Management System API"
API_DESCRIPTION: str = "نظام إدارة المبيعات - API"
