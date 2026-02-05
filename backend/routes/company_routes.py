"""
Company management routes
Create, update, and manage company profiles
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import get_db
from database.models import Company, User, IndustryType
from security import get_current_user
from security.audit_logger import AuditLogger

router = APIRouter(prefix="/companies")


# Pydantic models
class CompanyCreate(BaseModel):
    name: str
    registration_number: Optional[str] = None
    pan: Optional[str] = None
    gstin: Optional[str] = None
    industry: IndustryType
    sub_industry: Optional[str] = None
    founded_date: Optional[datetime] = None
    employee_count: Optional[int] = None
    annual_revenue: Optional[float] = None
    website: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    country: str = "India"


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    registration_number: Optional[str] = None
    pan: Optional[str] = None
    gstin: Optional[str] = None
    industry: Optional[IndustryType] = None
    sub_industry: Optional[str] = None
    founded_date: Optional[datetime] = None
    employee_count: Optional[int] = None
    annual_revenue: Optional[float] = None
    website: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None


class CompanyResponse(BaseModel):
    id: int
    name: str
    registration_number: Optional[str]
    pan: Optional[str]
    gstin: Optional[str]
    industry: str
    sub_industry: Optional[str]
    founded_date: Optional[datetime]
    employee_count: Optional[int]
    annual_revenue: Optional[float]
    website: Optional[str]
    city: Optional[str]
    state: Optional[str]
    country: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


@router.post("/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
    company_data: CompanyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new company profile
    """
    # Check if registration number already exists
    if company_data.registration_number:
        existing = db.query(Company).filter(
            Company.registration_number == company_data.registration_number
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Company with this registration number already exists"
            )
    
    # Create company
    new_company = Company(
        user_id=current_user.id,
        **company_data.dict()
    )
    
    db.add(new_company)
    db.commit()
    db.refresh(new_company)
    
    # Log creation
    AuditLogger.log_data_modification(
        db=db,
        user_id=current_user.id,
        resource_type="company",
        resource_id=new_company.id,
        action="create"
    )
    
    return CompanyResponse.from_orm(new_company)


@router.get("/", response_model=List[CompanyResponse])
async def list_companies(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all companies owned by current user
    """
    companies = db.query(Company).filter(Company.user_id == current_user.id).all()
    return [CompanyResponse.from_orm(c) for c in companies]


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get specific company details
    """
    company = db.query(Company).filter(
        Company.id == company_id,
        Company.user_id == current_user.id
    ).first()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Log access
    AuditLogger.log_data_access(
        db=db,
        user_id=current_user.id,
        resource_type="company",
        resource_id=company_id,
        action="read"
    )
    
    return CompanyResponse.from_orm(company)


@router.patch("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: int,
    company_data: CompanyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update company profile
    """
    company = db.query(Company).filter(
        Company.id == company_id,
        Company.user_id == current_user.id
    ).first()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Update fields
    update_data = company_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(company, field, value)
    
    company.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(company)
    
    # Log update
    AuditLogger.log_data_modification(
        db=db,
        user_id=current_user.id,
        resource_type="company",
        resource_id=company_id,
        action="update",
        changes=update_data
    )
    
    return CompanyResponse.from_orm(company)


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
    company_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete company (and all associated data)
    """
    company = db.query(Company).filter(
        Company.id == company_id,
        Company.user_id == current_user.id
    ).first()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Log deletion
    AuditLogger.log_data_modification(
        db=db,
        user_id=current_user.id,
        resource_type="company",
        resource_id=company_id,
        action="delete"
    )
    
    db.delete(company)
    db.commit()
    
    return None
