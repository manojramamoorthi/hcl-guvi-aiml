"""
Document upload routes
Upload and parse financial documents
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import get_db
from database.models import Company, User, FinancialStatement, Transaction
from security import get_current_user
from services.parsers import DocumentParser, FinancialStatementParser
from config import settings
from security.audit_logger import AuditLogger
from services.ai_service import ai_service

router = APIRouter(prefix="/upload")


class UploadResponse(BaseModel):
    message: str
    file_name: str
    file_type: str
    status: str
    data_summary: Optional[Dict[str, Any]] = None


@router.post("/{company_id}/financial-statement", response_model=UploadResponse)
async def upload_financial_statement(
    company_id: int,
    statement_type: str,  # balance_sheet, profit_loss, cash_flow
    period_start: datetime,
    period_end: datetime,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload financial statement (CSV, XLSX, or PDF)
    
    Parses the document and stores structured financial data
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
    
    # Validate file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Supported: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # Read file content
    file_content = await file.read()
    
    # Check file size
    if len(file_content) > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds {settings.MAX_FILE_SIZE_MB}MB limit"
        )
    
    # Parse file based on type
    try:
        structured_data = False
        if file_ext == '.csv':
            df = DocumentParser.parse_csv(file_content)
            if statement_type == 'balance_sheet':
                parsed_data = FinancialStatementParser.parse_balance_sheet(df)
                structured_data = bool(parsed_data.get("assets", {}).get("current_assets"))
            elif statement_type == 'profit_loss':
                parsed_data = FinancialStatementParser.parse_profit_loss(df)
                structured_data = bool(parsed_data.get("revenue", {}).get("items"))
            else:
                parsed_data = {"raw_data": df.to_dict()}
                
        elif file_ext in ['.xlsx', '.xls']:
            sheets = DocumentParser.parse_excel(file_content)
            first_sheet = list(sheets.values())[0]
            if statement_type == 'balance_sheet':
                parsed_data = FinancialStatementParser.parse_balance_sheet(first_sheet)
                structured_data = bool(parsed_data.get("assets", {}).get("current_assets"))
            elif statement_type == 'profit_loss':
                parsed_data = FinancialStatementParser.parse_profit_loss(first_sheet)
                structured_data = bool(parsed_data.get("revenue", {}).get("items"))
            else:
                parsed_data = {"raw_data": first_sheet.to_dict()}
                
        elif file_ext == '.pdf':
            pdf_data = DocumentParser.parse_pdf(file_content)
            if pdf_data['tables']:
                first_table = pdf_data['tables'][0]
                if statement_type == 'balance_sheet':
                    parsed_data = FinancialStatementParser.parse_balance_sheet(first_table)
                    structured_data = bool(parsed_data.get("assets", {}).get("current_assets"))
                elif statement_type == 'profit_loss':
                    parsed_data = FinancialStatementParser.parse_profit_loss(first_table)
                    structured_data = bool(parsed_data.get("revenue", {}).get("items"))
                else:
                    parsed_data = {"raw_data": first_table.to_dict()}
            else:
                parsed_data = {"text": pdf_data['text']}
        else:
            raise ValueError("Unsupported file type")
        
        # AI Fallback: If rule-based parsing failed to get structured data, use AI
        if not structured_data and ai_service:
            from services.ai_service import ai_service
            import json
            
            # Prepare text for AI
            if file_ext == '.pdf':
                text_to_parse = pdf_data['text'][:4000] # Limit to first 4k chars
            else:
                # For CSV/Excel, just take the first few rows as string
                text_to_parse = df.head(50).to_string() if 'df' in locals() else ""
            
            system_prompt = f"You are a financial data extractor. Extract {statement_type} items from the provided text into structured JSON."
            user_prompt = f"Extract {statement_type} data from this text:\n\n{text_to_parse}\n\nReturn ONLY a JSON object that fits the application's {statement_type} structure."
            
            try:
                ai_extracted = ai_service.generate_completion(system_prompt, user_prompt)
                # Simple cleanup of markdown blocks
                if "```json" in ai_extracted:
                    ai_extracted = ai_extracted.split("```json")[1].split("```")[0].strip()
                elif "```" in ai_extracted:
                    ai_extracted = ai_extracted.split("```")[1].split("```")[0].strip()
                
                new_data = json.loads(ai_extracted)
                if new_data:
                    parsed_data = new_data
            except Exception as ai_e:
                print(f"AI parsing failed: {str(ai_e)}")
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to parse file: {str(e)}"
        )
    
    # Save to database
    financial_statement = FinancialStatement(
        company_id=company_id,
        statement_type=statement_type,
        period_start=period_start,
        period_end=period_end,
        data=parsed_data,
        total_assets=parsed_data.get("assets", {}).get("total_assets", 0) if statement_type == 'balance_sheet' else None,
        total_liabilities=parsed_data.get("liabilities", {}).get("total_liabilities", 0) if statement_type == 'balance_sheet' else None,
        total_equity=parsed_data.get("equity", {}).get("total_equity", 0) if statement_type == 'balance_sheet' else None,
        total_revenue=parsed_data.get("revenue", {}).get("total_revenue", 0) if statement_type == 'profit_loss' else None,
        total_expenses=parsed_data.get("expenses", {}).get("total_expenses", 0) if statement_type == 'profit_loss' else None,
        net_profit=parsed_data.get("profit", {}).get("net_profit", 0) if statement_type == 'profit_loss' else None,
        source="uploaded",
        uploaded_file=file.filename
    )

    
    db.add(financial_statement)
    db.commit()
    db.refresh(financial_statement)
    
    # Log upload
    AuditLogger.log_data_modification(
        db=db,
        user_id=current_user.id,
        resource_type="financial_statement",
        resource_id=financial_statement.id,
        action="create"
    )
    
    return {
        "message": "Financial statement uploaded and parsed successfully",
        "file_name": file.filename,
        "file_type": file_ext,
        "status": "success",
        "data_summary": {
            "statement_type": statement_type,
            "period": f"{period_start.date()} to {period_end.date()}",
            "total_assets": financial_statement.total_assets,
            "total_liabilities": financial_statement.total_liabilities,
            "total_revenue": financial_statement.total_revenue,
            "net_profit": financial_statement.net_profit,
            "records_parsed": len(parsed_data) if isinstance(parsed_data, dict) else 0
        }
    }


@router.post("/{company_id}/transactions", response_model=UploadResponse)
async def upload_transactions(
    company_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload transaction list (CSV or XLSX)
    
    Parses transactions and stores them in the database
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
    
    # Validate file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ['.csv', '.xlsx', '.xls']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV and Excel files supported for transactions"
        )
    
    # Read file content
    file_content = await file.read()
    
    # Parse file
    try:
        if file_ext == '.csv':
            df = DocumentParser.parse_csv(file_content)
        else:
            sheets = DocumentParser.parse_excel(file_content)
            df = list(sheets.values())[0]
        
        # Parse transactions
        transactions_data = FinancialStatementParser.parse_transactions(df)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to parse transactions: {str(e)}"
        )
    
    # Save transactions to database
    transaction_objects = []
    for txn_data in transactions_data:
        transaction = Transaction(
            company_id=company_id,
            transaction_date=txn_data.get('date', datetime.utcnow()),
            description=txn_data.get('description', ''),
            amount=txn_data.get('amount', 0),
            category=txn_data.get('category'),
            debit_credit=txn_data.get('type', 'debit'),
            source="uploaded"
        )
        transaction_objects.append(transaction)
    
    db.add_all(transaction_objects)
    db.commit()
    
    # Log upload
    AuditLogger.log_data_modification(
        db=db,
        user_id=current_user.id,
        resource_type="transaction",
        resource_id=company_id,
        action="bulk_create",
        changes={"count": len(transaction_objects)}
    )
    
    return {
        "message": "Transactions uploaded successfully",
        "file_name": file.filename,
        "file_type": file_ext,
        "status": "success",
        "data_summary": {
            "transactions_count": len(transaction_objects),
            "total_amount": sum(t.amount for t in transaction_objects)
        }
    }
