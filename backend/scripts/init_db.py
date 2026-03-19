"""
Database initialization script
Creates tables and initial admin user
"""

import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.session import Base, engine
from app.models import User, Diagnosis, ChatSession, ChatMessage
from app.core.security import get_password_hash
from app.core.config import settings


def init_db():
    """Initialize database tables and create admin user"""
    print("🔄 Creating database tables...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        
        # Create session
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Check if admin user exists
        admin_email = "admin@agrovee.com"
        existing_admin = db.query(User).filter(User.email == admin_email).first()
        
        if not existing_admin:
            print("🔄 Creating admin user...")
            admin_user = User(
                email=admin_email,
                hashed_password=get_password_hash("admin123"),
                full_name="System Administrator",
                is_active=True,
                is_admin=True,
                is_verified=True
            )
            db.add(admin_user)
            db.commit()
            print(f"✅ Admin user created!")
            print(f"   Email: {admin_email}")
            print(f"   Password: admin123")
            print(f"   ⚠️  CHANGE PASSWORD IN PRODUCTION!")
        else:
            print(f"ℹ️  Admin user already exists: {admin_email}")
        
        db.close()
        print("\n✅ Database initialization complete!")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        sys.exit(1)


if __name__ == "__main__":
    print("="*60)
    print("Agrovee - Database Initialization")
    print("="*60)
    print(f"Database URL: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else 'Local'}")
    print()
    
    init_db()
