#!/usr/bin/env python3
"""
Simple migration to add scan_type column to scans table
"""

from api.database import engine
import sqlalchemy

def migrate_add_scan_type():
    """Add scan_type column to scans table if it doesn't exist"""
    try:
        # Check if column already exists
        inspector = sqlalchemy.inspect(engine)
        columns = inspector.get_columns('scans')
        column_names = [col['name'] for col in columns]
        
        if 'scan_type' in column_names:
            print("✅ scan_type column already exists")
            return
        
        # Add the column
        with engine.connect() as connection:
            # Use appropriate SQL for the database type
            if 'postgresql' in str(engine.url):
                connection.execute(sqlalchemy.text("ALTER TABLE scans ADD COLUMN scan_type VARCHAR"))
            elif 'sqlite' in str(engine.url):
                connection.execute(sqlalchemy.text("ALTER TABLE scans ADD COLUMN scan_type TEXT"))
            else:
                connection.execute(sqlalchemy.text("ALTER TABLE scans ADD COLUMN scan_type VARCHAR(255)"))
            
            connection.commit()
            print("✅ Successfully added scan_type column to scans table")
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise

if __name__ == "__main__":
    migrate_add_scan_type()