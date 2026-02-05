"""
Credit scoring and creditworthiness evaluation
Multi-factor scoring algorithm
"""
from typing import Dict, List, Any, Tuple
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings
from database.models import Company, Transaction, FinancialStatement, RiskLevel


class CreditScoringEngine:
    """Credit scoring engine for SMEs"""
    
    # Score ranges
    MIN_SCORE = settings.CREDIT_SCORE_MIN  # 300
    MAX_SCORE = settings.CREDIT_SCORE_MAX  # 900
    
    @staticmethod
    def calculate_payment_history_score(db: Session, company_id: int) -> Tuple[int, Dict]:
        """
        Calculate payment history score (max 250 points)
        
        Factors:
        - On-time payments to vendors/suppliers
        - Overdue receivables
        - Payment consistency
        """
        # In a real implementation, this would analyze payment patterns
        # from transaction data and accounts payable/receivable
        
        # For demonstration: analyze transaction regularity
        transactions = db.query(Transaction).filter(
            Transaction.company_id == company_id
        ).order_by(Transaction.transaction_date.desc()).limit(100).all()
        
        if not transactions:
            return 150, {"reason": "Limited payment history"}
        
        # Count overdue/negative patterns
        score = 250
        details = {}
        
        # Check for regular payments (simplified)
        if len(transactions) < 10:
            score -= 50
            details["limited_history"] = "Few transactions recorded"
        
        # In production: check for late payments, defaults, etc.
        # This is a simplified placeholder
        
        return score, details
    
    @staticmethod
    def calculate_credit_utilization_score(financial_data: Dict) -> Tuple[int, Dict]:
        """
        Calculate credit utilization score (max 200 points)
        
        Factors:
        - Debt levels relative to equity
        - Credit line utilization
        - Leverage ratios
        """
        leverage_ratios = financial_data.get("ratios", {}).get("leverage", {})
        debt_to_equity = leverage_ratios.get("debt_to_equity", 0)
        
        score = 200
        details = {}
        
        if debt_to_equity == 0:
            score = 200
            details["status"] = "No debt - excellent"
        elif debt_to_equity < 0.5:
            score = 180
            details["status"] = "Very low debt - excellent"
        elif debt_to_equity < 1.0:
            score = 160
            details["status"] = "Moderate debt - good"
        elif debt_to_equity < 2.0:
            score = 120
            details["status"] = "High debt - concerning"
        else:
            score = 80
            details["status"] = "Very high debt - risky"
        
        details["debt_to_equity_ratio"] = debt_to_equity
        
        return score, details
    
    @staticmethod
    def calculate_liquidity_score(financial_data: Dict) -> Tuple[int, Dict]:
        """
        Calculate liquidity score (max 200 points)
        
        Factors:
        - Current ratio
        - Quick ratio
        - Cash position
        """
        liquidity_ratios = financial_data.get("ratios", {}).get("liquidity", {})
        current_ratio = liquidity_ratios.get("current_ratio", 0)
        quick_ratio = liquidity_ratios.get("quick_ratio", 0)
        
        score = 0
        details = {}
        
        # Current ratio scoring
        if current_ratio >= 2.0:
            score += 100
            details["current_ratio_status"] = "Excellent"
        elif current_ratio >= 1.5:
            score += 80
            details["current_ratio_status"] = "Good"
        elif current_ratio >= 1.0:
            score += 60
            details["current_ratio_status"] = "Adequate"
        else:
            score += 30
            details["current_ratio_status"] = "Weak"
        
        # Quick ratio scoring
        if quick_ratio >= 1.5:
            score += 100
            details["quick_ratio_status"] = "Excellent"
        elif quick_ratio >= 1.0:
            score += 80
            details["quick_ratio_status"] = "Good"
        elif quick_ratio >= 0.75:
            score += 60
            details["quick_ratio_status"] = "Adequate"
        else:
            score += 30
            details["quick_ratio_status"] = "Weak"
        
        details["current_ratio"] = current_ratio
        details["quick_ratio"] = quick_ratio
        
        return min(score, 200), details
    
    @staticmethod
    def calculate_profitability_score(financial_data: Dict) -> Tuple[int, Dict]:
        """
        Calculate profitability score (max 150 points)
        
        Factors:
        - Net profit margin
        - Revenue growth
        - Consistency
        """
        profitability_ratios = financial_data.get("ratios", {}).get("profitability", {})
        net_margin = profitability_ratios.get("net_profit_margin", 0)
        
        score = 0
        details = {}
        
        if net_margin >= 20:
            score = 150
            details["status"] = "Excellent profitability"
        elif net_margin >= 15:
            score = 130
            details["status"] = "Very good profitability"
        elif net_margin >= 10:
            score = 110
            details["status"] = "Good profitability"
        elif net_margin >= 5:
            score = 80
            details["status"] = "Moderate profitability"
        elif net_margin > 0:
            score = 50
            details["status"] = "Low profitability"
        else:
            score = 0
            details["status"] = "Unprofitable"
        
        details["net_profit_margin"] = net_margin
        
        return score, details
    
    @staticmethod
    def calculate_business_stability_score(company: Company) -> Tuple[int, Dict]:
        """
        Calculate business stability score (max 100 points)
        
        Factors:
        - Years in business
        - Industry stability
        - Company size
        """
        score = 0
        details = {}
        
        # Years in business
        if company.founded_date:
            years = (datetime.utcnow() - company.founded_date).days / 365
            if years >= 10:
                score += 50
                details["years_status"] = "Well-established"
            elif years >= 5:
                score += 40
                details["years_status"] = "Established"
            elif years >= 3:
                score += 30
                details["years_status"] = "Growing"
            elif years >= 1:
                score += 20
                details["years_status"] = "Young company"
            else:
                score += 10
                details["years_status"] = "Startup"
            details["years_in_business"] = round(years, 1)
        else:
            score += 20
            details["years_status"] = "Unknown"
        
        # Company size (revenue-based)
        if company.annual_revenue:
            if company.annual_revenue >= 10000000:  # ₹1 Cr+
                score += 50
                details["size_status"] = "Large SME"
            elif company.annual_revenue >= 5000000:  # ₹50 L+
                score += 40
                details["size_status"] = "Medium SME"
            elif company.annual_revenue >= 1000000:  # ₹10 L+
                score += 30
                details["size_status"] = "Small SME"
            else:
                score += 20
                details["size_status"] = "Micro SME"
        else:
            score += 20
        
        return min(score, 100), details
    
    @staticmethod
    def calculate_credit_score(
        db: Session,
        company_id: int,
        financial_data: Dict
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive credit score
        
        Total: 900 points
        - Payment History: 250
        - Credit Utilization: 200
        - Liquidity: 200
        - Profitability: 150
        - Business Stability: 100
        
        Returns:
            Dictionary with score, grade, breakdown, and factors
        """
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise ValueError("Company not found")
        
        # Calculate component scores
        payment_score, payment_details = CreditScoringEngine.calculate_payment_history_score(db, company_id)
        utilization_score, utilization_details = CreditScoringEngine.calculate_credit_utilization_score(financial_data)
        liquidity_score, liquidity_details = CreditScoringEngine.calculate_liquidity_score(financial_data)
        profitability_score, profitability_details = CreditScoringEngine.calculate_profitability_score(financial_data)
        stability_score, stability_details = CreditScoringEngine.calculate_business_stability_score(company)
        
        # Total score
        total_score = (
            payment_score +
            utilization_score +
            liquidity_score +
            profitability_score +
            stability_score
        )
        
        # Ensure within range
        total_score = max(CreditScoringEngine.MIN_SCORE, min(total_score, CreditScoringEngine.MAX_SCORE))
        
        # Determine grade
        grade, risk_category = CreditScoringEngine.get_grade_and_risk(total_score)
        
        # Identify strengths and weaknesses
        component_scores = {
            "payment_history": payment_score / 250 * 100,
            "credit_utilization": utilization_score / 200 * 100,
            "liquidity": liquidity_score / 200 * 100,
            "profitability": profitability_score / 150 * 100,
            "stability": stability_score / 100 * 100
        }
        
        strengths = [k for k, v in component_scores.items() if v >= 80]
        weaknesses = [k for k, v in component_scores.items() if v < 60]
        
        return {
            "score": total_score,
            "grade": grade,
            "risk_category": risk_category,
            "breakdown": {
                "payment_history": {"score": payment_score, "max": 250, "details": payment_details},
                "credit_utilization": {"score": utilization_score, "max": 200, "details": utilization_details},
                "liquidity": {"score": liquidity_score, "max": 200, "details": liquidity_details},
                "profitability": {"score": profitability_score, "max": 150, "details": profitability_details},
                "business_stability": {"score": stability_score, "max": 100, "details": stability_details}
            },
            "strengths": strengths,
            "weaknesses": weaknesses,
            "improvement_suggestions": CreditScoringEngine.generate_improvement_suggestions(weaknesses)
        }
    
    @staticmethod
    def get_grade_and_risk(score: int) -> Tuple[str, str]:
        """Convert score to grade and risk category"""
        if score >= 800:
            return "A+", RiskLevel.LOW.value
        elif score >= 750:
            return "A", RiskLevel.LOW.value
        elif score >= 700:
            return "B+", RiskLevel.LOW.value
        elif score >= 650:
            return "B", RiskLevel.MEDIUM.value
        elif score >= 600:
            return "C+", RiskLevel.MEDIUM.value
        elif score >= 550:
            return "C", RiskLevel.MEDIUM.value
        elif score >= 500:
            return "D+", RiskLevel.HIGH.value
        else:
            return "D", RiskLevel.HIGH.value
    
    @staticmethod
    def generate_improvement_suggestions(weaknesses: List[str]) -> List[str]:
        """Generate improvement suggestions based on weaknesses"""
        suggestions_map = {
            "payment_history": "Maintain consistent payment schedules to vendors and creditors",
            "credit_utilization": "Reduce debt levels or increase equity to improve leverage ratios",
            "liquidity": "Build cash reserves and improve working capital management",
            "profitability": "Focus on increasing profit margins through cost optimization or revenue growth",
            "stability": "Continue building business track record and growing revenue"
        }
        
        return [suggestions_map.get(weakness, f"Improve {weakness}") for weakness in weaknesses]
