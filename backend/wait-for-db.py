#!/usr/bin/env python3
"""
Wait for database to be ready before starting the application
"""
import os
import time
import socket

def wait_for_db(max_retries=60, retry_interval=1):
    """Wait for database to be ready"""
    host = 'postgres'
    port = 5432
    
    print(f"Waiting for database at {host}:{port}...")
    
    for attempt in range(max_retries):
        try:
            # First check if we can resolve the hostname
            socket.gethostbyname(host)
            # Then check if the port is open
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                print(f"✓ Database is ready! (attempt {attempt + 1})")
                # Wait extra seconds for database to fully initialize
                time.sleep(3)
                return True
            else:
                raise Exception(f"Port {port} not open")
                
        except Exception as e:
            print(f"⏳ Database not ready yet (attempt {attempt + 1}/{max_retries}): {str(e)[:100]}")
            if attempt < max_retries - 1:
                time.sleep(retry_interval)
            else:
                print("✗ Database connection timeout!")
                return False
    
    return False

if __name__ == "__main__":
    if wait_for_db():
        exit(0)
    else:
        exit(1)
