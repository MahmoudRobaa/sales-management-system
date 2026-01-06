"""
Migration script to add payment_method column
"""
from database import engine
from sqlalchemy import text

def migrate():
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE sales ADD COLUMN payment_method VARCHAR(50) DEFAULT 'كاش'"))
            print("Added payment_method to sales table")
        except Exception as e:
            print(f"Sales column may already exist: {e}")
        
        try:
            conn.execute(text("ALTER TABLE purchases ADD COLUMN payment_method VARCHAR(50) DEFAULT 'كاش'"))
            print("Added payment_method to purchases table")
        except Exception as e:
            print(f"Purchases column may already exist: {e}")
        
        conn.commit()
        print("Migration complete!")

if __name__ == "__main__":
    migrate()
