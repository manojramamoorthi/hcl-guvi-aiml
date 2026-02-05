"""
Document parsers for CSV, XLSX, and PDF financial statements
"""
import pandas as pd
import PyPDF2
import pdfplumber
from typing import Dict, List, Any, Optional
from io import BytesIO
import re


class DocumentParser:
    """Parser for financial documents"""
    
    @staticmethod
    def parse_csv(file_content: bytes) -> pd.DataFrame:
        """
        Parse CSV file
        
        Args:
            file_content: CSV file bytes
            
        Returns:
            Pandas DataFrame with file data
        """
        try:
            df = pd.read_csv(BytesIO(file_content))
            return df
        except Exception as e:
            raise ValueError(f"Failed to parse CSV: {str(e)}")
    
    @staticmethod
    def parse_excel(file_content: bytes) -> Dict[str, pd.DataFrame]:
        """
        Parse Excel file (supports multiple sheets)
        
        Args:
            file_content: Excel file bytes
            
        Returns:
            Dictionary mapping sheet names to DataFrames
        """
        try:
            excel_file = pd.ExcelFile(BytesIO(file_content))
            sheets = {}
            for sheet_name in excel_file.sheet_names:
                sheets[sheet_name] = excel_file.parse(sheet_name)
            return sheets
        except Exception as e:
            raise ValueError(f"Failed to parse Excel: {str(e)}")
    
    @staticmethod
    def parse_pdf(file_content: bytes) -> Dict[str, Any]:
        """
        Parse PDF file and extract text/tables
        
        Args:
            file_content: PDF file bytes
            
        Returns:
            Dictionary with extracted text and tables
        """
        try:
            result = {
                "text": "",
                "tables": [],
                "metadata": {}
            }
            
            # Extract text using PyPDF2
            pdf_reader = PyPDF2.PdfReader(BytesIO(file_content))
            result["metadata"]["num_pages"] = len(pdf_reader.pages)
            
            for page in pdf_reader.pages:
                result["text"] += page.extract_text() + "\n"
            
            # Extract tables using pdfplumber
            with pdfplumber.open(BytesIO(file_content)) as pdf:
                for page in pdf.pages:
                    tables = page.extract_tables()
                    if tables:
                        for table in tables:
                            # Convert to DataFrame
                            if len(table) > 1:
                                df = pd.DataFrame(table[1:], columns=table[0])
                                result["tables"].append(df)
            
            return result
        except Exception as e:
            raise ValueError(f"Failed to parse PDF: {str(e)}")


