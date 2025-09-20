"""
LangGraph workflow for financial analysis multi-agent system
"""
import os
import logging
from typing import Dict, List, Any, TypedDict, Annotated
import operator
from langgraph.graph import END, START, StateGraph
from langgraph.constants import Send
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from agents.data_ingest_agent import DataIngestAgent, ProcessedData, TransactionData
from agents.cash_flow_agent import CashFlowAnalysisAgent, CashFlowComparison, CashFlowTimeSeriesData, CashFlowRootCauseAnalysis
from agents.revenue_agent import RevenueAnalysisAgent, RevenueComparison, RevenueTimeSeriesData, RevenueRootCauseAnalysis
from agents.expenses_agent import ExpensesAnalysisAgent, ExpensesComparison, ExpensesTimeSeriesData, ExpensesRootCauseAnalysis
from agents.income_agent import IncomeAnalysisAgent, IncomeComparison, IncomeTimeSeriesData, IncomeRootCauseAnalysis
from agents.data_storyteller_agent import DataStorytellerAgent
from agents.advisor_agent import FinancialAdvisorAgent

# Create logger
logger = logging.getLogger(__name__)


class FinancialWorkflowState(TypedDict):
    """State for the financial analysis workflow"""
    file_path: str
    processed_data: ProcessedData
    transactions: List[TransactionData]
    cash_flow_comparison: CashFlowComparison
    revenue_comparison: RevenueComparison
    expenses_comparison: ExpensesComparison
    income_comparison: IncomeComparison
    cash_flow_time_series: CashFlowTimeSeriesData
    revenue_time_series: RevenueTimeSeriesData
    expenses_time_series: ExpensesTimeSeriesData
    income_time_series: IncomeTimeSeriesData
    cash_flow_root_cause: CashFlowRootCauseAnalysis
    revenue_root_cause: RevenueRootCauseAnalysis
    expenses_root_cause: ExpensesRootCauseAnalysis
    income_root_cause: IncomeRootCauseAnalysis
    financial_narratives: Dict[str, Any]
    advisor_recommendations: Dict[str, Any]
    dashboard_data: Dict[str, Any]
    error_message: str


