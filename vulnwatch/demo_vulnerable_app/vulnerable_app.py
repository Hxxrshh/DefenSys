
import sqlite3
import hashlib
import os

# VULNERABILITY 1: Hardcoded password (Bandit will catch this)
DATABASE_PASSWORD = "admin123"

# VULNERABILITY 2: SQL Injection vulnerability
def get_user(user_id):
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    # This is vulnerable to SQL injection
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    return cursor.fetchone()

# VULNERABILITY 3: Weak cryptographic hash
def hash_password(password):
    # MD5 is cryptographically broken
    return hashlib.md5(password.encode()).hexdigest()

# VULNERABILITY 4: Command injection vulnerability
def process_file(filename):
    # This allows command injection
    os.system(f"cat {filename}")

# VULNERABILITY 5: Insecure random number generation
import random
def generate_token():
    return random.randint(1000, 9999)

if __name__ == "__main__":
    print("Starting vulnerable app...")
