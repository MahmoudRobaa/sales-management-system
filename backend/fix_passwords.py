#!/usr/bin/env python3
import bcrypt

# Generate password hashes
admin_hash = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
cashier_hash = bcrypt.hashpw('cashier123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

print(f"Admin hash: {admin_hash}")
print(f"Cashier hash: {cashier_hash}")
print()
print("SQL commands:")
print(f"UPDATE users SET password_hash = '{admin_hash}' WHERE username = 'admin';")
print(f"UPDATE users SET password_hash = '{cashier_hash}' WHERE username = 'cashier';")
