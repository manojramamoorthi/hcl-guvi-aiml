"""
Financial analysis routes
Calculate ratios, assess credit, analyze cash flow
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import sys
import os
import json

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
    
    if not balance_sheet_stmt and not pl_stmt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one financial statement (Balance Sheet or P&L) required for analysis"
        )
    
    # Prepare financial data - handle missing statements with empty dicts
    financial_data = {
        "balance_sheet": balance_sheet_stmt.data if balance_sheet_stmt else {},
        "profit_loss": pl_stmt.data if pl_stmt else {}
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
    
    if not balance_sheet_stmt and not pl_stmt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Financial statements required for credit scoring"
        )
    
    # Prepare financial data
    financial_data = {
        "balance_sheet": balance_sheet_stmt.data if balance_sheet_stmt else {},
        "profit_loss": pl_stmt.data if pl_stmt else {},
        "ratios": FinancialAnalyzer.calculate_all_ratios({
            "balance_sheet": balance_sheet_stmt.data if balance_sheet_stmt else {},
            "profit_loss": pl_stmt.data if pl_stmt else {}
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
    language: str = Query("en", pattern="^(en|hi)$"),
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
    
    if not balance_sheet_stmt and not pl_stmt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one financial statement required for health score"
        )
    
    # Calculate ratios
    financial_data = {
        "balance_sheet": balance_sheet_stmt.data if balance_sheet_stmt else {},
        "profit_loss": pl_stmt.data if pl_stmt else {}
    }
    ratios = FinancialAnalyzer.calculate_all_ratios(financial_data)

    
    # Analyze cash flow
    cash_flow_analysis = FinancialAnalyzer.analyze_cash_flow(db, company_id)
    
    # Calculate health score
    health_score = FinancialAnalyzer.calculate_financial_health_score(ratios, cash_flow_analysis)
    
    # Generate AI insights if requested
    ai_insights = None
    if include_ai_insights and ai_service:
        # Check for existing recent recommendations (last 24 hours)
        recent_rec = db.query(Recommendation).filter(
            Recommendation.company_id == company_id,
            Recommendation.recommendation_type == "financial_health_insight",
            Recommendation.language == language,
            Recommendation.generated_at >= datetime.utcnow() - timedelta(hours=24)
        ).order_by(Recommendation.generated_at.desc()).first()
        
        if recent_rec:
            ai_insights = recent_rec.detailed_insight
        else:
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
                
                # Save as a permanent recommendation
                new_rec = Recommendation(
                    company_id=company_id,
                    recommendation_type="financial_health_insight",
                    title="Financial Health Assessment",
                    description="AI-generated comprehensive analysis of your financial health.",
                    detailed_insight=ai_insights,
                    priority="medium",
                    language=language
                )
                db.add(new_rec)
                db.commit()
                
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
@router.get("/{company_id}/report")
async def get_investor_report(
    company_id: int,
    language: str = Query("en", pattern="^(en|hi)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate an investor-ready financial report
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
    
    # Get latest health score context
    # This might be slow as it recalculates, but ensures accuracy
    health_data = await get_financial_health_score(company_id, language, True, current_user, db)
    
    if not ai_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service not available"
        )
    
    try:
        company_profile = {
            "name": company.name,
            "industry": company.industry.value if hasattr(company.industry, 'value') else company.industry,
            "annual_revenue": company.annual_revenue
        }
        
        report_content = ai_service.generate_investor_report(
            company_data=company_profile,
            financial_summary=health_data['ratios'],
            health_score={
                "total_score": health_data['overall_score'],
                "grade": health_data['grade']
            },
            language=language
        )
        
        # Save report as a recommendation
        report_rec = Recommendation(
            company_id=company_id,
            recommendation_type="investor_report",
            title=f"Investor Report - {datetime.utcnow().strftime('%B %Y')}",
            description="Deep-dive financial report for investors.",
            detailed_insight=report_content,
            priority="high",
            language=language
        )
        db.add(report_rec)
        db.commit()
        
        return {
            "company_id": company_id,
            "report_content": report_content,
            "generated_at": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}"
        )
@router.post("/{company_id}/chat")
async def chat_with_data(
    company_id: int,
    message_data: Dict[str, str],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Chat with AI about company's financial data
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
    
    # Get context (latest financial statements and health score)
    health_data = await get_financial_health_score(company_id, "en", False, current_user, db)
    
    if not ai_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service not available"
        )

    user_message = message_data.get("message", "")
    
    system_prompt = f"""You are a senior financial advisor for SMEs. 
    You have access to the financial health data for '{company.name}' in the {company.industry.value if hasattr(company.industry, 'value') else company.industry} industry.
    
    Context:
    - Health Score: {health_data['overall_score']}/100 ({health_data['grade']})
    - Key Ratios: {json.dumps(health_data['ratios'])}
    - Cash Flow Summary: {json.dumps(health_data['cash_flow_summary'])}
    
    Answer the user's questions accurately, professionally, and clearly. 
    If they ask for recommendations, suggest cost optimization or suitable financial products based on their grade.
    Keep responses concise but insightful."""

    try:
        response = ai_service.generate_completion(system_prompt, user_message)
        
        # Log chat
        AuditLogger.log_event(
            db=db,
            user_id=current_user.id,
            event_type="financial_chat",
            action="message_sent",
            resource_type="company",
            resource_id=company_id
        )
        
        return {"response": response}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat failed: {str(e)}"
        )