class FinancialWorkflow:
    """LangGraph workflow for financial analysis"""
    
    def __init__(self, openai_api_key: str):
        logger.info("Initializing FinancialWorkflow")
        logger.debug("Creating DataIngestAgent")
        self.data_ingest_agent = DataIngestAgent(openai_api_key)
        
        logger.debug("Creating specialized financial analysis agents")
        self.cash_flow_agent = CashFlowAnalysisAgent()
        self.revenue_agent = RevenueAnalysisAgent()
        self.expenses_agent = ExpensesAnalysisAgent()
        self.income_agent = IncomeAnalysisAgent()
        
        logger.debug("Creating DataStorytellerAgent")
        self.data_storyteller_agent = DataStorytellerAgent(openai_api_key)
        
        logger.debug("Creating FinancialAdvisorAgent")
        self.advisor_agent = FinancialAdvisorAgent(openai_api_key)
        
        logger.debug("Building workflow graph")
        self.workflow = self._build_workflow()
        logger.info("FinancialWorkflow initialized successfully")
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""
        builder = StateGraph(FinancialWorkflowState)
        
        # Add nodes
        builder.add_node("data_ingest", self._data_ingest_node)
        builder.add_node("categorize_transactions", self._categorize_transactions_node)
        builder.add_node("calculate_cash_flow_metrics", self._calculate_cash_flow_metrics_node)
        builder.add_node("calculate_revenue_metrics", self._calculate_revenue_metrics_node)
        builder.add_node("calculate_expenses_metrics", self._calculate_expenses_metrics_node)
        builder.add_node("calculate_income_metrics", self._calculate_income_metrics_node)
        builder.add_node("generate_time_series", self._generate_time_series_node)
        builder.add_node("root_cause_analysis", self._root_cause_analysis_node)
        builder.add_node("generate_narratives", self._generate_narratives_node)
        builder.add_node("generate_recommendations", self._generate_recommendations_node)
        builder.add_node("prepare_dashboard_data", self._prepare_dashboard_data_node)
        builder.add_node("error_handler", self._error_handler_node)
        
        # Add edges
        builder.add_edge(START, "data_ingest")
        builder.add_conditional_edges(
            "data_ingest",
            self._check_data_ingest_success,
            {
                "success": "calculate_cash_flow_metrics",
                "error": "error_handler"
            }
        )
        # Parallel execution of metric calculations
        builder.add_edge("calculate_cash_flow_metrics", "calculate_revenue_metrics")
        builder.add_edge("calculate_revenue_metrics", "calculate_expenses_metrics")
        builder.add_edge("calculate_expenses_metrics", "calculate_income_metrics")
        builder.add_edge("calculate_income_metrics", "generate_time_series")
        builder.add_edge("generate_time_series", "root_cause_analysis")
        builder.add_edge("root_cause_analysis", "generate_narratives")
        builder.add_edge("generate_narratives", "generate_recommendations")
        builder.add_edge("generate_recommendations", "prepare_dashboard_data")
        builder.add_edge("prepare_dashboard_data", END)
        builder.add_edge("error_handler", END)
        
        return builder.compile()
    
    def _data_ingest_node(self, state: FinancialWorkflowState) -> FinancialWorkflowState:
        """Process CSV file and extract transaction data"""
        logger.info(f"Starting data ingestion for file: {state['file_path']}")
        try:
            logger.debug("Processing CSV file with DataIngestAgent")
            processed_data = self.data_ingest_agent.process_csv_file(state["file_path"])
            logger.info(f"Data ingestion successful: {len(processed_data.transactions)} transactions processed")
            logger.debug(f"Validation issues: {len(processed_data.validation_issues)}")
            
            return {
                **state,
                "processed_data": processed_data,
                "transactions": processed_data.transactions,
                "error_message": ""
            }
        except Exception as e:
            logger.error(f"Data ingestion failed: {str(e)}", exc_info=True)
            return {
                **state,
                "error_message": f"Data ingestion failed: {str(e)}"
            }
    
    def _categorize_transactions_node(self, state: FinancialWorkflowState) -> FinancialWorkflowState:
        """Categorize transactions using LLM"""
        try:
            categorized_transactions = self.data_ingest_agent.categorize_transactions(
                state["transactions"]
            )
            
            return {
                **state,
                "transactions": categorized_transactions
            }
        except Exception as e:
            return {
                **state,
                "error_message": f"Transaction categorization failed: {str(e)}"
            }
    
    def _calculate_cash_flow_metrics_node(self, state: FinancialWorkflowState) -> FinancialWorkflowState:
        """Calculate cash flow metrics using specialized agent"""
        try:
            cash_flow_comparison = self.cash_flow_agent.calculate_month_over_month_comparison(
                state["transactions"]
            )
            
            return {
                **state,
                "cash_flow_comparison": cash_flow_comparison
            }
        except Exception as e:
            return {
                **state,
                "error_message": f"Cash flow metrics calculation failed: {str(e)}"
            }
    
    def _calculate_revenue_metrics_node(self, state: FinancialWorkflowState) -> FinancialWorkflowState:
        """Calculate revenue metrics using specialized agent"""
        try:
            revenue_comparison = self.revenue_agent.calculate_month_over_month_comparison(
                state["transactions"]
            )
            
            return {
                **state,
                "revenue_comparison": revenue_comparison
            }
        except Exception as e:
            return {
                **state,
                "error_message": f"Revenue metrics calculation failed: {str(e)}"
            }
    
    def _calculate_expenses_metrics_node(self, state: FinancialWorkflowState) -> FinancialWorkflowState:
        """Calculate expenses metrics using specialized agent"""
        try:
            expenses_comparison = self.expenses_agent.calculate_month_over_month_comparison(
                state["transactions"]
            )
            
            return {
                **state,
                "expenses_comparison": expenses_comparison
            }
        except Exception as e:
            return {
                **state,
                "error_message": f"Expenses metrics calculation failed: {str(e)}"
            }
    
    def _calculate_income_metrics_node(self, state: FinancialWorkflowState) -> FinancialWorkflowState:
        """Calculate income metrics using specialized agent"""
        try:
            income_comparison = self.income_agent.calculate_month_over_month_comparison(
                state["transactions"]
            )
            
            return {
                **state,
                "income_comparison": income_comparison
            }
        except Exception as e:
            return {
                **state,
                "error_message": f"Income metrics calculation failed: {str(e)}"
            }
    
    def _generate_time_series_node(self, state: FinancialWorkflowState) -> FinancialWorkflowState:
        """Generate time series data for charts using specialized agents"""
        try:
            cash_flow_time_series = self.cash_flow_agent.generate_time_series_data(
                state["transactions"]
            )
            revenue_time_series = self.revenue_agent.generate_time_series_data(
                state["transactions"]
            )
            expenses_time_series = self.expenses_agent.generate_time_series_data(
                state["transactions"]
            )
            income_time_series = self.income_agent.generate_time_series_data(
                state["transactions"]
            )
            
            return {
                **state,
                "cash_flow_time_series": cash_flow_time_series,
                "revenue_time_series": revenue_time_series,
                "expenses_time_series": expenses_time_series,
                "income_time_series": income_time_series
            }
        except Exception as e:
            return {
                **state,
                "error_message": f"Time series generation failed: {str(e)}"
            }
    
    def _root_cause_analysis_node(self, state: FinancialWorkflowState) -> FinancialWorkflowState:
        """Perform root cause analysis using specialized agents"""
        try:
            cash_flow_root_cause = self.cash_flow_agent.analyze_cash_flow_root_cause(
                state["transactions"]
            )
            revenue_root_cause = self.revenue_agent.analyze_revenue_root_cause(
                state["transactions"]
            )
            expenses_root_cause = self.expenses_agent.analyze_expenses_root_cause(
                state["transactions"]
            )
            income_root_cause = self.income_agent.analyze_income_root_cause(
                state["transactions"]
            )
            
            return {
                **state,
                "cash_flow_root_cause": cash_flow_root_cause,
                "revenue_root_cause": revenue_root_cause,
                "expenses_root_cause": expenses_root_cause,
                "income_root_cause": income_root_cause
            }
        except Exception as e:
            return {
                **state,
                "error_message": f"Root cause analysis failed: {str(e)}"
            }
    
    def _generate_narratives_node(self, state: FinancialWorkflowState) -> FinancialWorkflowState:
        """Generate financial narratives using the DataStorytellerAgent"""
        logger.info("Starting narrative generation with DataStorytellerAgent")
        try:
            revenue_root_cause = state["revenue_root_cause"]
            expenses_root_cause = state["expenses_root_cause"]
            income_root_cause = state["income_root_cause"]
            cash_flow_root_cause = state["cash_flow_root_cause"]
            logger.debug("Root cause analyses available for narrative generation")
            
            # Generate overall insights and priority actions
            overall_insights = self._generate_overall_insights(
                revenue_root_cause, expenses_root_cause, income_root_cause, cash_flow_root_cause
            )
            priority_actions = self._generate_priority_actions(
                revenue_root_cause, expenses_root_cause, income_root_cause, cash_flow_root_cause
            )
            
            # Generate comprehensive narratives using the DataStorytellerAgent
            logger.debug("Calling DataStorytellerAgent.generate_comprehensive_narrative")
            financial_narratives = self.data_storyteller_agent.generate_comprehensive_narrative(
                revenue_root_cause,
                expenses_root_cause,
                income_root_cause,
                cash_flow_root_cause,
                overall_insights,
                priority_actions
            )
            
            logger.info("Narrative generation completed successfully")
            return {
                **state,
                "financial_narratives": financial_narratives
            }
        except Exception as e:
            logger.error(f"Narrative generation failed: {str(e)}", exc_info=True)
            return {
                **state,
                "error_message": f"Narrative generation failed: {str(e)}"
            }
    
    def _generate_recommendations_node(self, state: FinancialWorkflowState) -> FinancialWorkflowState:
        """Generate intelligent recommendations using the Advisor Agent"""
        try:
            logger.info("Starting recommendation generation with FinancialAdvisorAgent")
            
            # Get the analysis data and narratives
            cash_flow_root_cause = state["cash_flow_root_cause"]
            revenue_root_cause = state["revenue_root_cause"]
            expenses_root_cause = state["expenses_root_cause"]
            income_root_cause = state["income_root_cause"]
            financial_narratives = state["financial_narratives"]
            
            # Prepare analysis data for each metric
            revenue_analysis_data = {
                "current_period_value": revenue_root_cause.current_period_value,
                "previous_period_value": revenue_root_cause.previous_period_value,
                "total_change": revenue_root_cause.total_change,
                "change_percent": revenue_root_cause.change_percent,
                "trend_direction": revenue_root_cause.trend_direction,
                "top_contributing_factors": [
                    {
                        "factor_name": factor.factor_name,
                        "factor_type": factor.factor_type,
                        "change": factor.change,
                        "change_percent": factor.change_percent,
                        "impact_score": factor.impact_score
                    }
                    for factor in revenue_root_cause.top_contributing_factors
                ]
            }
            
            expenses_analysis_data = {
                "current_period_value": expenses_root_cause.current_period_value,
                "previous_period_value": expenses_root_cause.previous_period_value,
                "total_change": expenses_root_cause.total_change,
                "change_percent": expenses_root_cause.change_percent,
                "trend_direction": expenses_root_cause.trend_direction,
                "top_contributing_factors": [
                    {
                        "factor_name": factor.factor_name,
                        "factor_type": factor.factor_type,
                        "change": factor.change,
                        "change_percent": factor.change_percent,
                        "impact_score": factor.impact_score
                    }
                    for factor in expenses_root_cause.top_contributing_factors
                ]
            }
            
            income_analysis_data = {
                "current_period_value": income_root_cause.current_period_value,
                "previous_period_value": income_root_cause.previous_period_value,
                "total_change": income_root_cause.total_change,
                "change_percent": income_root_cause.change_percent,
                "trend_direction": income_root_cause.trend_direction,
                "top_contributing_factors": [
                    {
                        "factor_name": factor.factor_name,
                        "factor_type": factor.factor_type,
                        "change": factor.change,
                        "change_percent": factor.change_percent,
                        "impact_score": factor.impact_score
                    }
                    for factor in income_root_cause.top_contributing_factors
                ]
            }
            
            cash_flow_analysis_data = {
                "current_period_value": cash_flow_root_cause.current_period_value,
                "previous_period_value": cash_flow_root_cause.previous_period_value,
                "total_change": cash_flow_root_cause.total_change,
                "change_percent": cash_flow_root_cause.change_percent,
                "trend_direction": cash_flow_root_cause.trend_direction,
                "top_contributing_factors": [
                    {
                        "factor_name": factor.factor_name,
                        "factor_type": factor.factor_type,
                        "change": factor.change,
                        "change_percent": factor.change_percent,
                        "impact_score": factor.impact_score
                    }
                    for factor in cash_flow_root_cause.top_contributing_factors
                ]
            }
            
            # Generate recommendations using the Advisor Agent
            logger.debug("Calling FinancialAdvisorAgent.generate_bulk_recommendations")
            advisor_recommendations = self.advisor_agent.generate_bulk_recommendations(
                revenue_analysis_data,
                expenses_analysis_data,
                income_analysis_data,
                cash_flow_analysis_data,
                financial_narratives
            )
            
            logger.info("Recommendation generation completed successfully")
            return {
                **state,
                "advisor_recommendations": advisor_recommendations
            }
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {str(e)}", exc_info=True)
            return {
                **state,
                "error_message": f"Recommendation generation failed: {str(e)}"
            }
    
    def _prepare_dashboard_data_node(self, state: FinancialWorkflowState) -> FinancialWorkflowState:
        """Prepare final dashboard data structure"""
        try:
            cash_flow_comparison = state["cash_flow_comparison"]
            revenue_comparison = state["revenue_comparison"]
            expenses_comparison = state["expenses_comparison"]
            income_comparison = state["income_comparison"]
            
            cash_flow_time_series = state["cash_flow_time_series"]
            revenue_time_series = state["revenue_time_series"]
            expenses_time_series = state["expenses_time_series"]
            income_time_series = state["income_time_series"]
            
            cash_flow_root_cause = state["cash_flow_root_cause"]
            revenue_root_cause = state["revenue_root_cause"]
            expenses_root_cause = state["expenses_root_cause"]
            income_root_cause = state["income_root_cause"]
            
            narratives = state["financial_narratives"]
            advisor_recommendations = state.get("advisor_recommendations", {})
            
            dashboard_data = {
                "tiles": {
                    "revenue": {
                        "current": revenue_comparison.current_month.revenue,
                        "previous": revenue_comparison.previous_month.revenue,
                        "change": revenue_comparison.revenue_change,
                        "change_percent": revenue_comparison.current_month.revenue_pct_change
                    },
                    "expenses": {
                        "current": expenses_comparison.current_month.expenses,
                        "previous": expenses_comparison.previous_month.expenses,
                        "change": expenses_comparison.expenses_change,
                        "change_percent": expenses_comparison.current_month.expenses_pct_change
                    },
                    "income": {
                        "current": income_comparison.current_month.net_income,
                        "previous": income_comparison.previous_month.net_income,
                        "change": income_comparison.income_change,
                        "change_percent": income_comparison.current_month.income_pct_change
                    },
                    "free_cash_flow": {
                        "current": cash_flow_comparison.current_month.cash_flow,
                        "previous": cash_flow_comparison.previous_month.cash_flow,
                        "change": cash_flow_comparison.cash_flow_change,
                        "change_percent": cash_flow_comparison.current_month.cash_flow_pct_change
                    }
                },
                "time_series": {
                    "dates": revenue_time_series.dates,
                    "revenue": revenue_time_series.revenue,
                    "expenses": expenses_time_series.expenses,
                    "income": income_time_series.net_income,
                    "free_cash_flow": cash_flow_time_series.cash_flow
                },
                "root_cause_analysis": {
                    "revenue": {
                        "metric": revenue_root_cause.metric,
                        "trend_direction": revenue_root_cause.trend_direction,
                        "analysis_summary": revenue_root_cause.analysis_summary,
                        "top_factors": [
                            {
                                "factor_name": factor.factor_name,
                                "factor_type": factor.factor_type,
                                "change": factor.change,
                                "change_percent": factor.change_percent,
                                "impact_score": factor.impact_score,
                                "rank": factor.rank
                            }
                            for factor in revenue_root_cause.top_contributing_factors
                        ],
                        "recommendations": [advisor_recommendations.get("revenue", {}).get("recommendation", "No recommendations available")]
                    },
                    "expenses": {
                        "metric": expenses_root_cause.metric,
                        "trend_direction": expenses_root_cause.trend_direction,
                        "analysis_summary": expenses_root_cause.analysis_summary,
                        "top_factors": [
                            {
                                "factor_name": factor.factor_name,
                                "factor_type": factor.factor_type,
                                "change": factor.change,
                                "change_percent": factor.change_percent,
                                "impact_score": factor.impact_score,
                                "rank": factor.rank
                            }
                            for factor in expenses_root_cause.top_contributing_factors
                        ],
                        "recommendations": [advisor_recommendations.get("expenses", {}).get("recommendation", "No recommendations available")]
                    },
                    "income": {
                        "metric": income_root_cause.metric,
                        "trend_direction": income_root_cause.trend_direction,
                        "analysis_summary": income_root_cause.analysis_summary,
                        "top_factors": [
                            {
                                "factor_name": factor.factor_name,
                                "factor_type": factor.factor_type,
                                "change": factor.change,
                                "change_percent": factor.change_percent,
                                "impact_score": factor.impact_score,
                                "rank": factor.rank
                            }
                            for factor in income_root_cause.top_contributing_factors
                        ],
                        "recommendations": [advisor_recommendations.get("income", {}).get("recommendation", "No recommendations available")]
                    },
                    "free_cash_flow": {
                        "metric": cash_flow_root_cause.metric,
                        "trend_direction": cash_flow_root_cause.trend_direction,
                        "analysis_summary": cash_flow_root_cause.analysis_summary,
                        "top_factors": [
                            {
                                "factor_name": factor.factor_name,
                                "factor_type": factor.factor_type,
                                "change": factor.change,
                                "change_percent": factor.change_percent,
                                "impact_score": factor.impact_score,
                                "rank": factor.rank
                            }
                            for factor in cash_flow_root_cause.top_contributing_factors
                        ],
                        "recommendations": [advisor_recommendations.get("free_cash_flow", {}).get("recommendation", "No recommendations available")]
                    }
                },
                "insights": {
                    "overall_insights": narratives["overall_insights"],
                    "priority_actions": narratives["priority_actions"],
                    "overall_business_story": narratives["overall_business_story"]
                },
                "narratives": {
                    "revenue": {
                        "narrative": narratives["revenue"].narrative,
                        "key_insights": narratives["revenue"].key_insights,
                        "actionable_recommendations": narratives["revenue"].actionable_recommendations,
                        "business_impact": narratives["revenue"].business_impact
                    },
                    "expenses": {
                        "narrative": narratives["expenses"].narrative,
                        "key_insights": narratives["expenses"].key_insights,
                        "actionable_recommendations": narratives["expenses"].actionable_recommendations,
                        "business_impact": narratives["expenses"].business_impact
                    },
                    "income": {
                        "narrative": narratives["income"].narrative,
                        "key_insights": narratives["income"].key_insights,
                        "actionable_recommendations": narratives["income"].actionable_recommendations,
                        "business_impact": narratives["income"].business_impact
                    },
                    "free_cash_flow": {
                        "narrative": narratives["free_cash_flow"].narrative,
                        "key_insights": narratives["free_cash_flow"].key_insights,
                        "actionable_recommendations": narratives["free_cash_flow"].actionable_recommendations,
                        "business_impact": narratives["free_cash_flow"].business_impact
                    }
                },
                "summary": {
                    "total_transactions": len(state["transactions"]),
                    "current_period": revenue_comparison.current_month.period,
                    "previous_period": revenue_comparison.previous_month.period
                }
            }
            
            return {
                **state,
                "dashboard_data": dashboard_data
            }
        except Exception as e:
            return {
                **state,
                "error_message": f"Dashboard data preparation failed: {str(e)}"
            }
    
    def _error_handler_node(self, state: FinancialWorkflowState) -> FinancialWorkflowState:
        """Handle errors and return error state"""
        return {
            **state,
            "dashboard_data": {
                "error": state.get("error_message", "Unknown error occurred"),
                "tiles": {},
                "time_series": {},
                "insights": {},
                "narratives": {},
                "summary": {}
            }
        }
    
    def _check_data_ingest_success(self, state: FinancialWorkflowState) -> str:
        """Check if data ingestion was successful"""
        if state.get("error_message"):
            return "error"
        return "success"
    
    
    def process_file(self, file_path: str) -> Dict[str, Any]:
        """Process a CSV file and return dashboard data"""
        logger.info(f"Starting file processing workflow for: {file_path}")
        initial_state = {
            "file_path": file_path,
            "processed_data": None,
            "transactions": [],
            "cash_flow_comparison": None,
            "revenue_comparison": None,
            "expenses_comparison": None,
            "income_comparison": None,
            "cash_flow_time_series": None,
            "revenue_time_series": None,
            "expenses_time_series": None,
            "income_time_series": None,
            "cash_flow_root_cause": None,
            "revenue_root_cause": None,
            "expenses_root_cause": None,
            "income_root_cause": None,
            "financial_narratives": None,
            "advisor_recommendations": None,
            "dashboard_data": {},
            "error_message": ""
        }
        
        logger.debug("Invoking workflow with initial state")
        result = self.workflow.invoke(initial_state)
        logger.info("Workflow processing completed")
        
        if "error_message" in result and result["error_message"]:
            logger.error(f"Workflow completed with error: {result['error_message']}")
        else:
            logger.info("Workflow completed successfully")
            
        return result["dashboard_data"]
    
    def _generate_overall_insights(self, revenue_analysis, expenses_analysis, income_analysis, cash_flow_analysis) -> List[str]:
        """Generate overall business insights from all analyses"""
        insights = []
        
        # Trend analysis
        trends = [
            ("Revenue", revenue_analysis.trend_direction, revenue_analysis.change_percent),
            ("Expenses", expenses_analysis.trend_direction, expenses_analysis.change_percent),
            ("Income", income_analysis.trend_direction, income_analysis.change_percent),
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
            if income_analysis.trend_direction == "increasing":
                insights.append("Revenue growth is outpacing expense growth, leading to improved profitability")
            else:
                insights.append("Expense growth is outpacing revenue growth, impacting profitability")
        
        if cash_flow_analysis.trend_direction != income_analysis.trend_direction:
            insights.append("Cash flow and profitability trends are diverging - review working capital management")
        
        return insights
    
    def _generate_priority_actions(self, revenue_analysis, expenses_analysis, income_analysis, cash_flow_analysis) -> List[str]:
        """Generate priority actions based on all analyses"""
        actions = []
        
        # High impact actions based on largest changes
        all_changes = [
            ("Revenue", abs(revenue_analysis.change_percent)),
            ("Expenses", abs(expenses_analysis.change_percent)),
            ("Income", abs(income_analysis.change_percent)),
            ("Cash Flow", abs(cash_flow_analysis.change_percent))
        ]
        
        # Sort by magnitude of change
        sorted_changes = sorted(all_changes, key=lambda x: x[1], reverse=True)
        
        # Focus on metrics with significant changes (>10%)
        significant_changes = [m for m, p in sorted_changes if p > 10]
        
        if "Income" in significant_changes:
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
