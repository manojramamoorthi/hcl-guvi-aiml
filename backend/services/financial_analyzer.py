"""
Financial analysis engine
Calculates key financial ratios, metrics, and trends
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import numpy as np
from sqlalchemy.orm import Session

from database.models import FinancialStatement, Transaction, Company


class FinancialAnalyzer:
    """Core financial analysis service"""
    
    @staticmethod
    def calculate_liquidity_ratios(balance_sheet: Dict) -> Dict[str, float]:
        """
        Calculate liquidity ratios
        
        Returns:
            Dictionary with current_ratio, quick_ratio, cash_ratio
        """
        current_assets = sum(balance_sheet.get("assets", {}).get("current_assets", {}).values())
        current_liabilities = sum(balance_sheet.get("liabilities", {}).get("current_liabilities", {}).values())
        
        # Get cash and cash equivalents
        cash_items = balance_sheet.get("assets", {}).get("current_assets", {})
        cash = sum(v for k, v in cash_items.items() if 'cash' in k.lower() or 'bank' in k.lower())
        
        # Quick assets (excluding inventory)
        inventory = sum(v for k, v in cash_items.items() if 'inventory' in k.lower())
        quick_assets = current_assets - inventory
        
        ratios = {}
        
        # Current Ratio
        ratios['current_ratio'] = current_assets / current_liabilities if current_liabilities > 0 else 0
        
        # Quick Ratio
        ratios['quick_ratio'] = quick_assets / current_liabilities if current_liabilities > 0 else 0
        
        # Cash Ratio
        ratios['cash_ratio'] = cash / current_liabilities if current_liabilities > 0 else 0
        
        return ratios
    
    @staticmethod
    def calculate_profitability_ratios(pl_statement: Dict, balance_sheet: Dict) -> Dict[str, float]:
        """Calculate profitability ratios"""
        total_revenue = pl_statement.get("revenue", {}).get("total_revenue", 0)
        gross_profit = pl_statement.get("profit", {}).get("gross_profit", 0)
        operating_profit = pl_statement.get("profit", {}).get("operating_profit", 0)
        net_profit = pl_statement.get("profit", {}).get("net_profit", 0)
        
        total_assets = balance_sheet.get("assets", {}).get("total_assets", 0)
        total_equity = balance_sheet.get("equity", {}).get("total_equity", 0)
        
        ratios = {}
        
        # Profit Margins
        ratios['gross_profit_margin'] = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
        ratios['operating_profit_margin'] = (operating_profit / total_revenue * 100) if total_revenue > 0 else 0
        ratios['net_profit_margin'] = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        # Return Ratios
        ratios['return_on_assets'] = (net_profit / total_assets * 100) if total_assets > 0 else 0
        ratios['return_on_equity'] = (net_profit / total_equity * 100) if total_equity > 0 else 0
        
        return ratios
    
    @staticmethod
    def calculate_leverage_ratios(balance_sheet: Dict) -> Dict[str, float]:
        """Calculate leverage/solvency ratios"""
        total_assets = balance_sheet.get("assets", {}).get("total_assets", 0)
        total_liabilities = balance_sheet.get("liabilities", {}).get("total_liabilities", 0)
        total_equity = balance_sheet.get("equity", {}).get("total_equity", 0)
        
        ratios = {}
        
        # Debt to Equity
        ratios['debt_to_equity'] = total_liabilities / total_equity if total_equity > 0 else 0
        
        # Debt to Assets
        ratios['debt_to_assets'] = (total_liabilities / total_assets * 100) if total_assets > 0 else 0
        
        # Equity Ratio
        ratios['equity_ratio'] = (total_equity / total_assets * 100) if total_assets > 0 else 0
        
        return ratios
    
    @staticmethod
    def calculate_efficiency_ratios(pl_statement: Dict, balance_sheet: Dict) -> Dict[str, float]:
        """Calculate efficiency/activity ratios"""
        total_revenue = pl_statement.get("revenue", {}).get("total_revenue", 0)
        total_assets = balance_sheet.get("assets", {}).get("total_assets", 0)
        
        # Get specific asset categories
        current_assets = balance_sheet.get("assets", {}).get("current_assets", {})
        receivables = sum(v for k, v in current_assets.items() if 'receivable' in k.lower())
        inventory = sum(v for k, v in current_assets.items() if 'inventory' in k.lower())
        
        ratios = {}
        
        # Asset Turnover
        ratios['asset_turnover'] = total_revenue / total_assets if total_assets > 0 else 0
        
        # Receivables Turnover (assumes 365 days)
        ratios['receivables_turnover'] = total_revenue / receivables if receivables > 0 else 0
        ratios['days_sales_outstanding'] = 365 / ratios['receivables_turnover'] if ratios['receivables_turnover'] > 0 else 0
        
        # Inventory Turnover
        cogs = pl_statement.get("expenses", {}).get("cost_of_goods_sold", 0)
        ratios['inventory_turnover'] = cogs / inventory if inventory > 0 else 0
        ratios['days_inventory_outstanding'] = 365 / ratios['inventory_turnover'] if ratios['inventory_turnover'] > 0 else 0
        
        return ratios
    
    @staticmethod
    def calculate_all_ratios(financial_data: Dict) -> Dict[str, Any]:
        """
        Calculate all financial ratios
        
        Args:
            financial_data: Dictionary with balance_sheet and profit_loss data
            
        Returns:
            Dictionary with all calculated ratios
        """
        balance_sheet = financial_data.get("balance_sheet", {})
        pl_statement = financial_data.get("profit_loss", {})
        
        all_ratios = {
            "liquidity": FinancialAnalyzer.calculate_liquidity_ratios(balance_sheet),
            "profitability": FinancialAnalyzer.calculate_profitability_ratios(pl_statement, balance_sheet),
            "leverage": FinancialAnalyzer.calculate_leverage_ratios(balance_sheet),
            "efficiency": FinancialAnalyzer.calculate_efficiency_ratios(pl_statement, balance_sheet)
        }
        
        return all_ratios
    
    @staticmethod
    def analyze_cash_flow(db: Session, company_id: int, months: int = 12) -> Dict[str, Any]:
        """
        Analyze cash flow patterns
        
        Args:
            db: Database session
            company_id: Company ID
            months: Number of months to analyze
            
        Returns:
            Cash flow analysis with trends and projections
        """
        # Get transactions for the period
        start_date = datetime.utcnow() - timedelta(days=months * 30)
        transactions = db.query(Transaction).filter(
            Transaction.company_id == company_id,
            Transaction.transaction_date >= start_date
        ).order_by(Transaction.transaction_date).all()
        
        if not transactions:
            return {"error": "No transaction data available"}
        
        # Categorize cash flows
        operating_inflows = []
        operating_outflows = []
        investing_outflows = []
        financing_inflows = []
        
        for txn in transactions:
            if txn.category and 'revenue' in txn.category.lower():
                operating_inflows.append(txn.amount)
            elif txn.category and any(kw in txn.category.lower() for kw in ['expense', 'cost', 'salary']):
                operating_outflows.append(abs(txn.amount))
            elif txn.category and any(kw in txn.category.lower() for kw in ['asset', 'equipment', 'investment']):
                investing_outflows.append(abs(txn.amount))
            elif txn.category and any(kw in txn.category.lower() for kw in ['loan', 'equity', 'financing']):
                financing_inflows.append(txn.amount)
        
        analysis = {
            "operating_cash_flow": {
                "inflows": sum(operating_inflows),
                "outflows": sum(operating_outflows),
                "net": sum(operating_inflows) - sum(operating_outflows)
            },
            "investing_cash_flow": {
                "outflows": sum(investing_outflows),
                "net": -sum(investing_outflows)
            },
            "financing_cash_flow": {
                "inflows": sum(financing_inflows),
                "net": sum(financing_inflows)
            }
        }
        
        # Calculate total net cash flow
        analysis["total_net_cash_flow"] = (
            analysis["operating_cash_flow"]["net"] +
            analysis["investing_cash_flow"]["net"] +
            analysis["financing_cash_flow"]["net"]
        )
        
        # Cash burn rate (for companies with negative operating cash flow)
        if analysis["operating_cash_flow"]["net"] < 0:
            monthly_burn = abs(analysis["operating_cash_flow"]["net"]) / months
            analysis["monthly_burn_rate"] = monthly_burn
        
        return analysis
    
    @staticmethod
    def calculate_financial_health_score(ratios: Dict, cash_flow: Dict) -> Dict[str, Any]:
        """
        Calculate overall financial health score (0-100)
        
        Weighted scoring based on:
        - Liquidity: 25%
        - Profitability: 30%
        - Leverage: 20%
        - Efficiency: 15%
        - Cash Flow: 10%
        """
        score_breakdown = {}
        
        # Liquidity Score (25 points)
        current_ratio = ratios.get("liquidity", {}).get("current_ratio", 0)
        if current_ratio >= 2.0:
            liquidity_score = 25
        elif current_ratio >= 1.5:
            liquidity_score = 20
        elif current_ratio >= 1.0:
            liquidity_score = 15
        else:
            liquidity_score = 5
        score_breakdown["liquidity"] = liquidity_score
        
        # Profitability Score (30 points)
        net_margin = ratios.get("profitability", {}).get("net_profit_margin", 0)
        if net_margin >= 20:
            profitability_score = 30
        elif net_margin >= 10:
            profitability_score = 20
        elif net_margin >= 5:
            profitability_score = 15
        elif net_margin > 0:
            profitability_score = 10
        else:
            profitability_score = 0
        score_breakdown["profitability"] = profitability_score
        
        # Leverage Score (20 points) - lower debt is better
        debt_to_equity = ratios.get("leverage", {}).get("debt_to_equity", 0)
        if debt_to_equity <= 0.5:
            leverage_score = 20
        elif debt_to_equity <= 1.0:
            leverage_score = 15
        elif debt_to_equity <= 2.0:
            leverage_score = 10
        else:
            leverage_score = 5
        score_breakdown["leverage"] = leverage_score
        
        # Efficiency Score (15 points)
        asset_turnover = ratios.get("efficiency", {}).get("asset_turnover", 0)
        if asset_turnover >= 2.0:
            efficiency_score = 15
        elif asset_turnover >= 1.0:
            efficiency_score = 10
        else:
            efficiency_score = 5
        score_breakdown["efficiency"] = efficiency_score
        
        # Cash Flow Score (10 points)
        net_cash_flow = cash_flow.get("total_net_cash_flow", 0)
        if net_cash_flow > 0:
            cash_flow_score = 10
        else:
            cash_flow_score = 0
        score_breakdown["cash_flow"] = cash_flow_score
        
        # Total Score
        total_score = sum(score_breakdown.values())
        
        # Grade
        if total_score >= 90:
            grade = "A+"
        elif total_score >= 80:
            grade = "A"
        elif total_score >= 70:
            grade = "B+"
        elif total_score >= 60:
            grade = "B"
        elif total_score >= 50:
            grade = "C+"
        elif total_score >= 40:
            grade = "C"
        else:
            grade = "D"
        
        return {
            "total_score": total_score,
            "grade": grade,
            "breakdown": score_breakdown,
            "max_score": 100
        }
