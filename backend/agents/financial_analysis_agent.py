"""
Financial Analysis Agent for calculating business financial performance using pandas
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, TypedDict, Annotated
from datetime import datetime, timedelta
import operator
from pydantic import BaseModel, Field
from agents.data_ingest_agent import TransactionData


class FinancialMetrics(BaseModel):
    """Schema for financial metrics"""
    revenue: float = Field(description="Total revenue for the period")
    expenses: float = Field(description="Total expenses for the period")
    profitability: float = Field(description="Net profit/loss for the period")
    cash_flow: float = Field(description="Net cash flow for the period")
    period: str = Field(description="Period being analyzed (e.g., '2024-01')")
    revenue_pct_change: float = Field(description="Revenue percentage change from previous period")
    expenses_pct_change: float = Field(description="Expenses percentage change from previous period")
    profitability_pct_change: float = Field(description="Profitability percentage change from previous period")
    cash_flow_pct_change: float = Field(description="Cash flow percentage change from previous period")


class MonthlyComparison(BaseModel):
    """Schema for month-over-month comparison"""
    current_month: FinancialMetrics = Field(description="Current month metrics")
    previous_month: FinancialMetrics = Field(description="Previous month metrics")
    revenue_change: float = Field(description="Revenue change from previous month")
    expenses_change: float = Field(description="Expenses change from previous month")
    profitability_change: float = Field(description="Profitability change from previous month")
    cash_flow_change: float = Field(description="Cash flow change from previous month")


class TimeSeriesData(BaseModel):
    """Schema for time series data"""
    dates: List[str] = Field(description="List of dates in YYYY-MM format")
    revenue: List[float] = Field(description="Revenue values for each month")
    expenses: List[float] = Field(description="Expense values for each month")
    profitability: List[float] = Field(description="Profitability values for each month")
    cash_flow: List[float] = Field(description="Cash flow values for each month")
    revenue_pct_changes: List[float] = Field(description="Revenue percentage changes month-over-month")
    expenses_pct_changes: List[float] = Field(description="Expenses percentage changes month-over-month")
    profitability_pct_changes: List[float] = Field(description="Profitability percentage changes month-over-month")
    cash_flow_pct_changes: List[float] = Field(description="Cash flow percentage changes month-over-month")


class RootCauseFactor(BaseModel):
    """Schema for individual root cause factors"""
    factor_name: str = Field(description="Name of the contributing factor")
    factor_type: str = Field(description="Type of factor (category, description, account, etc.)")
    current_value: float = Field(description="Current period value")
    previous_value: float = Field(description="Previous period value")
    change: float = Field(description="Absolute change")
    change_percent: float = Field(description="Percentage change")
    impact_score: float = Field(description="Impact score (0-100) based on contribution to total change")
    rank: int = Field(description="Ranking by impact (1 = highest impact)")


class RootCauseAnalysis(BaseModel):
    """Schema for root cause analysis results"""
    metric: str = Field(description="Metric being analyzed (Revenue, Expenses, Profitability, Cash Flow)")
    current_period_value: float = Field(description="Current period metric value")
    previous_period_value: float = Field(description="Previous period metric value")
    total_change: float = Field(description="Total change in metric")
    change_percent: float = Field(description="Percentage change")
    trend_direction: str = Field(description="Trend direction (increasing, decreasing, stable)")
    top_contributing_factors: List[RootCauseFactor] = Field(description="Top contributing factors ranked by impact")
    analysis_summary: str = Field(description="Summary of the root cause analysis")
    recommendations: List[str] = Field(description="Actionable recommendations based on analysis")


class ComprehensiveRootCauseAnalysis(BaseModel):
    """Schema for comprehensive root cause analysis across all metrics"""
    revenue_analysis: RootCauseAnalysis = Field(description="Revenue root cause analysis")
    expenses_analysis: RootCauseAnalysis = Field(description="Expenses root cause analysis")
    profitability_analysis: RootCauseAnalysis = Field(description="Profitability root cause analysis")
    cash_flow_analysis: RootCauseAnalysis = Field(description="Cash flow root cause analysis")
    overall_insights: List[str] = Field(description="Overall business insights from the analysis")
    priority_actions: List[str] = Field(description="Priority actions based on all analyses")


class FinancialAnalysisAgent:
    """Agent responsible for financial analysis using pandas calculations"""
    
    def __init__(self):
        self.revenue_categories = ['revenue/sales', 'interest income', 'other income', 'gst collected']
    
    def _transactions_to_dataframe(self, transactions: List[TransactionData]) -> pd.DataFrame:
        """Convert transactions to pandas DataFrame for analysis"""
        data = []
        for t in transactions:
            data.append({
                'date': t.date,
                'description': t.description,
                'amount': t.amount,
                'category': t.category,
                'account': t.account
            })
        
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df['year_month'] = df['date'].dt.to_period('M')
        return df
    
    def calculate_monthly_metrics(self, transactions: List[TransactionData], 
                                target_month: str = None, 
                                previous_month: str = None) -> FinancialMetrics:
        """Calculate financial metrics for a specific month using pandas"""
        if target_month is None:
            target_month = datetime.now().strftime('%Y-%m')
        
        df = self._transactions_to_dataframe(transactions)
        
        # Filter for target month
        target_period = pd.Period(target_month)
        month_df = df[df['year_month'] == target_period]
        
        if month_df.empty:
            return FinancialMetrics(
                revenue=0.0,
                expenses=0.0,
                profitability=0.0,
                cash_flow=0.0,
                period=target_month,
                revenue_pct_change=0.0,
                expenses_pct_change=0.0,
                profitability_pct_change=0.0,
                cash_flow_pct_change=0.0
            )
        
        # Calculate metrics using pandas
        revenue_mask = month_df['category'].str.lower().isin(self.revenue_categories)
        revenue = month_df[revenue_mask]['amount'].sum()
        expenses = month_df[~revenue_mask]['amount'].sum()
        profitability = revenue - expenses
        cash_flow = month_df['amount'].sum()
        
        # Calculate percentage changes if previous month data is available
        revenue_pct_change = 0.0
        expenses_pct_change = 0.0
        profitability_pct_change = 0.0
        cash_flow_pct_change = 0.0
        
        if previous_month:
            prev_period = pd.Period(previous_month)
            prev_month_df = df[df['year_month'] == prev_period]
            
            if not prev_month_df.empty:
                prev_revenue_mask = prev_month_df['category'].str.lower().isin(self.revenue_categories)
                prev_revenue = prev_month_df[prev_revenue_mask]['amount'].sum()
                prev_expenses = prev_month_df[~prev_revenue_mask]['amount'].sum()
                prev_profitability = prev_revenue - prev_expenses
                prev_cash_flow = prev_month_df['amount'].sum()
                
                # Calculate percentage changes
                revenue_pct_change = self._calculate_percentage_change(revenue, prev_revenue)
                expenses_pct_change = self._calculate_percentage_change(expenses, prev_expenses)
                profitability_pct_change = self._calculate_percentage_change(profitability, prev_profitability)
                cash_flow_pct_change = self._calculate_percentage_change(cash_flow, prev_cash_flow)
        
        return FinancialMetrics(
            revenue=revenue,
            expenses=expenses,
            profitability=profitability,
            cash_flow=cash_flow,
            period=target_month,
            revenue_pct_change=revenue_pct_change,
            expenses_pct_change=expenses_pct_change,
            profitability_pct_change=profitability_pct_change,
            cash_flow_pct_change=cash_flow_pct_change
        )
    
    def _calculate_percentage_change(self, current: float, previous: float) -> float:
        """Calculate percentage change between current and previous values"""
        if previous == 0:
            return 0.0 if current == 0 else 100.0
        return ((current - previous) / abs(previous)) * 100
    
    def calculate_month_over_month_comparison(self, transactions: List[TransactionData]) -> MonthlyComparison:
        """Calculate month-over-month comparison using pandas"""
        if not transactions:
            # Return empty comparison if no transactions
            empty_metrics = FinancialMetrics(
                revenue=0.0,
                expenses=0.0,
                profitability=0.0,
                cash_flow=0.0,
                period="unknown",
                revenue_pct_change=0.0,
                expenses_pct_change=0.0,
                profitability_pct_change=0.0,
                cash_flow_pct_change=0.0
            )
            return MonthlyComparison(
                current_month=empty_metrics,
                previous_month=empty_metrics,
                revenue_change=0.0,
                expenses_change=0.0,
                profitability_change=0.0,
                cash_flow_change=0.0
            )
        
        df = self._transactions_to_dataframe(transactions)
        
        # Get available months sorted
        available_months = sorted(df['year_month'].unique())
        
        if len(available_months) < 2:
            # Not enough data for comparison
            current_month = available_months[0].strftime('%Y-%m') if available_months else datetime.now().strftime('%Y-%m')
            current_metrics = self.calculate_monthly_metrics(transactions, current_month)
            previous_metrics = FinancialMetrics(
                revenue=0.0,
                expenses=0.0,
                profitability=0.0,
                cash_flow=0.0,
                period="unknown",
                revenue_pct_change=0.0,
                expenses_pct_change=0.0,
                profitability_pct_change=0.0,
                cash_flow_pct_change=0.0
            )
        else:
            # Get current and previous months
            current_period = available_months[-1]
            previous_period = available_months[-2]
            
            current_month = current_period.strftime('%Y-%m')
            previous_month = previous_period.strftime('%Y-%m')
            
            # Calculate metrics for both months
            current_metrics = self.calculate_monthly_metrics(transactions, current_month, previous_month)
            previous_metrics = self.calculate_monthly_metrics(transactions, previous_month)
        
        # Calculate changes
        revenue_change = current_metrics.revenue - previous_metrics.revenue
        expenses_change = current_metrics.expenses - previous_metrics.expenses
        profitability_change = current_metrics.profitability - previous_metrics.profitability
        cash_flow_change = current_metrics.cash_flow - previous_metrics.cash_flow
        
        return MonthlyComparison(
            current_month=current_metrics,
            previous_month=previous_metrics,
            revenue_change=revenue_change,
            expenses_change=expenses_change,
            profitability_change=profitability_change,
            cash_flow_change=cash_flow_change
        )
    
    def generate_time_series_data(self, transactions: List[TransactionData], 
                                months_back: int = 12) -> TimeSeriesData:
        """Generate time series data for the last N months using pandas"""
        if not transactions:
            return TimeSeriesData(
                dates=[],
                revenue=[],
                expenses=[],
                profitability=[],
                cash_flow=[],
                revenue_pct_changes=[],
                expenses_pct_changes=[],
                profitability_pct_changes=[],
                cash_flow_pct_changes=[]
            )
        
        df = self._transactions_to_dataframe(transactions)
        
        # Get available months and limit to requested number
        available_months = sorted(df['year_month'].unique())
        if len(available_months) > months_back:
            available_months = available_months[-months_back:]
        
        dates = []
        revenue_data = []
        expenses_data = []
        profitability_data = []
        cash_flow_data = []
        revenue_pct_changes = []
        expenses_pct_changes = []
        profitability_pct_changes = []
        cash_flow_pct_changes = []
        
        for i, period in enumerate(available_months):
            month_str = period.strftime('%Y-%m')
            dates.append(month_str)
            
            # Get previous month for percentage calculation
            prev_month = None
            if i > 0:
                prev_month = available_months[i-1].strftime('%Y-%m')
            
            # Calculate metrics for this month
            metrics = self.calculate_monthly_metrics(transactions, month_str, prev_month)
            revenue_data.append(metrics.revenue)
            expenses_data.append(metrics.expenses)
            profitability_data.append(metrics.profitability)
            cash_flow_data.append(metrics.cash_flow)
            
            # Add percentage changes
            revenue_pct_changes.append(metrics.revenue_pct_change)
            expenses_pct_changes.append(metrics.expenses_pct_change)
            profitability_pct_changes.append(metrics.profitability_pct_change)
            cash_flow_pct_changes.append(metrics.cash_flow_pct_change)
        
        return TimeSeriesData(
            dates=dates,
            revenue=revenue_data,
            expenses=expenses_data,
            profitability=profitability_data,
            cash_flow=cash_flow_data,
            revenue_pct_changes=revenue_pct_changes,
            expenses_pct_changes=expenses_pct_changes,
            profitability_pct_changes=profitability_pct_changes,
            cash_flow_pct_changes=cash_flow_pct_changes
        )
    
    def get_current_month_summary(self, transactions: List[TransactionData]) -> Dict[str, Any]:
        """Get current month financial summary with all metrics"""
        comparison = self.calculate_month_over_month_comparison(transactions)
        time_series = self.generate_time_series_data(transactions, months_back=6)
        
        return {
            "current_month": {
                "period": comparison.current_month.period,
                "revenue": {
                    "value": comparison.current_month.revenue,
                    "previous_value": comparison.previous_month.revenue,
                    "change": comparison.revenue_change,
                    "percentage_change": comparison.current_month.revenue_pct_change
                },
                "expenses": {
                    "value": comparison.current_month.expenses,
                    "previous_value": comparison.previous_month.expenses,
                    "change": comparison.expenses_change,
                    "percentage_change": comparison.current_month.expenses_pct_change
                },
                "profitability": {
                    "value": comparison.current_month.profitability,
                    "previous_value": comparison.previous_month.profitability,
                    "change": comparison.profitability_change,
                    "percentage_change": comparison.current_month.profitability_pct_change
                },
                "cash_flow": {
                    "value": comparison.current_month.cash_flow,
                    "previous_value": comparison.previous_month.cash_flow,
                    "change": comparison.cash_flow_change,
                    "percentage_change": comparison.current_month.cash_flow_pct_change
                }
            },
            "time_series": {
                "dates": time_series.dates,
                "revenue": time_series.revenue,
                "expenses": time_series.expenses,
                "profitability": time_series.profitability,
                "cash_flow": time_series.cash_flow,
                "revenue_pct_changes": time_series.revenue_pct_changes,
                "expenses_pct_changes": time_series.expenses_pct_changes,
                "profitability_pct_changes": time_series.profitability_pct_changes,
                "cash_flow_pct_changes": time_series.cash_flow_pct_changes
            }
        }
    
    def categorize_expenses(self, transactions: List[TransactionData]) -> Dict[str, float]:
        """Categorize expenses by category using pandas"""
        df = self._transactions_to_dataframe(transactions)
        
        # Filter for expenses (negative amounts or non-revenue categories)
        expense_mask = ~df['category'].str.lower().isin(self.revenue_categories)
        expense_df = df[expense_mask]
        
        # Group by category and sum amounts
        category_totals = expense_df.groupby('category')['amount'].sum().abs().to_dict()
        
        return category_totals
    
    def identify_top_revenue_sources(self, transactions: List[TransactionData]) -> Dict[str, float]:
        """Identify top revenue sources using pandas"""
        df = self._transactions_to_dataframe(transactions)
        
        # Filter for revenue transactions
        revenue_mask = df['category'].str.lower().isin(self.revenue_categories)
        revenue_df = df[revenue_mask]
        
        # Group by description and sum amounts
        source_totals = revenue_df.groupby('description')['amount'].sum().to_dict()
        
        # Sort by amount and return top 10
        sorted_sources = sorted(source_totals.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_sources[:10])
    
    def get_metric_analysis(self, transactions: List[TransactionData], metric: str) -> Dict[str, Any]:
        """Get detailed analysis for a specific metric (Revenue, Expenses, Profitability, Cash Flow)"""
        comparison = self.calculate_month_over_month_comparison(transactions)
        time_series = self.generate_time_series_data(transactions, months_back=12)
        
        if metric.lower() == "revenue":
            current = comparison.current_month.revenue
            previous = comparison.previous_month.revenue
            change = comparison.revenue_change
            pct_change = comparison.current_month.revenue_pct_change
            time_series_data = time_series.revenue
            pct_changes = time_series.revenue_pct_changes
        elif metric.lower() == "expenses":
            current = comparison.current_month.expenses
            previous = comparison.previous_month.expenses
            change = comparison.expenses_change
            pct_change = comparison.current_month.expenses_pct_change
            time_series_data = time_series.expenses
            pct_changes = time_series.expenses_pct_changes
        elif metric.lower() == "profitability":
            current = comparison.current_month.profitability
            previous = comparison.previous_month.profitability
            change = comparison.profitability_change
            pct_change = comparison.current_month.profitability_pct_change
            time_series_data = time_series.profitability
            pct_changes = time_series.profitability_pct_changes
        elif metric.lower() == "cash_flow":
            current = comparison.current_month.cash_flow
            previous = comparison.previous_month.cash_flow
            change = comparison.cash_flow_change
            pct_change = comparison.current_month.cash_flow_pct_change
            time_series_data = time_series.cash_flow
            pct_changes = time_series.cash_flow_pct_changes
        else:
            raise ValueError(f"Unknown metric: {metric}. Must be one of: Revenue, Expenses, Profitability, Cash Flow")
        
        return {
            "metric": metric,
            "current_month_value": current,
            "previous_month_value": previous,
            "change": change,
            "percentage_change": pct_change,
            "time_series": {
                "dates": time_series.dates,
                "values": time_series_data,
                "percentage_changes": pct_changes
            }
        }
    
    def analyze_root_cause(self, transactions: List[TransactionData], metric: str) -> RootCauseAnalysis:
        """Perform root cause analysis for a specific metric"""
        comparison = self.calculate_month_over_month_comparison(transactions)
        
        # Get current and previous period data
        df = self._transactions_to_dataframe(transactions)
        current_period = pd.Period(comparison.current_month.period)
        previous_period = pd.Period(comparison.previous_month.period)
        
        current_df = df[df['year_month'] == current_period]
        previous_df = df[df['year_month'] == previous_period]
        
        if metric.lower() == "revenue":
            return self._analyze_revenue_root_cause(current_df, previous_df, comparison)
        elif metric.lower() == "expenses":
            return self._analyze_expenses_root_cause(current_df, previous_df, comparison)
        elif metric.lower() == "profitability":
            return self._analyze_profitability_root_cause(current_df, previous_df, comparison)
        elif metric.lower() == "cash_flow" or metric.lower() == "cash flow":
            return self._analyze_cash_flow_root_cause(current_df, previous_df, comparison)
        else:
            raise ValueError(f"Unknown metric: {metric}. Must be one of: Revenue, Expenses, Profitability, Cash Flow")
    
    def _analyze_revenue_root_cause(self, current_df: pd.DataFrame, previous_df: pd.DataFrame, 
                                   comparison: MonthlyComparison) -> RootCauseAnalysis:
        """Analyze root causes for revenue changes"""
        factors = []
        
        # Analyze by category
        current_revenue = current_df[current_df['category'].str.lower().isin(self.revenue_categories)]
        previous_revenue = previous_df[previous_df['category'].str.lower().isin(self.revenue_categories)]
        
        category_factors = self._analyze_by_category(current_revenue, previous_revenue, "category")
        factors.extend(category_factors)
        
        # Analyze by description (top revenue sources)
        desc_factors = self._analyze_by_description(current_revenue, previous_revenue, "description")
        factors.extend(desc_factors)
        
        # Analyze by account
        account_factors = self._analyze_by_category(current_revenue, previous_revenue, "account")
        factors.extend(account_factors)
        
        # Rank factors by impact
        ranked_factors = self._rank_factors_by_impact(factors, comparison.revenue_change)
        
        # Generate analysis summary and recommendations
        summary = self._generate_revenue_analysis_summary(comparison, ranked_factors)
        recommendations = self._generate_revenue_recommendations(ranked_factors)
        
        return RootCauseAnalysis(
            metric="Revenue",
            current_period_value=comparison.current_month.revenue,
            previous_period_value=comparison.previous_month.revenue,
            total_change=comparison.revenue_change,
            change_percent=comparison.current_month.revenue_pct_change,
            trend_direction="increasing" if comparison.revenue_change > 0 else "decreasing" if comparison.revenue_change < 0 else "stable",
            top_contributing_factors=ranked_factors[:5],  # Top 5 factors
            analysis_summary=summary,
            recommendations=recommendations
        )
    
    def _analyze_expenses_root_cause(self, current_df: pd.DataFrame, previous_df: pd.DataFrame, 
                                    comparison: MonthlyComparison) -> RootCauseAnalysis:
        """Analyze root causes for expense changes"""
        factors = []
        
        # Analyze by category (expenses only)
        current_expenses = current_df[~current_df['category'].str.lower().isin(self.revenue_categories)]
        previous_expenses = previous_df[~previous_df['category'].str.lower().isin(self.revenue_categories)]
        
        category_factors = self._analyze_by_category(current_expenses, previous_expenses, "category")
        factors.extend(category_factors)
        
        # Analyze by description (top expense sources)
        desc_factors = self._analyze_by_description(current_expenses, previous_expenses, "description")
        factors.extend(desc_factors)
        
        # Analyze by account
        account_factors = self._analyze_by_category(current_expenses, previous_expenses, "account")
        factors.extend(account_factors)
        
        # Rank factors by impact
        ranked_factors = self._rank_factors_by_impact(factors, comparison.expenses_change)
        
        # Generate analysis summary and recommendations
        summary = self._generate_expenses_analysis_summary(comparison, ranked_factors)
        recommendations = self._generate_expenses_recommendations(ranked_factors)
        
        return RootCauseAnalysis(
            metric="Expenses",
            current_period_value=comparison.current_month.expenses,
            previous_period_value=comparison.previous_month.expenses,
            total_change=comparison.expenses_change,
            change_percent=comparison.current_month.expenses_pct_change,
            trend_direction="increasing" if comparison.expenses_change > 0 else "decreasing" if comparison.expenses_change < 0 else "stable",
            top_contributing_factors=ranked_factors[:5],  # Top 5 factors
            analysis_summary=summary,
            recommendations=recommendations
        )
    
    def _analyze_profitability_root_cause(self, current_df: pd.DataFrame, previous_df: pd.DataFrame, 
                                         comparison: MonthlyComparison) -> RootCauseAnalysis:
        """Analyze root causes for profitability changes"""
        factors = []
        
        # Profitability is derived from revenue - expenses, so analyze both components
        current_revenue = current_df[current_df['category'].str.lower().isin(self.revenue_categories)]
        previous_revenue = previous_df[previous_df['category'].str.lower().isin(self.revenue_categories)]
        current_expenses = current_df[~current_df['category'].str.lower().isin(self.revenue_categories)]
        previous_expenses = previous_df[~previous_df['category'].str.lower().isin(self.revenue_categories)]
        
        # Revenue impact factors
        revenue_factors = self._analyze_by_category(current_revenue, previous_revenue, "category")
        for factor in revenue_factors:
            factor.factor_type = f"Revenue - {factor.factor_type}"
        factors.extend(revenue_factors)
        
        # Expense impact factors (negative impact on profitability)
        expense_factors = self._analyze_by_category(current_expenses, previous_expenses, "category")
        for factor in expense_factors:
            factor.factor_type = f"Expense - {factor.factor_type}"
            factor.change = -factor.change  # Expenses reduce profitability
        factors.extend(expense_factors)
        
        # Rank factors by impact
        ranked_factors = self._rank_factors_by_impact(factors, comparison.profitability_change)
        
        # Generate analysis summary and recommendations
        summary = self._generate_profitability_analysis_summary(comparison, ranked_factors)
        recommendations = self._generate_profitability_recommendations(ranked_factors)
        
        return RootCauseAnalysis(
            metric="Profitability",
            current_period_value=comparison.current_month.profitability,
            previous_period_value=comparison.previous_month.profitability,
            total_change=comparison.profitability_change,
            change_percent=comparison.current_month.profitability_pct_change,
            trend_direction="increasing" if comparison.profitability_change > 0 else "decreasing" if comparison.profitability_change < 0 else "stable",
            top_contributing_factors=ranked_factors[:5],  # Top 5 factors
            analysis_summary=summary,
            recommendations=recommendations
        )
    
    def _analyze_cash_flow_root_cause(self, current_df: pd.DataFrame, previous_df: pd.DataFrame, 
                                     comparison: MonthlyComparison) -> RootCauseAnalysis:
        """Analyze root causes for cash flow changes"""
        factors = []
        
        # Cash flow includes all transactions, so analyze both revenue and expenses
        current_revenue = current_df[current_df['category'].str.lower().isin(self.revenue_categories)]
        previous_revenue = previous_df[previous_df['category'].str.lower().isin(self.revenue_categories)]
        current_expenses = current_df[~current_df['category'].str.lower().isin(self.revenue_categories)]
        previous_expenses = previous_df[~previous_df['category'].str.lower().isin(self.revenue_categories)]
        
        # Revenue impact factors (positive impact on cash flow)
        revenue_factors = self._analyze_by_category(current_revenue, previous_revenue, "category")
        for factor in revenue_factors:
            factor.factor_type = f"Inflow - {factor.factor_type}"
        factors.extend(revenue_factors)
        
        # Expense impact factors (negative impact on cash flow)
        expense_factors = self._analyze_by_category(current_expenses, previous_expenses, "category")
        for factor in expense_factors:
            factor.factor_type = f"Outflow - {factor.factor_type}"
        factors.extend(expense_factors)
        
        # Analyze by account
        account_factors = self._analyze_by_category(current_df, previous_df, "account")
        factors.extend(account_factors)
        
        # Rank factors by impact
        ranked_factors = self._rank_factors_by_impact(factors, comparison.cash_flow_change)
        
        # Generate analysis summary and recommendations
        summary = self._generate_cash_flow_analysis_summary(comparison, ranked_factors)
        recommendations = self._generate_cash_flow_recommendations(ranked_factors)
        
        return RootCauseAnalysis(
            metric="Cash Flow",
            current_period_value=comparison.current_month.cash_flow,
            previous_period_value=comparison.previous_month.cash_flow,
            total_change=comparison.cash_flow_change,
            change_percent=comparison.current_month.cash_flow_pct_change,
            trend_direction="increasing" if comparison.cash_flow_change > 0 else "decreasing" if comparison.cash_flow_change < 0 else "stable",
            top_contributing_factors=ranked_factors[:5],  # Top 5 factors
            analysis_summary=summary,
            recommendations=recommendations
        )
    
    def _analyze_by_category(self, current_df: pd.DataFrame, previous_df: pd.DataFrame, 
                            column: str) -> List[RootCauseFactor]:
        """Analyze factors by a specific column (category, account, etc.)"""
        factors = []
        
        # Get unique values in current period
        current_totals = current_df.groupby(column)['amount'].sum()
        previous_totals = previous_df.groupby(column)['amount'].sum()
        
        # Combine all unique values from both periods
        all_values = set(current_totals.index) | set(previous_totals.index)
        
        for value in all_values:
            current_val = current_totals.get(value, 0.0)
            previous_val = previous_totals.get(value, 0.0)
            change = current_val - previous_val
            
            if abs(change) > 0.01:  # Only include factors with meaningful changes
                change_percent = self._calculate_percentage_change(current_val, previous_val)
                
                factor = RootCauseFactor(
                    factor_name=value,
                    factor_type=column.title(),
                    current_value=current_val,
                    previous_value=previous_val,
                    change=change,
                    change_percent=change_percent,
                    impact_score=0.0,  # Will be calculated later
                    rank=0  # Will be set later
                )
                factors.append(factor)
        
        return factors
    
    def _analyze_by_description(self, current_df: pd.DataFrame, previous_df: pd.DataFrame, 
                               column: str) -> List[RootCauseFactor]:
        """Analyze factors by description (top contributors)"""
        factors = []
        
        # Get top 10 descriptions by amount in current period
        current_top = current_df.groupby(column)['amount'].sum().abs().nlargest(10)
        previous_totals = previous_df.groupby(column)['amount'].sum()
        
        for desc in current_top.index:
            current_val = current_df[current_df[column] == desc]['amount'].sum()
            previous_val = previous_totals.get(desc, 0.0)
            change = current_val - previous_val
            
            if abs(change) > 0.01:  # Only include factors with meaningful changes
                change_percent = self._calculate_percentage_change(current_val, previous_val)
                
                factor = RootCauseFactor(
                    factor_name=desc,
                    factor_type=f"{column.title()} (Top Contributor)",
                    current_value=current_val,
                    previous_value=previous_val,
                    change=change,
                    change_percent=change_percent,
                    impact_score=0.0,  # Will be calculated later
                    rank=0  # Will be set later
                )
                factors.append(factor)
        
        return factors
    
    def _rank_factors_by_impact(self, factors: List[RootCauseFactor], total_change: float) -> List[RootCauseFactor]:
        """Rank factors by their impact on the total change"""
        if abs(total_change) < 0.01:
            return factors
        
        # Calculate impact score for each factor
        for factor in factors:
            # Impact score is the percentage contribution to total change
            factor.impact_score = abs(factor.change / total_change) * 100 if total_change != 0 else 0
        
        # Sort by impact score (descending)
        sorted_factors = sorted(factors, key=lambda x: x.impact_score, reverse=True)
        
        # Set ranks
        for i, factor in enumerate(sorted_factors):
            factor.rank = i + 1
        
        return sorted_factors
    
    def _generate_revenue_analysis_summary(self, comparison: MonthlyComparison, 
                                         factors: List[RootCauseFactor]) -> str:
        """Generate basic analysis summary for revenue (narratives handled by DataStorytellerAgent)"""
        direction = "increased" if comparison.revenue_change > 0 else "decreased" if comparison.revenue_change < 0 else "remained stable"
        
        if not factors:
            return f"Revenue {direction} by {abs(comparison.revenue_change):,.2f} ({abs(comparison.current_month.revenue_pct_change):.1f}%) with no significant contributing factors identified."
        
        top_factor = factors[0]
        summary = f"Revenue {direction} by {abs(comparison.revenue_change):,.2f} ({abs(comparison.current_month.revenue_pct_change):.1f}%). "
        summary += f"Primary driver: {top_factor.factor_name} ({top_factor.factor_type}) with {top_factor.impact_score:.1f}% impact."
        
        if len(factors) > 1:
            secondary_factor = factors[1]
            summary += f" Secondary driver: {secondary_factor.factor_name} ({secondary_factor.impact_score:.1f}% impact)."
        
        return summary
    
    def _generate_expenses_analysis_summary(self, comparison: MonthlyComparison, 
                                          factors: List[RootCauseFactor]) -> str:
        """Generate basic analysis summary for expenses (narratives handled by DataStorytellerAgent)"""
        direction = "increased" if comparison.expenses_change > 0 else "decreased" if comparison.expenses_change < 0 else "remained stable"
        
        if not factors:
            return f"Expenses {direction} by {abs(comparison.expenses_change):,.2f} ({abs(comparison.current_month.expenses_pct_change):.1f}%) with no significant contributing factors identified."
        
        top_factor = factors[0]
        summary = f"Expenses {direction} by {abs(comparison.expenses_change):,.2f} ({abs(comparison.current_month.expenses_pct_change):.1f}%). "
        summary += f"Primary driver: {top_factor.factor_name} ({top_factor.factor_type}) with {top_factor.impact_score:.1f}% impact."
        
        if len(factors) > 1:
            secondary_factor = factors[1]
            summary += f" Secondary driver: {secondary_factor.factor_name} ({secondary_factor.impact_score:.1f}% impact)."
        
        return summary
    
    def _generate_profitability_analysis_summary(self, comparison: MonthlyComparison, 
                                               factors: List[RootCauseFactor]) -> str:
        """Generate basic analysis summary for profitability (narratives handled by DataStorytellerAgent)"""
        direction = "improved" if comparison.profitability_change > 0 else "declined" if comparison.profitability_change < 0 else "remained stable"
        
        if not factors:
            return f"Profitability {direction} by {abs(comparison.profitability_change):,.2f} ({abs(comparison.current_month.profitability_pct_change):.1f}%) with no significant contributing factors identified."
        
        top_factor = factors[0]
        summary = f"Profitability {direction} by {abs(comparison.profitability_change):,.2f} ({abs(comparison.current_month.profitability_pct_change):.1f}%). "
        summary += f"Primary driver: {top_factor.factor_name} ({top_factor.factor_type}) with {top_factor.impact_score:.1f}% impact."
        
        if len(factors) > 1:
            secondary_factor = factors[1]
            summary += f" Secondary driver: {secondary_factor.factor_name} ({secondary_factor.impact_score:.1f}% impact)."
        
        return summary
    
    def _generate_cash_flow_analysis_summary(self, comparison: MonthlyComparison, 
                                           factors: List[RootCauseFactor]) -> str:
        """Generate basic analysis summary for cash flow (narratives handled by DataStorytellerAgent)"""
        direction = "improved" if comparison.cash_flow_change > 0 else "declined" if comparison.cash_flow_change < 0 else "remained stable"
        
        if not factors:
            return f"Cash flow {direction} by {abs(comparison.cash_flow_change):,.2f} ({abs(comparison.current_month.cash_flow_pct_change):.1f}%) with no significant contributing factors identified."
        
        top_factor = factors[0]
        summary = f"Cash flow {direction} by {abs(comparison.cash_flow_change):,.2f} ({abs(comparison.current_month.cash_flow_pct_change):.1f}%). "
        summary += f"Primary driver: {top_factor.factor_name} ({top_factor.factor_type}) with {top_factor.impact_score:.1f}% impact."
        
        if len(factors) > 1:
            secondary_factor = factors[1]
            summary += f" Secondary driver: {secondary_factor.factor_name} ({secondary_factor.impact_score:.1f}% impact)."
        
        return summary
    
    def _generate_revenue_recommendations(self, factors: List[RootCauseFactor]) -> List[str]:
        """Generate basic recommendations for revenue optimization (detailed recommendations handled by DataStorytellerAgent)"""
        recommendations = []
        
        if not factors:
            return ["Monitor revenue streams closely for emerging trends."]
        
        # Basic recommendations based on factors
        positive_factors = [f for f in factors if f.change > 0]
        negative_factors = [f for f in factors if f.change < 0]
        
        if positive_factors:
            recommendations.append("Focus on scaling successful revenue streams.")
        
        if negative_factors:
            recommendations.append("Review underperforming revenue categories.")
        
        return recommendations
    
    def _generate_expenses_recommendations(self, factors: List[RootCauseFactor]) -> List[str]:
        """Generate basic recommendations for expense management (detailed recommendations handled by DataStorytellerAgent)"""
        recommendations = []
        
        if not factors:
            return ["Review expense categories for optimization opportunities."]
        
        # Basic recommendations based on factors
        increasing_factors = [f for f in factors if f.change > 0]
        decreasing_factors = [f for f in factors if f.change < 0]
        
        if increasing_factors:
            recommendations.append("Review increasing expense categories.")
        
        if decreasing_factors:
            recommendations.append("Maintain successful cost reduction strategies.")
        
        return recommendations
    
    def _generate_profitability_recommendations(self, factors: List[RootCauseFactor]) -> List[str]:
        """Generate basic recommendations for profitability improvement (detailed recommendations handled by DataStorytellerAgent)"""
        recommendations = []
        
        if not factors:
            return ["Focus on revenue growth and cost management balance."]
        
        # Basic recommendations based on factors
        revenue_factors = [f for f in factors if f.factor_type.startswith("Revenue")]
        expense_factors = [f for f in factors if f.factor_type.startswith("Expense")]
        
        if revenue_factors:
            recommendations.append("Focus on revenue growth strategies.")
        
        if expense_factors:
            recommendations.append("Implement cost control measures.")
        
        return recommendations
    
    def _generate_cash_flow_recommendations(self, factors: List[RootCauseFactor]) -> List[str]:
        """Generate basic recommendations for cash flow management (detailed recommendations handled by DataStorytellerAgent)"""
        recommendations = []
        
        if not factors:
            return ["Implement cash flow monitoring systems."]
        
        # Basic recommendations based on factors
        inflow_factors = [f for f in factors if f.factor_type.startswith("Inflow")]
        outflow_factors = [f for f in factors if f.factor_type.startswith("Outflow")]
        
        if inflow_factors:
            recommendations.append("Optimize cash inflow processes.")
        
        if outflow_factors:
            recommendations.append("Review cash outflow management.")
        
        return recommendations
    
    def perform_comprehensive_root_cause_analysis(self, transactions: List[TransactionData]) -> ComprehensiveRootCauseAnalysis:
        """Perform comprehensive root cause analysis for all metrics"""
        revenue_analysis = self.analyze_root_cause(transactions, "Revenue")
        expenses_analysis = self.analyze_root_cause(transactions, "Expenses")
        profitability_analysis = self.analyze_root_cause(transactions, "Profitability")
        cash_flow_analysis = self.analyze_root_cause(transactions, "Cash Flow")
        
        # Generate overall insights
        overall_insights = self._generate_overall_insights(
            revenue_analysis, expenses_analysis, profitability_analysis, cash_flow_analysis
        )
        
        # Generate priority actions
        priority_actions = self._generate_priority_actions(
            revenue_analysis, expenses_analysis, profitability_analysis, cash_flow_analysis
        )
        
        return ComprehensiveRootCauseAnalysis(
            revenue_analysis=revenue_analysis,
            expenses_analysis=expenses_analysis,
            profitability_analysis=profitability_analysis,
            cash_flow_analysis=cash_flow_analysis,
            overall_insights=overall_insights,
            priority_actions=priority_actions
        )
    
    def _generate_overall_insights(self, revenue_analysis: RootCauseAnalysis, 
                                  expenses_analysis: RootCauseAnalysis,
                                  profitability_analysis: RootCauseAnalysis,
                                  cash_flow_analysis: RootCauseAnalysis) -> List[str]:
        """Generate overall business insights from all analyses"""
        insights = []
        
        # Trend analysis
        trends = [
            ("Revenue", revenue_analysis.trend_direction, revenue_analysis.change_percent),
            ("Expenses", expenses_analysis.trend_direction, expenses_analysis.change_percent),
            ("Profitability", profitability_analysis.trend_direction, profitability_analysis.change_percent),
            ("Cash Flow", cash_flow_analysis.trend_direction, cash_flow_analysis.change_percent)
        ]
        
        # Identify patterns
        increasing_metrics = [m for m, t, p in trends if t == "increasing"]
        decreasing_metrics = [m for m, t, p in trends if t == "decreasing"]
        
        if len(increasing_metrics) >= 3:
            insights.append(f"Strong positive momentum across multiple metrics: {', '.join(increasing_metrics)}")
        
        if len(decreasing_metrics) >= 3:
            insights.append(f"Multiple metrics showing decline: {', '.join(decreasing_metrics)} - requires immediate attention")
        
        # Cross-metric insights
        if revenue_analysis.trend_direction == "increasing" and expenses_analysis.trend_direction == "increasing":
            if profitability_analysis.trend_direction == "increasing":
                insights.append("Revenue growth is outpacing expense growth, leading to improved profitability")
            else:
                insights.append("Expense growth is outpacing revenue growth, impacting profitability")
        
        if cash_flow_analysis.trend_direction != profitability_analysis.trend_direction:
            insights.append("Cash flow and profitability trends are diverging - review working capital management")
        
        return insights
    
    def _generate_priority_actions(self, revenue_analysis: RootCauseAnalysis, 
                                  expenses_analysis: RootCauseAnalysis,
                                  profitability_analysis: RootCauseAnalysis,
                                  cash_flow_analysis: RootCauseAnalysis) -> List[str]:
        """Generate priority actions based on all analyses"""
        actions = []
        
        # High impact actions based on largest changes
        all_changes = [
            ("Revenue", abs(revenue_analysis.change_percent)),
            ("Expenses", abs(expenses_analysis.change_percent)),
            ("Profitability", abs(profitability_analysis.change_percent)),
            ("Cash Flow", abs(cash_flow_analysis.change_percent))
        ]
        
        # Sort by magnitude of change
        sorted_changes = sorted(all_changes, key=lambda x: x[1], reverse=True)
        
        # Focus on metrics with significant changes (>10%)
        significant_changes = [m for m, p in sorted_changes if p > 10]
        
        if "Profitability" in significant_changes:
            actions.append("Priority: Address profitability challenges immediately")
        
        if "Cash Flow" in significant_changes:
            actions.append("Priority: Implement cash flow management measures")
        
        if "Expenses" in significant_changes and expenses_analysis.trend_direction == "increasing":
            actions.append("Priority: Control expense growth")
        
        if "Revenue" in significant_changes and revenue_analysis.trend_direction == "decreasing":
            actions.append("Priority: Focus on revenue generation")
        
        # Add general actions
        actions.append("Implement regular financial monitoring and reporting")
        actions.append("Develop contingency plans for adverse scenarios")
        
        return actions
