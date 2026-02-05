"""
Seed database with initial development data
"""
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.database import SessionLocal, init_db, engine, Base
from database.models import User, Company, IndustryType, RiskLevel
from security import AuthService

def seed_data():
    db = SessionLocal()
    
    # 1. Create a development user
    dev_user = db.query(User).filter(User.email == "dev@example.com").first()
    if not dev_user:
        print("Creating development user...")
        dev_user = User(
            email="dev@example.com",
            hashed_password=AuthService.get_password_hash("password123"),
            full_name="Dev User",
            is_active=True,
            is_verified=True,
            role="admin"
        )
        db.add(dev_user)
        db.commit()
        db.refresh(dev_user)
        print(f"✓ Created user: {dev_user.email}")
    else:
        print(f"User {dev_user.email} already exists")

    # 2. Create some sample companies
    if db.query(Company).count() == 0:
        print("Creating sample companies...")
        companies = [
            {
                "name": "TechFlow Solutions",
                "registration_number": "ROC123456",
                "industry": IndustryType.IT_SOFTWARE,
                "city": "Bangalore",
                "state": "Karnataka",
                "annual_revenue": 5000000.0
            },
            {
                "name": "GreenHarvest Agri",
                "registration_number": "ROC654321",
                "industry": IndustryType.AGRICULTURE,
                "city": "Pune",
                "state": "Maharashtra",
                "annual_revenue": 2500000.0
            },
            {
                "name": "Urban Style Retail",
                "registration_number": "ROC987654",
                "industry": IndustryType.RETAIL,
                "city": "Mumbai",
                "state": "Maharashtra",
                "annual_revenue": 12000000.0
            }
        ]
        
        for comp_data in companies:
            company = Company(
                user_id=dev_user.id,
                **comp_data
            )
            db.add(company)
        
        db.commit()
        print(f"✓ Created {len(companies)} companies")
    else:
        print("Companies already exist in database")

    db.close()
    print("✓ Seeding completed successfully")

if __name__ == "__main__":
    print("Starting database seeding...")
    # Ensure tables exist
    init_db()
    seed_data()
