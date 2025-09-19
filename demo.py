#!/usr/bin/env python3
"""
Demo script for the Financial Dashboard Multi-Agent System
This script demonstrates the LangGraph workflow without requiring the web interface.
"""
import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from agents.financial_workflow import FinancialWorkflow

def demo_financial_analysis():
    """Demonstrate the financial analysis workflow"""
    print("🏦 Financial Dashboard Multi-Agent System Demo")
    print("=" * 50)
    print()
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY environment variable is required")
        print("Please set it with: export OPENAI_API_KEY='your-api-key-here'")
        return False
    
    # Initialize the workflow
    print("🤖 Initializing LangGraph workflow...")
    try:
        workflow = FinancialWorkflow(os.getenv("OPENAI_API_KEY"))
        print("✅ Workflow initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize workflow: {e}")
        return False
    
    # Process sample data
    sample_file = Path("data/sample_transactions.csv")
    if not sample_file.exists():
        print(f"❌ Sample data file not found: {sample_file}")
        return False
    
    print(f"📁 Processing sample data: {sample_file}")
    print("⏳ Running multi-agent analysis...")
    print()
    
    try:
        # Process the file
        result = workflow.process_file(str(sample_file))
        
        if "error" in result:
            print(f"❌ Processing failed: {result['error']}")
            return False
        
        # Display results
        print("📊 ANALYSIS RESULTS")
        print("=" * 30)
        print()
        
        # Display tiles
        print("💰 FINANCIAL METRICS (Current vs Previous Month)")
        print("-" * 50)
        
        for metric, data in result["tiles"].items():
            print(f"{metric.upper().replace('_', ' ')}:")
            print(f"  Current:  ${data['current']:,.2f}")
            print(f"  Previous: ${data['previous']:,.2f}")
            print(f"  Change:   ${data['change']:,.2f} ({data['change_percent']:+.1f}%)")
            print()
        
        # Display insights
        print("🧠 AI-GENERATED INSIGHTS")
        print("-" * 30)
        
        for metric, insight in result["insights"].items():
            print(f"{metric.upper().replace('_', ' ')}:")
            print(f"  Analysis: {insight['insight']}")
            print(f"  Trend:    {insight['trend']}")
            print(f"  Recommendation: {insight['recommendation']}")
            print()
        
        # Display summary
        print("📈 SUMMARY")
        print("-" * 20)
        summary = result["summary"]
        print(f"Total Transactions: {summary['total_transactions']}")
        print(f"Current Period: {summary['current_period']}")
        print(f"Previous Period: {summary['previous_period']}")
        print()
        
        # Display time series data preview
        print("📊 TIME SERIES DATA (Last 6 months)")
        print("-" * 40)
        time_series = result["time_series"]
        dates = time_series["dates"][-6:]  # Last 6 months
        
        print("Month    | Revenue  | Expenses | Profit   | Cash Flow")
        print("-" * 50)
        
        for i, date in enumerate(dates):
            idx = len(time_series["dates"]) - 6 + i
            if idx >= 0:
                revenue = time_series["revenue"][idx]
                expenses = time_series["expenses"][idx]
                profit = time_series["profitability"][idx]
                cash_flow = time_series["cash_flow"][idx]
                
                print(f"{date:8} | ${revenue:7,.0f} | ${expenses:7,.0f} | ${profit:7,.0f} | ${cash_flow:8,.0f}")
        
        print()
        print("🎉 Demo completed successfully!")
        print()
        print("To run the full web application:")
        print("1. Start the backend: cd backend && python main.py")
        print("2. Start the frontend: cd frontend && npm start")
        print("3. Open http://localhost:3000 in your browser")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main demo function"""
    success = demo_financial_analysis()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
