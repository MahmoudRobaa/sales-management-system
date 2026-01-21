"""
Migration script to add cash_transactions table for capital/cash management
"""
from database import engine
from sqlalchemy import text

def migrate():
    with engine.connect() as conn:
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS cash_transactions (
                    id SERIAL PRIMARY KEY,
                    transaction_type VARCHAR(50) NOT NULL,
                    amount DECIMAL(15, 2) NOT NULL,
                    balance_before DECIMAL(15, 2) NOT NULL,
                    balance_after DECIMAL(15, 2) NOT NULL,
                    reference_type VARCHAR(50),
                    reference_id INTEGER,
                    description TEXT,
                    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            print("Created cash_transactions table")
            
            # Create index for faster lookups
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_cash_transactions_type ON cash_transactions(transaction_type)
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_cash_transactions_created ON cash_transactions(created_at DESC)
            """))
            print("Created indexes on cash_transactions")
            
            conn.commit()
            print("Migration complete!")
        except Exception as e:
            print(f"Migration error: {e}")
            conn.rollback()

if __name__ == "__main__":
    migrate()
