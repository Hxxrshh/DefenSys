"""
Database Migration Script for Phase 1
Creates/updates all tables for targets, scans, vulnerabilities, and findings
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.database import engine
from api.models import Base, Target, Project, Scan, Vulnerability, Finding

def migrate_database():
    """Create all tables"""
    print("🔄 Starting database migration...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        print("✅ Database migration completed successfully!")
        print("\nCreated tables:")
        print("  - targets")
        print("  - projects") 
        print("  - scans")
        print("  - vulnerabilities")
        print("  - findings")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = migrate_database()
    sys.exit(0 if success else 1)
