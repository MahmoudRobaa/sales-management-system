from database import engine, Base
from models import *  # Import all models to ensure they are registered

print("Dropping all tables...")
Base.metadata.drop_all(bind=engine)
print("Tables dropped.")

print("Recreating tables...")
Base.metadata.create_all(bind=engine)
print("Tables recreated successfully!")
print("Run 'python migrate_cash.py' to ensure all migrations are applied if needed.")
