#!/usr/bin/env python3
"""
Test script to calculate Free Cash Flow for June 2025
Focuses on Capex (Capital Expenditure) from Plant & Equipment purchases
"""

import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

def load_test_data():
    """Load the synthetic bakery general ledger test data"""
    data_path = "../../data/Synthetic_Bakery_GeneralLedger_test.csv"
    
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Test data file not found: {data_path}")
    
    df = pd.read_csv(data_path)
    df['Date'] = pd.to_datetime(df['Date'])
    
    print(f"✅ Loaded test data: {len(df)} transactions")
    print(f"📅 Date range: {df['Date'].min()} to {df['Date'].max()}")
    return df

def filter_june_2025_data(df):
    """Filter data for June 2025"""
    june_2025 = df[(df['Date'].dt.year == 2025) & (df['Date'].dt.month == 6)]
    
    print(f"📊 June 2025 transactions: {len(june_2025)}")
    if len(june_2025) == 0:
        print("⚠️  No data found for June 2025 in test file")
        print("❌ Test cannot proceed without June 2025 data")
        return None
    
    return june_2025


def calculate_capex_june_2025(df):
    """Calculate Capital Expenditure (Capex) for June 2025"""
    # Filter for all capital asset purchases in June 2025
    capex_categories = ['Plant & Equipment', 'Motor Vehicle', 'Office furniture and equipment']
    capex_transactions = df[
        (df['Category'].isin(capex_categories)) & 
        (df['Debit'] > 0)  # Only actual purchases (debits)
    ]
    
    total_capex = capex_transactions['Debit'].sum()
    capex_count = len(capex_transactions)
    
    print(f"\n🏭 CAPEX Analysis for June 2025:")
    print(f"   Capital asset purchases: {capex_count}")
    print(f"   Total Capex: ${total_capex:,.2f}")
    
    if len(capex_transactions) > 0:
        print(f"\n📋 Capex Details:")
        for _, row in capex_transactions.iterrows():
            print(f"   • {row['Date'].strftime('%Y-%m-%d')}: {row['Transaction description']}")
            print(f"     Amount: ${row['Debit']:,.2f} (Tax: ${row['Tax Amount']:,.2f})")
    
    return total_capex, capex_transactions

def calculate_operating_cash_flow_june_2025(df):
    """Calculate Operating Cash Flow for June 2025"""
    # Revenue (credit transactions to income accounts)
    revenue_accounts = ['Interest Income', 'Other Income']
    revenue = df[df['Category'].isin(revenue_accounts) & (df['Credit'] > 0)]['Credit'].sum()
    
    # Operating expenses (debit transactions to expense accounts)
    expense_accounts = [cat for cat in df['Category'].unique() 
                       if 'Expenses' in cat or 'Fees' in cat]
    operating_expenses = df[df['Category'].isin(expense_accounts) & (df['Debit'] > 0)]['Debit'].sum()
    
    # Net operating cash flow
    operating_cash_flow = revenue - operating_expenses
    
    print(f"\n💰 Operating Cash Flow Analysis for June 2025:")
    print(f"   Revenue: ${revenue:,.2f}")
    print(f"   Operating Expenses: ${operating_expenses:,.2f}")
    print(f"   Operating Cash Flow: ${operating_cash_flow:,.2f}")
    
    return operating_cash_flow

def calculate_free_cash_flow_june_2025(df):
    """Calculate Free Cash Flow for June 2025"""
    operating_cash_flow = calculate_operating_cash_flow_june_2025(df)
    capex, capex_details = calculate_capex_june_2025(df)
    
    free_cash_flow = operating_cash_flow - capex
    
    print(f"\n🎯 FREE CASH FLOW CALCULATION for June 2025:")
    print(f"   Operating Cash Flow: ${operating_cash_flow:,.2f}")
    print(f"   Capital Expenditure: ${capex:,.2f}")
    print(f"   FREE CASH FLOW: ${free_cash_flow:,.2f}")
    
    if free_cash_flow > 0:
        print(f"   ✅ Positive FCF: Company generated ${free_cash_flow:,.2f} in free cash")
    else:
        print(f"   ⚠️  Negative FCF: Company used ${abs(free_cash_flow):,.2f} more than generated")
    
    return free_cash_flow

def run_free_cash_flow_test():
    """Main test function"""
    print("🚀 FREE CASH FLOW TEST - June 2025")
    print("=" * 50)
    
    try:
        # Load test data
        df = load_test_data()
        
        # Filter for June 2025
        june_2025_data = filter_june_2025_data(df)
        
        if june_2025_data is None:
            print("❌ TEST FAILED: No June 2025 data available in test file")
            return None
        
        # Calculate Free Cash Flow
        fcf = calculate_free_cash_flow_june_2025(june_2025_data)
        
        print(f"\n✅ TEST COMPLETED SUCCESSFULLY")
        print(f"📊 Final Result: Free Cash Flow for June 2025 = ${fcf:,.2f}")
        
        return fcf
        
    except Exception as e:
        print(f"❌ TEST FAILED: {str(e)}")
        return None

if __name__ == "__main__":
    result = run_free_cash_flow_test()
    
    if result is not None:
        print(f"\n🎉 Test passed! Free Cash Flow calculated: ${result:,.2f}")
        sys.exit(0)
    else:
        print(f"\n💥 Test failed!")
        sys.exit(1)
