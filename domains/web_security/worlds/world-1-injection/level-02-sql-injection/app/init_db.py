#!/usr/bin/env python3
"""
Initialize SQLite database for SQL injection challenge
"""

import sqlite3
import os

# Create database
conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# Create users table
cursor.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        secret TEXT
    )
''')

# Get flag from environment or use default
FLAG = os.environ.get('FLAG', 'ARENA{SQL_1nj3ct10n_m4st3r}')

# Insert sample users
users = [
    ('admin', 'super_secret_password_123', 'administrator', FLAG),
    ('john', 'password123', 'user', None),
    ('alice', 'alice2023', 'user', None),
    ('bob', 'qwerty', 'user', None),
]

cursor.executemany(
    'INSERT INTO users (username, password, role, secret) VALUES (?, ?, ?, ?)',
    users
)

conn.commit()
conn.close()

print("Database initialized successfully")
