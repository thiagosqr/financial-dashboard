"""
Data Ingest Agent for processing CSV files with business transactions
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, TypedDict
from datetime import datetime
import operator
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field


class TransactionData(BaseModel):
    """Schema for validated transaction data"""
    date: str = Field(description="Transaction date in YYYY-MM-DD format")
    description: str = Field(description="Transaction description")
    amount: float = Field(description="Transaction amount (positive for income, negative for expenses)")
    category: str = Field(description="Transaction category")
    account: str = Field(description="Account name")


class ProcessedData(BaseModel):
    """Schema for processed financial data"""
    transactions: List[TransactionData] = Field(description="List of processed transactions")
    summary: Dict[str, Any] = Field(description="Summary statistics of the data")
    validation_issues: List[str] = Field(description="List of any validation issues found")


class DataIngestAgent:
    """Agent responsible for ingesting and validating CSV transaction data"""
    
    def __init__(self, openai_api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo", 
            temperature=0,
            api_key=openai_api_key
        )
        self.structured_llm = self.llm.with_structured_output(ProcessedData)
    
    def process_csv_file(self, file_path: str) -> ProcessedData:
        """Process CSV file and return structured data"""
        try:
            # Read CSV file
            df = pd.read_csv(file_path)
            
            # Basic data cleaning and validation
            df = self._clean_data(df)
            
            # Convert to structured format
            transactions = self._convert_to_transactions(df)
            
            # Generate summary
            summary = self._generate_summary(df)
            
            # Validate data
            validation_issues = self._validate_data(df)
            
            return ProcessedData(
                transactions=transactions,
                summary=summary,
                validation_issues=validation_issues
            )
            
        except Exception as e:
            return ProcessedData(
                transactions=[],
                summary={},
                validation_issues=[f"Error processing file: {str(e)}"]
            )
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize the data"""
        # Remove rows with all NaN values
        df = df.dropna(how='all')
        
        # Standardize column names (case insensitive)
        df.columns = df.columns.str.lower().str.strip()
        
        # Map common column names
        column_mapping = {
            'transaction_date': 'date',
            'date': 'date',
            'description': 'description',
            'transaction description': 'description',
            'desc': 'description',
            'amount': 'amount',
            'value': 'amount',
            'net activity': 'amount',
            'category': 'category',
            'type': 'category',
            'account': 'account',
            'account_name': 'account',
            'account id': 'account'
        }
        
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns:
                df = df.rename(columns={old_name: new_name})
        
        return df
    
    def _convert_to_transactions(self, df: pd.DataFrame) -> List[TransactionData]:
        """Convert DataFrame to list of TransactionData objects"""
        transactions = []
        
        for _, row in df.iterrows():
            try:
                # Parse date
                if 'date' in row and pd.notna(row['date']):
                    if isinstance(row['date'], str):
                        date_str = pd.to_datetime(row['date']).strftime('%Y-%m-%d')
                    else:
                        date_str = row['date'].strftime('%Y-%m-%d')
                else:
                    date_str = datetime.now().strftime('%Y-%m-%d')
                
                # Parse amount - handle different formats
                amount = 0.0
                if 'amount' in row and pd.notna(row.get('amount')):
                    amount = float(row['amount'])
                elif 'net activity' in row and pd.notna(row.get('net activity')):
                    amount = float(row['net activity'])
                elif 'debit' in row and 'credit' in row:
                    # Calculate net amount from debit and credit
                    debit = float(row.get('debit', 0)) if pd.notna(row.get('debit')) else 0.0
                    credit = float(row.get('credit', 0)) if pd.notna(row.get('credit')) else 0.0
                    amount = credit - debit  # Credit increases, debit decreases
                else:
                    amount = 0.0
                
                # Parse description
                description = str(row.get('description', 'Unknown')) if pd.notna(row.get('description')) else 'Unknown'
                
                # Parse category
                category = str(row.get('category', 'Uncategorized')) if pd.notna(row.get('category')) else 'Uncategorized'
                
                # Parse account
                account = str(row.get('account', 'Unknown')) if pd.notna(row.get('account')) else 'Unknown'
                
                transaction = TransactionData(
                    date=date_str,
                    description=description,
                    amount=amount,
                    category=category,
                    account=account
                )
                transactions.append(transaction)
                
            except Exception as e:
                print(f"Error processing row: {e}")
                continue
        
        return transactions
    
    def _generate_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate summary statistics"""
        # Calculate total amount based on available columns
        total_amount = 0
        if 'amount' in df.columns:
            total_amount = df['amount'].sum()
        elif 'net activity' in df.columns:
            total_amount = df['net activity'].sum()
        elif 'debit' in df.columns and 'credit' in df.columns:
            total_amount = (df['credit'].fillna(0) - df['debit'].fillna(0)).sum()
        
        summary = {
            'total_transactions': len(df),
            'date_range': {
                'start': df['date'].min() if 'date' in df.columns else None,
                'end': df['date'].max() if 'date' in df.columns else None
            },
            'total_amount': total_amount,
            'categories': df['category'].value_counts().to_dict() if 'category' in df.columns else {},
            'accounts': df['account'].value_counts().to_dict() if 'account' in df.columns else {}
        }
        return summary
    
    def _validate_data(self, df: pd.DataFrame) -> List[str]:
        """Validate data and return list of issues"""
        issues = []
        
        # Check required columns
        required_columns = ['date']
        for col in required_columns:
            if col not in df.columns:
                issues.append(f"Missing required column: {col}")
        
        # Check for amount-related columns (at least one should be present)
        amount_columns = ['amount', 'net activity', 'debit', 'credit']
        has_amount_data = any(col in df.columns for col in amount_columns)
        if not has_amount_data:
            issues.append("No amount-related columns found (need amount, net activity, or debit/credit)")
        
        # Check for missing values in required columns
        if 'date' in df.columns:
            if df['date'].isna().any():
                issues.append("Found missing values in date column")
        
        # Check for invalid amounts in available amount columns
        for col in ['amount', 'net activity', 'debit', 'credit']:
            if col in df.columns:
                if not pd.api.types.is_numeric_dtype(df[col]):
                    issues.append(f"{col} column contains non-numeric values")
        
        return issues
    
    def categorize_transactions(self, transactions: List[TransactionData]) -> List[TransactionData]:
        """Use LLM to categorize transactions intelligently"""
        if not transactions:
            return transactions
        
        # Group transactions by description for batch processing
        description_groups = {}
        for i, transaction in enumerate(transactions):
            desc = transaction.description.lower()
            if desc not in description_groups:
                description_groups[desc] = []
            description_groups[desc].append((i, transaction))
        
        # Process each unique description
        for desc, transaction_list in description_groups.items():
            if len(transaction_list) > 0:
                # Use LLM to categorize
                category = self._categorize_with_llm(desc)
                
                # Update all transactions with this description
                for idx, transaction in transaction_list:
                    transaction.category = category
        
        return transactions
    
    def _categorize_with_llm(self, description: str) -> str:
        """Use LLM to categorize a transaction description"""
        try:
            response = self.llm.invoke([
                SystemMessage(content="""You are a financial categorization expert. 
                Categorize the following transaction description into one of these categories:
                - Revenue/Sales
                - Operating Expenses
                - Cost of Goods Sold
                - Administrative
                - Marketing
                - Utilities
                - Rent
                - Insurance
                - Professional Services
                - Travel
                - Equipment
                - Other
                
                Return only the category name, nothing else."""),
                HumanMessage(content=f"Transaction description: {description}")
            ])
            
            return response.content.strip()
        except:
            return "Other"
