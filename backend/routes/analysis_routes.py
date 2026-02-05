"""
Financial analysis routes
Calculate ratios, assess credit, analyze cash flow
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import get_db
from database.models import Company, User, FinancialStatement, CreditScore, RiskAssessment, Recommendation
from security import get_current_user
from services.financial_analyzer import FinancialAnalyzer
from services.credit_scoring import CreditScoringEngine
from services.ai_service import ai_service
from security.audit_logger import AuditLogger

router = APIRouter(prefix="/analysis")


class FinancialRatiosResponse(BaseModel):
    company_id: int
    liquidity: Dict[str, float]
    profitability: Dict[str, float]
    leverage: Dict[str, float]
    efficiency: Dict[str, float]
    calculated_at: datetime


class CreditScoreResponse(BaseModel):
    company_id: int
    score: int
    grade: str
    risk_category: str
    breakdown: Dict[str, Any]
    strengths: List[str]
    weaknesses: List[str]
    improvement_suggestions: List[str]
    calculated_at: datetime


class FinancialHealthResponse(BaseModel):
    company_id: int
    overall_score: int
    grade: str
    score_breakdown: Dict[str, int]
    ratios: Dict[str, Dict[str, float]]
    cash_flow_summary: Dict[str, Any]
    ai_insights: Optional[str] = None


@router.get("/{company_id}/ratios", response_model=FinancialRatiosResponse)
async def calculate_financial_ratios(
    company_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Calculate financial ratios for a company
    
    Returns liquidity, profitability, leverage, and efficiency ratios
    """
    # Verify company ownership
    company = db.query(Company).filter(
        Company.id == company_id,
        Company.user_id == current_user.id
    ).first()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Get latest financial statements
    balance_sheet_stmt = db.query(FinancialStatement).filter(
        FinancialStatement.company_id == company_id,
        FinancialStatement.statement_type == "balance_sheet"
    ).order_by(FinancialStatement.period_end.desc()).first()
    
    pl_stmt = db.query(FinancialStatement).filter(
        FinancialStatement.company_id == company_id,
        FinancialStatement.statement_type == "profit_loss"
    ).order_by(FinancialStatement.period_end.desc()).first()
    
    if not balance_sheet_stmt or not pl_stmt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Both balance sheet and P&L statements required for ratio analysis"
        )
    
    # Prepare financial data
    financial_data = {
        "balance_sheet": balance_sheet_stmt.data,
        "profit_loss": pl_stmt.data
    }
    
    # Calculate ratios
    ratios = FinancialAnalyzer.calculate_all_ratios(financial_data)
    
    # Log access
    AuditLogger.log_data_access(
        db=db,
        user_id=current_user.id,
        resource_type="financial_analysis",
        resource_id=company_id
    )
    
    return {
        "company_id": company_id,
        **ratios,
        "calculated_at": datetime.utcnow()
    }


