#!/usr/bin/env python3

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, '/app/src')

from server import app, db

def init_db():
    """Initialize the database tables."""
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()
