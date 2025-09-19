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
from agents.financial_analysis_agent import (
    FinancialAnalysisAgent, 
    MonthlyComparison, 
    TimeSeriesData,
    ComprehensiveRootCauseAnalysis
)
from agents.data_storyteller_agent import DataStorytellerAgent

# Create logger
logger = logging.getLogger(__name__)


class FinancialWorkflowState(TypedDict):
    """State for the financial analysis workflow"""
    file_path: str
    processed_data: ProcessedData
    transactions: List[TransactionData]
    monthly_comparison: MonthlyComparison
    time_series_data: TimeSeriesData
    root_cause_analysis: ComprehensiveRootCauseAnalysis
    financial_narratives: Dict[str, Any]
    dashboard_data: Dict[str, Any]
    error_message: str


class FinancialWorkflow:
    """LangGraph workflow for financial analysis"""
    
    def __init__(self, openai_api_key: str):
        logger.info("Initializing FinancialWorkflow")
        logger.debug("Creating DataIngestAgent")
        self.data_ingest_agent = DataIngestAgent(openai_api_key)
        
        logger.debug("Creating FinancialAnalysisAgent")
        self.financial_analysis_agent = FinancialAnalysisAgent()
        
        logger.debug("Creating DataStorytellerAgent")
        self.data_storyteller_agent = DataStorytellerAgent(openai_api_key)
        
        logger.debug("Building workflow graph")
        self.workflow = self._build_workflow()
        logger.info("FinancialWorkflow initialized successfully")
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""
        builder = StateGraph(FinancialWorkflowState)
        
        # Add nodes
        builder.add_node("data_ingest", self._data_ingest_node)
        builder.add_node("categorize_transactions", self._categorize_transactions_node)
        builder.add_node("calculate_metrics", self._calculate_metrics_node)
        builder.add_node("generate_time_series", self._generate_time_series_node)
        builder.add_node("root_cause_analysis", self._root_cause_analysis_node)
        builder.add_node("generate_narratives", self._generate_narratives_node)
        builder.add_node("prepare_dashboard_data", self._prepare_dashboard_data_node)
        builder.add_node("error_handler", self._error_handler_node)
        
        # Add edges
        builder.add_edge(START, "data_ingest")
        builder.add_conditional_edges(
            "data_ingest",
            self._check_data_ingest_success,
            {
                "success": "calculate_metrics",
                "error": "error_handler"
            }
        )
        builder.add_edge("calculate_metrics", "generate_time_series")
        builder.add_edge("generate_time_series", "root_cause_analysis")
        builder.add_edge("root_cause_analysis", "generate_narratives")
        builder.add_edge("generate_narratives", "prepare_dashboard_data")
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
    
    def _calculate_metrics_node(self, state: FinancialWorkflowState) -> FinancialWorkflowState:
        """Calculate monthly financial metrics and comparison"""
        try:
            monthly_comparison = self.financial_analysis_agent.calculate_month_over_month_comparison(
                state["transactions"]
            )
            
            return {
                **state,
                "monthly_comparison": monthly_comparison
            }
        except Exception as e:
            return {
                **state,
                "error_message": f"Metrics calculation failed: {str(e)}"
            }
    
    def _generate_time_series_node(self, state: FinancialWorkflowState) -> FinancialWorkflowState:
        """Generate time series data for charts"""
        try:
            time_series_data = self.financial_analysis_agent.generate_time_series_data(
                state["transactions"]
            )
            
            return {
                **state,
                "time_series_data": time_series_data
            }
        except Exception as e:
            return {
                **state,
                "error_message": f"Time series generation failed: {str(e)}"
            }
    
    def _root_cause_analysis_node(self, state: FinancialWorkflowState) -> FinancialWorkflowState:
        """Perform comprehensive root cause analysis for all metrics"""
        try:
            root_cause_analysis = self.financial_analysis_agent.perform_comprehensive_root_cause_analysis(
                state["transactions"]
            )
            
            return {
                **state,
                "root_cause_analysis": root_cause_analysis
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
            root_cause_analysis = state["root_cause_analysis"]
            logger.debug("Root cause analysis available for narrative generation")
            
            # Generate comprehensive narratives using the DataStorytellerAgent
            logger.debug("Calling DataStorytellerAgent.generate_comprehensive_narrative")
            financial_narratives = self.data_storyteller_agent.generate_comprehensive_narrative(
                root_cause_analysis.revenue_analysis,
                root_cause_analysis.expenses_analysis,
                root_cause_analysis.profitability_analysis,
                root_cause_analysis.cash_flow_analysis,
                root_cause_analysis.overall_insights,
                root_cause_analysis.priority_actions
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
    
    
    def _prepare_dashboard_data_node(self, state: FinancialWorkflowState) -> FinancialWorkflowState:
        """Prepare final dashboard data structure"""
        try:
            comparison = state["monthly_comparison"]
            time_series = state["time_series_data"]
            root_cause = state["root_cause_analysis"]
            narratives = state["financial_narratives"]
            
            dashboard_data = {
                "tiles": {
                    "revenue": {
                        "current": comparison.current_month.revenue,
                        "previous": comparison.previous_month.revenue,
                        "change": comparison.revenue_change,
                        "change_percent": comparison.current_month.revenue_pct_change
                    },
                    "expenses": {
                        "current": comparison.current_month.expenses,
                        "previous": comparison.previous_month.expenses,
                        "change": comparison.expenses_change,
                        "change_percent": comparison.current_month.expenses_pct_change
                    },
                    "profitability": {
                        "current": comparison.current_month.profitability,
                        "previous": comparison.previous_month.profitability,
                        "change": comparison.profitability_change,
                        "change_percent": comparison.current_month.profitability_pct_change
                    },
                    "cash_flow": {
                        "current": comparison.current_month.cash_flow,
                        "previous": comparison.previous_month.cash_flow,
                        "change": comparison.cash_flow_change,
                        "change_percent": comparison.current_month.cash_flow_pct_change
                    }
                },
                "time_series": {
                    "dates": time_series.dates,
                    "revenue": time_series.revenue,
                    "expenses": time_series.expenses,
                    "profitability": time_series.profitability,
                    "cash_flow": time_series.cash_flow
                },
                "root_cause_analysis": {
                    "revenue": {
                        "metric": root_cause.revenue_analysis.metric,
                        "trend_direction": root_cause.revenue_analysis.trend_direction,
                        "analysis_summary": root_cause.revenue_analysis.analysis_summary,
                        "top_factors": [
                            {
                                "factor_name": factor.factor_name,
                                "factor_type": factor.factor_type,
                                "change": factor.change,
                                "change_percent": factor.change_percent,
                                "impact_score": factor.impact_score,
                                "rank": factor.rank
                            }
                            for factor in root_cause.revenue_analysis.top_contributing_factors
                        ],
                        "recommendations": root_cause.revenue_analysis.recommendations
                    },
                    "expenses": {
                        "metric": root_cause.expenses_analysis.metric,
                        "trend_direction": root_cause.expenses_analysis.trend_direction,
                        "analysis_summary": root_cause.expenses_analysis.analysis_summary,
                        "top_factors": [
                            {
                                "factor_name": factor.factor_name,
                                "factor_type": factor.factor_type,
                                "change": factor.change,
                                "change_percent": factor.change_percent,
                                "impact_score": factor.impact_score,
                                "rank": factor.rank
                            }
                            for factor in root_cause.expenses_analysis.top_contributing_factors
                        ],
                        "recommendations": root_cause.expenses_analysis.recommendations
                    },
                    "profitability": {
                        "metric": root_cause.profitability_analysis.metric,
                        "trend_direction": root_cause.profitability_analysis.trend_direction,
                        "analysis_summary": root_cause.profitability_analysis.analysis_summary,
                        "top_factors": [
                            {
                                "factor_name": factor.factor_name,
                                "factor_type": factor.factor_type,
                                "change": factor.change,
                                "change_percent": factor.change_percent,
                                "impact_score": factor.impact_score,
                                "rank": factor.rank
                            }
                            for factor in root_cause.profitability_analysis.top_contributing_factors
                        ],
                        "recommendations": root_cause.profitability_analysis.recommendations
                    },
                    "cash_flow": {
                        "metric": root_cause.cash_flow_analysis.metric,
                        "trend_direction": root_cause.cash_flow_analysis.trend_direction,
                        "analysis_summary": root_cause.cash_flow_analysis.analysis_summary,
                        "top_factors": [
                            {
                                "factor_name": factor.factor_name,
                                "factor_type": factor.factor_type,
                                "change": factor.change,
                                "change_percent": factor.change_percent,
                                "impact_score": factor.impact_score,
                                "rank": factor.rank
                            }
                            for factor in root_cause.cash_flow_analysis.top_contributing_factors
                        ],
                        "recommendations": root_cause.cash_flow_analysis.recommendations
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
                    "profitability": {
                        "narrative": narratives["profitability"].narrative,
                        "key_insights": narratives["profitability"].key_insights,
                        "actionable_recommendations": narratives["profitability"].actionable_recommendations,
                        "business_impact": narratives["profitability"].business_impact
                    },
                    "cash_flow": {
                        "narrative": narratives["cash_flow"].narrative,
                        "key_insights": narratives["cash_flow"].key_insights,
                        "actionable_recommendations": narratives["cash_flow"].actionable_recommendations,
                        "business_impact": narratives["cash_flow"].business_impact
                    }
                },
                "summary": {
                    "total_transactions": len(state["transactions"]),
                    "current_period": comparison.current_month.period,
                    "previous_period": comparison.previous_month.period
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
            "monthly_comparison": None,
            "time_series_data": None,
            "root_cause_analysis": None,
            "financial_narratives": None,
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
