"""
Seed database with initial development data
"""
import sys
import os
from datetime import datetime, timedelta
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.database import SessionLocal, init_db, engine, Base, drop_db
from database.models import User, Company, IndustryType, RiskLevel, FinancialStatement, Transaction
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

    # 2. Create some sample companies if they don't exist
    companies_data = [
        {
            "name": "TechFlow Solutions",
            "registration_number": "ROC123456",
            "industry": IndustryType.IT_SOFTWARE,
            "city": "Bangalore",
            "state": "Karnataka",
            "annual_revenue": 5000000.0,
            "founded_date": datetime.utcnow() - timedelta(days=5*365)
        },
        {
            "name": "GreenHarvest Agri",
            "registration_number": "ROC654321",
            "industry": IndustryType.AGRICULTURE,
            "city": "Pune",
            "state": "Maharashtra",
            "annual_revenue": 2500000.0,
            "founded_date": datetime.utcnow() - timedelta(days=3*365)
        },
        {
            "name": "Urban Style Retail",
            "registration_number": "ROC987654",
            "industry": IndustryType.RETAIL,
            "city": "Mumbai",
            "state": "Maharashtra",
            "annual_revenue": 12000000.0,
            "founded_date": datetime.utcnow() - timedelta(days=8*365)
        }
    ]
    
    for comp_info in companies_data:
        company = db.query(Company).filter(Company.registration_number == comp_info["registration_number"]).first()
        if not company:
            print(f"Creating company: {comp_info['name']}")
            company = Company(
                user_id=dev_user.id,
                **comp_info
            )
            db.add(company)
            db.commit()
            db.refresh(company)
        
        # 3. Add Financial Data if missing
        if db.query(FinancialStatement).filter(FinancialStatement.company_id == company.id).count() == 0:
            print(f"Seeding financial data for {company.name}...")
            
            # Balance Sheet
            bs_data = {
                "assets": {
                    "current_assets": {
                        "cash_in_hand": company.annual_revenue * 0.1,
                        "bank_balance": company.annual_revenue * 0.2,
                        "accounts_receivable": company.annual_revenue * 0.15,
                        "inventory": company.annual_revenue * 0.05
                    },
                    "fixed_assets": {
                        "office_equipment": 500000.0,
                        "furniture": 200000.0
                    },
                    "total_assets": company.annual_revenue * 0.5 + 700000.0
                },
                "liabilities": {
                    "current_liabilities": {
                        "accounts_payable": company.annual_revenue * 0.1,
                        "short_term_loan": company.annual_revenue * 0.05
                    },
                    "long_term_liabilities": {
                        "term_loan": 1000000.0
                    },
                    "total_liabilities": company.annual_revenue * 0.15 + 1000000.0
                },
                "equity": {
                    "items": {
                        "share_capital": 1000000.0,
                        "retained_earnings": company.annual_revenue * 0.2
                    },
                    "total_equity": 1000000.0 + company.annual_revenue * 0.2
                }
            }
            
            bs = FinancialStatement(
                company_id=company.id,
                statement_type="balance_sheet",
                period_start=datetime.utcnow() - timedelta(days=365),
                period_end=datetime.utcnow(),
                fiscal_year="2024-25",
                data=bs_data,
                total_assets=bs_data["assets"]["total_assets"],
                total_liabilities=bs_data["liabilities"]["total_liabilities"],
                total_equity=bs_data["equity"]["total_equity"],
                source="manual"
            )
            db.add(bs)

            # Profit & Loss
            revenue = company.annual_revenue
            cogs = revenue * 0.4
            gross_profit = revenue - cogs
            operating_expenses = revenue * 0.3
            operating_profit = gross_profit - operating_expenses
            net_profit = operating_profit * 0.8 # After tax etc.
            
            pl_data = {
                "revenue": {
                    "items": {"sales": revenue},
                    "total_revenue": revenue
                },
                "expenses": {
                    "cost_of_goods_sold": cogs,
                    "operating_expenses": {
                        "salaries": operating_expenses * 0.6,
                        "rent": operating_expenses * 0.2,
                        "marketing": operating_expenses * 0.2
                    },
                    "total_expenses": cogs + operating_expenses
                },
                "profit": {
                    "gross_profit": gross_profit,
                    "operating_profit": operating_profit,
                    "net_profit": net_profit
                }
            }
            
            pl = FinancialStatement(
                company_id=company.id,
                statement_type="profit_loss",
                period_start=datetime.utcnow() - timedelta(days=365),
                period_end=datetime.utcnow(),
                fiscal_year="2024-25",
                data=pl_data,
                total_revenue=revenue,
                total_expenses=cogs + operating_expenses,
                net_profit=net_profit,
                source="manual"
            )
            db.add(pl)

            # Transactions
            for i in range(20):
                txn = Transaction(
                    company_id=company.id,
                    transaction_date=datetime.utcnow() - timedelta(days=i*15),
                    description=f"Transaction {i}",
                    amount=revenue / 50,
                    category="revenue" if i % 2 == 0 else "expense",
                    debit_credit="credit" if i % 2 == 0 else "debit",
                    source="bank_sync"
                )
                db.add(txn)
            
            db.commit()

    db.close()
    print("✓ Seeding completed successfully")

if __name__ == "__main__":
    print("Starting database seeding...")
    # Uncomment to clear DB before seeding
    # drop_db()
    init_db()
    seed_data()
