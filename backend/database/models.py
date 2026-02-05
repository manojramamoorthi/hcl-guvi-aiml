"""
SQLAlchemy database models for SME Financial Platform
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import Base


class IndustryType(str, enum.Enum):
    """Industry categories"""
    MANUFACTURING = "Manufacturing"
    RETAIL = "Retail"
    AGRICULTURE = "Agriculture"
    SERVICES = "Services"
    LOGISTICS = "Logistics"
    ECOMMERCE = "E-commerce"
    HEALTHCARE = "Healthcare"
    EDUCATION = "Education"
    HOSPITALITY = "Hospitality"
    CONSTRUCTION = "Construction"
    IT_SOFTWARE = "IT & Software"
    OTHER = "Other"


class RiskLevel(str, enum.Enum):
    """Risk severity levels"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class IntegrationStatus(str, enum.Enum):
    """API integration status"""
    CONNECTED = "Connected"
    DISCONNECTED = "Disconnected"
    ERROR = "Error"
    SYNCING = "Syncing"


# ==================== USER & AUTHENTICATION ====================

class User(Base):
    """User accounts"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    phone = Column(String(20))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    role = Column(String(50), default="user")  # user, admin, analyst
    language_preference = Column(String(5), default="en")  # en, hi
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    companies = relationship("Company", back_populates="owner")
    audit_logs = relationship("AuditLog", back_populates="user")


# ==================== COMPANY PROFILE ====================

class Company(Base):
    """SME company profiles"""
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Basic Information
    name = Column(String(255), nullable=False)
    registration_number = Column(String(100), unique=True)
    pan = Column(String(10))
    gstin = Column(String(15))
    industry = Column(Enum(IndustryType), nullable=False)
    sub_industry = Column(String(100))
    
    # Business Details
    founded_date = Column(DateTime)
    employee_count = Column(Integer)
    annual_revenue = Column(Float)
    website = Column(String(255))
    
    # Address
    address_line1 = Column(String(255))
    address_line2 = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    pincode = Column(String(10))
    country = Column(String(100), default="India")
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="companies")
    financial_statements = relationship("FinancialStatement", back_populates="company", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="company", cascade="all, delete-orphan")
    credit_scores = relationship("CreditScore", back_populates="company", cascade="all, delete-orphan")
    risk_assessments = relationship("RiskAssessment", back_populates="company", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="company", cascade="all, delete-orphan")
    integrations = relationship("Integration", back_populates="company", cascade="all, delete-orphan")
    tax_compliance = relationship("TaxCompliance", back_populates="company", cascade="all, delete-orphan")


# ==================== FINANCIAL DATA ====================

class FinancialStatement(Base):
    """Financial statements - Balance Sheet, P&L, Cash Flow"""
    __tablename__ = "financial_statements"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    # Statement Details
    statement_type = Column(String(50), nullable=False)  # balance_sheet, profit_loss, cash_flow
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    fiscal_year = Column(String(10))
    
    # Financial Data (stored as JSON for flexibility)
    data = Column(JSON, nullable=False)
    # Example structure:
    # {
    #   "assets": {"current": {...}, "fixed": {...}},
    #   "liabilities": {"current": {...}, "long_term": {...}},
    #   "equity": {...},
    #   "revenue": {...},
    #   "expenses": {...},
    #   "profit_metrics": {...}
    # }
    
    # Calculated Metrics
    total_assets = Column(Float)
    total_liabilities = Column(Float)
    total_equity = Column(Float)
    total_revenue = Column(Float)
    total_expenses = Column(Float)
    net_profit = Column(Float)
    
    # Metadata
    source = Column(String(100))  # uploaded, api_sync, manual
    uploaded_file = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="financial_statements")


class Transaction(Base):
    """Individual financial transactions"""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    # Transaction Details
    transaction_date = Column(DateTime, nullable=False)
    description = Column(Text)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="INR")
    
    # Categorization
    category = Column(String(100))  # revenue, expense, asset_purchase, etc.
    sub_category = Column(String(100))
    is_recurring = Column(Boolean, default=False)
    
    # Accounting
    account_type = Column(String(50))  # cash, bank, credit_card, accounts_payable, etc.
    debit_credit = Column(String(10))  # debit, credit
    
    # Integration
    source = Column(String(100))  # manual, bank_sync, payment_gateway, gst
    external_id = Column(String(255))  # ID from external system
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="transactions")


# ==================== ANALYSIS & SCORING ====================

class CreditScore(Base):
    """Credit score evaluations"""
    __tablename__ = "credit_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    # Score
    score = Column(Integer, nullable=False)  # 300-900 range
    grade = Column(String(5))  # A+, A, B+, B, C+, C, D
    risk_category = Column(Enum(RiskLevel))
    
    # Score Components (JSON)
    score_breakdown = Column(JSON)
    # {
    #   "payment_history": 35,
    #   "credit_utilization": 25,
    #   "liquidity": 20,
    #   "profitability": 15,
    #   "leverage": 5
    # }
    
    # Key Factors
    positive_factors = Column(JSON)  # List of strengths
    negative_factors = Column(JSON)  # List of weaknesses
    improvement_suggestions = Column(JSON)
    
    # Metadata
    calculated_at = Column(DateTime, default=datetime.utcnow)
    valid_until = Column(DateTime)
    
    # Relationships
    company = relationship("Company", back_populates="credit_scores")


class RiskAssessment(Base):
    """Risk identification and assessment"""
    __tablename__ = "risk_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    # Risk Details
    risk_type = Column(String(100), nullable=False)  # liquidity, credit, operational, market
    risk_level = Column(Enum(RiskLevel), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Impact & Probability
    impact_score = Column(Integer)  # 1-10
    probability_score = Column(Integer)  # 1-10
    overall_risk_score = Column(Float)  # Calculated from impact * probability
    
    # Mitigation
    mitigation_strategies = Column(JSON)  # List of suggested actions
    status = Column(String(50), default="identified")  # identified, mitigating, resolved
    
    # Metadata
    identified_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="risk_assessments")


class Recommendation(Base):
    """AI-generated recommendations and insights"""
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    # Recommendation Details
    recommendation_type = Column(String(100), nullable=False)  # cost_optimization, financial_product, growth_opportunity
    title = Column(String(255), nullable=False)
    description = Column(Text)
    detailed_insight = Column(Text)  # AI-generated narrative
    
    # Priority & Impact
    priority = Column(String(20))  # high, medium, low
    estimated_impact = Column(Text)  # Expected benefit
    
    # Financial Product Recommendations
    product_category = Column(String(100))  # loan, credit_line, insurance, investment
    provider_name = Column(String(255))
    product_details = Column(JSON)
    
    # Actions
    actionable_steps = Column(JSON)  # List of steps to implement
    
    # Metadata
    language = Column(String(5), default="en")
    generated_at = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)
    is_implemented = Column(Boolean, default=False)
    
    # Relationships
    company = relationship("Company", back_populates="recommendations")


# ==================== INTEGRATIONS ====================

class Integration(Base):
    """External API integrations"""
    __tablename__ = "integrations"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    # Integration Details
    integration_type = Column(String(100), nullable=False)  # plaid_banking, razorpay, gst
    provider_name = Column(String(255))
    account_id = Column(String(255))  # External account identifier
    
    # Status
    status = Column(Enum(IntegrationStatus), default=IntegrationStatus.DISCONNECTED)
    last_sync_at = Column(DateTime)
    next_sync_at = Column(DateTime)
    sync_frequency = Column(String(50))  # daily, weekly, manual
    
    # Configuration
    config = Column(JSON)  # API-specific config
    access_token = Column(Text)  # Encrypted token
    
    # Metadata
    connected_at = Column(DateTime)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="integrations")


# ==================== TAX & COMPLIANCE ====================

class TaxCompliance(Base):
    """Tax compliance and GST records"""
    __tablename__ = "tax_compliance"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    # Filing Details
    filing_type = Column(String(50), nullable=False)  # GSTR1, GSTR3B, Annual Return
    filing_period = Column(String(20), nullable=False)  # MM-YYYY
    due_date = Column(DateTime, nullable=False)
    filed_date = Column(DateTime)
    
    # Status
    status = Column(String(50), default="pending")  # pending, filed, overdue, error
    is_compliant = Column(Boolean, default=True)
    
    # Data
    filing_data = Column(JSON)  # GST return data
    total_sales = Column(Float)
    total_purchases = Column(Float)
    tax_liability = Column(Float)
    input_tax_credit = Column(Float)
    net_tax_payable = Column(Float)
    
    # Deductions
    deductions_claimed = Column(JSON)  # List of deductions
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="tax_compliance")


# ==================== AUDIT & LOGGING ====================

class AuditLog(Base):
    """Audit trail for security and compliance"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Event Details
    event_type = Column(String(100), nullable=False)  # login, data_access, data_modify, etc.
    resource_type = Column(String(100))  # user, company, financial_statement, etc.
    resource_id = Column(Integer)
    action = Column(String(100), nullable=False)  # create, read, update, delete
    
    # Context
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    details = Column(JSON)  # Additional context
    
    # Metadata
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
