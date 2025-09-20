#!/usr/bin/env python3
"""
Test script for Free Cash Flow implementation
"""
import sys
import os
sys.path.append('backend')

from agents.financial_analysis_agent import FinancialAnalysisAgent
from agents.data_ingest_agent import TransactionData
from datetime import datetime

def test_free_cash_flow():
    """Test the free cash flow calculation"""
    print("🧪 Testing Free Cash Flow Implementation")
    print("=" * 50)
    
    # Create test data
    transactions = [
        # Revenue transactions (positive)
        TransactionData(
            date="2024-01-15",
            description="Product sales",
            amount=5000.0,
            category="revenue/sales",
            account="Bank Account"
        ),
        TransactionData(
            date="2024-01-20",
            description="Service income",
            amount=3000.0,
            category="revenue/sales", 
            account="Bank Account"
        ),
        
        # Operating expenses (negative)
        TransactionData(
            date="2024-01-10",
            description="Office rent",
            amount=-1200.0,
            category="rent expenses",
            account="Bank Account"
        ),
        TransactionData(
            date="2024-01-12",
            description="Utilities",
            amount=-300.0,
            category="utilities",
            account="Bank Account"
        ),
        
        # Capital expenditure (should be identified)
        TransactionData(
            date="2024-01-25",
            description="Purchase of commercial oven",
            amount=-2000.0,
            category="Plant & Equipment",
            account="Bank Account"
        ),
        TransactionData(
            date="2024-01-28",
            description="Office desk purchase",
            amount=-500.0,
            category="Office furniture and equipment",
            account="Bank Account"
        ),
    ]
    
    # Initialize financial analysis agent
    agent = FinancialAnalysisAgent()
    
    # Test capital expenditure identification
    print("🔍 Testing Capital Expenditure Identification:")
    capex_items = []
    for transaction in transactions:
        if agent._is_capital_expenditure(transaction.category, transaction.description):
            capex_items.append(transaction)
            print(f"  ✅ {transaction.description} (${abs(transaction.amount):,.2f})")
    
    expected_capex = 2500.0  # 2000 + 500
    actual_capex = sum(abs(t.amount) for t in capex_items)
    print(f"  Total CapEx: ${actual_capex:,.2f} (Expected: ${expected_capex:,.2f})")
    
    # Test monthly metrics calculation
    print("\n📊 Testing Monthly Metrics Calculation:")
    metrics = agent.calculate_monthly_metrics(transactions, "2024-01")
    
    print(f"  Revenue: ${metrics.revenue:,.2f}")
    print(f"  Expenses: ${metrics.expenses:,.2f}")
    print(f"  Profitability: ${metrics.profitability:,.2f}")
    print(f"  Operating Cash Flow: ${metrics.operating_cash_flow:,.2f}")
    print(f"  Capital Expenditure: ${metrics.capital_expenditure:,.2f}")
    print(f"  Free Cash Flow: ${metrics.free_cash_flow:,.2f}")
    
    # Verify calculations
    expected_revenue = 8000.0  # 5000 + 3000
    expected_operating_cash_flow = 4000.0  # 8000 (inflows) - 4000 (outflows including capex) = 4000
    expected_free_cash_flow = 1500.0  # 4000 - 2500 = 1500
    
    print(f"\n✅ Verification:")
    print(f"  Revenue: ${metrics.revenue:,.2f} == ${expected_revenue:,.2f} ✅" if abs(metrics.revenue - expected_revenue) < 0.01 else f"  Revenue: ${metrics.revenue:,.2f} != ${expected_revenue:,.2f} ❌")
    print(f"  Capital Expenditure: ${metrics.capital_expenditure:,.2f} == ${expected_capex:,.2f} ✅" if abs(metrics.capital_expenditure - expected_capex) < 0.01 else f"  Capital Expenditure: ${metrics.capital_expenditure:,.2f} != ${expected_capex:,.2f} ❌")
    
    # Test Free Cash Flow formula
    calculated_fcf = metrics.operating_cash_flow - metrics.capital_expenditure
    print(f"  Free Cash Flow Formula: ${calculated_fcf:,.2f} == ${metrics.free_cash_flow:,.2f} ✅" if abs(calculated_fcf - metrics.free_cash_flow) < 0.01 else f"  Free Cash Flow Formula: ${calculated_fcf:,.2f} != ${metrics.free_cash_flow:,.2f} ❌")
    
    print(f"\n🎉 Free Cash Flow Implementation Test Complete!")
    return True

if __name__ == "__main__":
    test_free_cash_flow()