class FinancialStatementParser:
    """Parse financial statements and normalize data"""
    
    @staticmethod
    def parse_balance_sheet(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Parse balance sheet from DataFrame
        Attempts to intelligently identify assets, liabilities, equity
        """
        balance_sheet = {
            "assets": {
                "current_assets": {},
                "fixed_assets": {},
                "total_assets": 0
            },
            "liabilities": {
                "current_liabilities": {},
                "long_term_liabilities": {},
                "total_liabilities": 0
            },
            "equity": {
                "items": {},
                "total_equity": 0
            }
        }
        
        # Simple pattern matching for common line items
        # In production, this should be more sophisticated with ML
        for idx, row in df.iterrows():
            if len(row) < 2:
                continue
                
            item_name = str(row.iloc[0]).strip().lower()
            try:
                value = float(str(row.iloc[1]).replace(',', '').replace('₹', '').strip())
            except:
                continue
            
            # Categorize items
            if any(keyword in item_name for keyword in ['cash', 'bank', 'receivable', 'inventory', 'current asset']):
                balance_sheet["assets"]["current_assets"][item_name] = value
            elif any(keyword in item_name for keyword in ['equipment', 'property', 'plant', 'fixed asset', 'machinery']):
                balance_sheet["assets"]["fixed_assets"][item_name] = value
            elif any(keyword in item_name for keyword in ['payable', 'current liabilit', 'short-term']):
                balance_sheet["liabilities"]["current_liabilities"][item_name] = value
            elif any(keyword in item_name for keyword in ['long-term', 'loan', 'debt']):
                balance_sheet["liabilities"]["long_term_liabilities"][item_name] = value
            elif any(keyword in item_name for keyword in ['equity', 'capital', 'retained earnings']):
                balance_sheet["equity"]["items"][item_name] = value
 
        # Calculate totals
        balance_sheet["assets"]["total_assets"] = (
            sum(balance_sheet["assets"]["current_assets"].values()) +
            sum(balance_sheet["assets"]["fixed_assets"].values())
        )
        balance_sheet["liabilities"]["total_liabilities"] = (
            sum(balance_sheet["liabilities"]["current_liabilities"].values()) +
            sum(balance_sheet["liabilities"]["long_term_liabilities"].values())
        )
        balance_sheet["equity"]["total_equity"] = sum(balance_sheet["equity"]["items"].values())
        
        return balance_sheet
    
    @staticmethod
    def parse_profit_loss(df: pd.DataFrame) -> Dict[str, Any]:
        """Parse profit & loss statement"""
        pl_statement = {
            "revenue": {
                "items": {},
                "total_revenue": 0
            },
            "expenses": {
                "cost_of_goods_sold": 0,
                "operating_expenses": {},
                "other_expenses": {},
                "total_expenses": 0
            },
            "profit": {
                "gross_profit": 0,
                "operating_profit": 0,
                "net_profit": 0
            }
        }
        
        for idx, row in df.iterrows():
            if len(row) < 2:
                continue
                
            item_name = str(row.iloc[0]).strip().lower()
            try:
                value = float(str(row.iloc[1]).replace(',', '').replace('₹', '').strip())
            except:
                continue
            
            # Categorize items
            if any(keyword in item_name for keyword in ['revenue', 'sales', 'income']):
                pl_statement["revenue"]["items"][item_name] = value
            elif any(keyword in item_name for keyword in ['cost of goods', 'cogs']):
                pl_statement["expenses"]["cost_of_goods_sold"] += value
            elif any(keyword in item_name for keyword in ['salary', 'wage', 'rent', 'utilities', 'marketing', 'admin']):
                pl_statement["expenses"]["operating_expenses"][item_name] = value
            elif 'expense' in item_name or 'cost' in item_name:
                pl_statement["expenses"]["other_expenses"][item_name] = value
        
        # Calculate totals
        pl_statement["revenue"]["total_revenue"] = sum(pl_statement["revenue"]["items"].values())
        pl_statement["expenses"]["total_expenses"] = (
            pl_statement["expenses"]["cost_of_goods_sold"] +
            sum(pl_statement["expenses"]["operating_expenses"].values()) +
            sum(pl_statement["expenses"]["other_expenses"].values())
        )
        pl_statement["profit"]["gross_profit"] = (
            pl_statement["revenue"]["total_revenue"] - 
            pl_statement["expenses"]["cost_of_goods_sold"]
        )
        pl_statement["profit"]["operating_profit"] = (
            pl_statement["profit"]["gross_profit"] -
            sum(pl_statement["expenses"]["operating_expenses"].values())
        )
        pl_statement["profit"]["net_profit"] = (
            pl_statement["revenue"]["total_revenue"] -
            pl_statement["expenses"]["total_expenses"]
        )
        
        return pl_statement
    
    @staticmethod
    def parse_transactions(df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Parse transaction list from DataFrame
        
        Expected columns: date, description, amount, category (optional)
        """
        transactions = []
        
        # Normalize column names
        df.columns = [col.strip().lower() for col in df.columns]
        
        for idx, row in df.iterrows():
            transaction = {}
            
            # Extract date
            if 'date' in df.columns:
                transaction['date'] = pd.to_datetime(row['date'])
            
            # Extract description
            if 'description' in df.columns or 'particulars' in df.columns:
                desc_col = 'description' if 'description' in df.columns else 'particulars'
                transaction['description'] = str(row[desc_col])
            
            # Extract amount
            amount_col = None
            for col in ['amount', 'value', 'debit', 'credit']:
                if col in df.columns:
                    amount_col = col
                    break
            
            if amount_col:
                try:
                    amount = float(str(row[amount_col]).replace(',', '').replace('₹', '').strip())
                    transaction['amount'] = amount
                except:
                    continue
            
            # Extract category if available
            if 'category' in df.columns:
                transaction['category'] = str(row['category'])
            
            # Determine debit/credit
            if 'type' in df.columns:
                transaction['type'] = str(row['type']).lower()
            elif 'debit' in df.columns and 'credit' in df.columns:
                transaction['type'] = 'debit' if pd.notna(row['debit']) else 'credit'
            
            if transaction:
                transactions.append(transaction)
        
        return transactions
