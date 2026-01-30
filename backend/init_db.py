"""
Initialize database with default admin user
Run this once after creating the database schema
"""
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
from auth import get_password_hash

# Create tables
models.Base.metadata.create_all(bind=engine)

# Create session
db = SessionLocal()

# Check if admin user exists
admin = db.query(models.User).filter(models.User.username == "admin").first()

if admin:
    print("✓ Admin user already exists")
else:
    # Create admin user
    admin_user = models.User(
        username="admin",
        password_hash=get_password_hash("admin123"),
        full_name="مدير النظام",
        role="admin",
        is_active=True
    )
    db.add(admin_user)
    db.commit()
    print("✓ Admin user created successfully")
    print("  Username: admin")
    print("  Password: admin123")

db.close()