@router.get("/{company_id}/credit-score", response_model=CreditScoreResponse)
async def calculate_credit_score(
    company_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Calculate credit score for a company
    
    Returns comprehensive creditworthiness assessment
    """
    # Verify company ownership
    company = db.query(Company).filter(
        Company.id == company_id,
        Company.user_id == current_user.id
    ).first()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Get latest financial statements
    balance_sheet_stmt = db.query(FinancialStatement).filter(
        FinancialStatement.company_id == company_id,
        FinancialStatement.statement_type == "balance_sheet"
    ).order_by(FinancialStatement.period_end.desc()).first()
    
    pl_stmt = db.query(FinancialStatement).filter(
        FinancialStatement.company_id == company_id,
        FinancialStatement.statement_type == "profit_loss"
    ).order_by(FinancialStatement.period_end.desc()).first()
    
    if not balance_sheet_stmt or not pl_stmt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Financial statements required for credit scoring"
        )
    
    # Prepare financial data
    financial_data = {
        "balance_sheet": balance_sheet_stmt.data,
        "profit_loss": pl_stmt.data,
        "ratios": FinancialAnalyzer.calculate_all_ratios({
            "balance_sheet": balance_sheet_stmt.data,
            "profit_loss": pl_stmt.data
        })
    }
    
    # Calculate credit score
    credit_score_data = CreditScoringEngine.calculate_credit_score(
        db=db,
        company_id=company_id,
        financial_data=financial_data
    )
    
    # Save to database
    credit_score_record = CreditScore(
        company_id=company_id,
        score=credit_score_data['score'],
        grade=credit_score_data['grade'],
        risk_category=credit_score_data['risk_category'],
        score_breakdown=credit_score_data['breakdown'],
        positive_factors=credit_score_data['strengths'],
        negative_factors=credit_score_data['weaknesses'],
        improvement_suggestions=credit_score_data['improvement_suggestions']
    )
    
    db.add(credit_score_record)
    db.commit()
    
    # Log calculation
    AuditLogger.log_data_access(
        db=db,
        user_id=current_user.id,
        resource_type="credit_score",
        resource_id=company_id
    )
    
    return {
        "company_id": company_id,
        **credit_score_data,
        "calculated_at": datetime.utcnow()
    }


@router.get("/{company_id}/health-score", response_model=FinancialHealthResponse)
async def get_financial_health_score(
    company_id: int,
    language: str = Query("en", regex="^(en|hi)$"),
    include_ai_insights: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive financial health score and insights
    
    Returns overall health score, ratios, cash flow analysis, and AI-generated insights
    """
    # Verify company ownership
    company = db.query(Company).filter(
        Company.id == company_id,
        Company.user_id == current_user.id
    ).first()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Get financial statements
    balance_sheet_stmt = db.query(FinancialStatement).filter(
        FinancialStatement.company_id == company_id,
        FinancialStatement.statement_type == "balance_sheet"
    ).order_by(FinancialStatement.period_end.desc()).first()
    
    pl_stmt = db.query(FinancialStatement).filter(
        FinancialStatement.company_id == company_id,
        FinancialStatement.statement_type == "profit_loss"
    ).order_by(FinancialStatement.period_end.desc()).first()
    
    if not balance_sheet_stmt or not pl_stmt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Financial statements required"
        )
    
    # Calculate ratios
    financial_data = {
        "balance_sheet": balance_sheet_stmt.data,
        "profit_loss": pl_stmt.data
    }
    ratios = FinancialAnalyzer.calculate_all_ratios(financial_data)
    
    # Analyze cash flow
    cash_flow_analysis = FinancialAnalyzer.analyze_cash_flow(db, company_id)
    
    # Calculate health score
    health_score = FinancialAnalyzer.calculate_financial_health_score(ratios, cash_flow_analysis)
    
    # Generate AI insights if requested
    ai_insights = None
    if include_ai_insights and ai_service:
        try:
            company_data = {
                "name": company.name,
                "industry": company.industry.value if hasattr(company.industry, 'value') else company.industry
            }
            ai_insights = ai_service.generate_financial_insights(
                company_data=company_data,
                financial_ratios=ratios,
                cash_flow_analysis=cash_flow_analysis,
                language=language
            )
        except Exception as e:
            # AI insights are optional, don't fail the request
            ai_insights = f"AI insights unavailable: {str(e)}"
    
    # Log access
    AuditLogger.log_data_access(
        db=db,
        user_id=current_user.id,
        resource_type="health_score",
        resource_id=company_id
    )
    
    return {
        "company_id": company_id,
        "overall_score": health_score['total_score'],
        "grade": health_score['grade'],
        "score_breakdown": health_score['breakdown'],
        "ratios": ratios,
        "cash_flow_summary": cash_flow_analysis,
        "ai_insights": ai_insights
    }


@router.get("/{company_id}/cash-flow")
async def analyze_cash_flow(
    company_id: int,
    months: int = Query(12, ge=1, le=36),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze cash flow patterns
    
    Returns operating, investing, and financing cash flows
    """
    # Verify company ownership
    company = db.query(Company).filter(
        Company.id == company_id,
        Company.user_id == current_user.id
    ).first()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Analyze cash flow
    cash_flow_analysis = FinancialAnalyzer.analyze_cash_flow(db, company_id, months)
    
    return {
        "company_id": company_id,
        "analysis_period_months": months,
        **cash_flow_analysis,
        "analyzed_at": datetime.utcnow()
    }
