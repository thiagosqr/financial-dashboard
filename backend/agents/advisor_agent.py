"""
Financial Advisor Agent for generating intelligent recommendations using LLM
"""
import logging
from typing import Dict, List, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field

# Create logger
logger = logging.getLogger(__name__)


class MetricAnalysisInput(BaseModel):
    """Schema for metric analysis input to the advisor agent"""
    metric_name: str = Field(description="Name of the metric (Revenue, Expenses, Profitability, Free Cash Flow)")
    current_value: float = Field(description="Current period metric value")
    previous_value: float = Field(description="Previous period metric value")
    change: float = Field(description="Absolute change from previous period")
    change_percent: float = Field(description="Percentage change from previous period")
    trend_direction: str = Field(description="Trend direction (increasing, decreasing, stable)")
    time_series_data: List[float] = Field(description="Last 12 months of metric values")
    time_series_dates: List[str] = Field(description="Corresponding dates for time series")
    top_contributing_factors: List[Dict[str, Any]] = Field(description="Top factors contributing to the change")
    narrative: str = Field(description="Descriptive narrative from data storyteller agent")


class AdvisorRecommendation(BaseModel):
    """Schema for advisor recommendation output"""
    metric: str = Field(description="The metric being analyzed")
    recommendation: str = Field(description="Short paragraph with actionable recommendations for business owners")
    priority_level: str = Field(description="Priority level: High, Medium, or Low")
    implementation_timeframe: str = Field(description="Suggested timeframe: Immediate, Short-term (1-3 months), Long-term (3-12 months)")


class FinancialAdvisorAgent:
    """LLM-based Financial Advisor Agent for generating intelligent recommendations"""
    
    def __init__(self, openai_api_key: str):
        logger.info("Initializing FinancialAdvisorAgent")
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.2,  # Lower temperature for more consistent, professional advice
            api_key=openai_api_key
        )
        self.structured_llm = self.llm.with_structured_output(AdvisorRecommendation)
        logger.info("FinancialAdvisorAgent initialized successfully")
    
    def generate_recommendation(self, analysis_input: MetricAnalysisInput) -> AdvisorRecommendation:
        """Generate intelligent recommendations for a specific metric"""
        logger.debug(f"Generating recommendation for metric: {analysis_input.metric_name}")
        logger.debug(f"Current value: {analysis_input.current_value}, Change: {analysis_input.change_percent:.1f}%")
        
        # Create the system prompt
        system_prompt = self._create_system_prompt()
        
        # Create the human message with analysis data
        human_message = self._create_analysis_prompt(analysis_input)
        
        try:
            # Generate the recommendation
            logger.debug("Calling LLM for recommendation generation")
            recommendation = self.structured_llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_message)
            ])
            
            logger.info(f"Successfully generated recommendation for {analysis_input.metric_name}")
            logger.debug(f"Recommendation priority: {recommendation.priority_level}")
            return recommendation
            
        except Exception as e:
            logger.error(f"Error generating recommendation for {analysis_input.metric_name}: {str(e)}")
            # Return a fallback recommendation
            return AdvisorRecommendation(
                metric=analysis_input.metric_name,
                recommendation=f"Monitor {analysis_input.metric_name.lower()} trends closely and consider consulting with a financial advisor for specific guidance.",
                priority_level="Medium",
                implementation_timeframe="Short-term (1-3 months)"
            )
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt for the financial advisor agent"""
        return """You are a professional financial advisor agent specializing in small to medium business financial analysis.

Your expertise includes:
- Financial accounting principles and business performance metrics
- Practical strategies to improve revenue, decrease expenses, increase cash flow, and boost profitability
- Understanding of business operations and market dynamics
- Experience with actionable recommendations that business owners can implement

Your role:
- Analyze financial metrics including overall performance, changes, trends, and contributing factors
- Provide specific, actionable recommendations that business owners can implement
- Focus on practical solutions that can realistically improve the specific metric
- Consider the business context and provide recommendations appropriate for the situation
- Prioritize recommendations based on potential impact and feasibility

Guidelines for recommendations:
- Keep recommendations concise but comprehensive (short paragraph)
- Focus on actionable steps, not just general advice
- Consider both immediate and strategic approaches
- Be specific about what actions to take
- Take into account the trend direction and contributing factors
- Provide realistic timeframes for implementation
- Consider the business owner's perspective and practical constraints"""

    def _create_analysis_prompt(self, analysis_input: MetricAnalysisInput) -> str:
        """Create the analysis prompt with metric data"""
        
        # Format time series trend
        if len(analysis_input.time_series_data) >= 2:
            recent_trend = "increasing" if analysis_input.time_series_data[-1] > analysis_input.time_series_data[-2] else "decreasing"
        else:
            recent_trend = analysis_input.trend_direction
        
        # Format contributing factors
        factors_text = ""
        if analysis_input.top_contributing_factors:
            factors_text = "Top contributing factors:\n"
            for i, factor in enumerate(analysis_input.top_contributing_factors[:3], 1):
                factor_name = factor.get('factor_name', 'Unknown')
                factor_change = factor.get('change', 0)
                impact_score = factor.get('impact_score', 0)
                factors_text += f"{i}. {factor_name}: {factor_change:+,.2f} ({impact_score:.1f}% impact)\n"
        
        # Format time series summary
        if len(analysis_input.time_series_data) >= 3:
            time_series_summary = f"12-month trend: Started at {analysis_input.time_series_data[0]:,.2f}, peaked/bottomed at {max(analysis_input.time_series_data):,.2f}/{min(analysis_input.time_series_data):,.2f}, currently at {analysis_input.time_series_data[-1]:,.2f}"
        else:
            time_series_summary = "Limited historical data available"
        
        return f"""Please analyze the following {analysis_input.metric_name} performance and provide actionable recommendations:

METRIC PERFORMANCE:
- Metric: {analysis_input.metric_name}
- Current Period Value: ${analysis_input.current_value:,.2f}
- Previous Period Value: ${analysis_input.previous_value:,.2f}
- Change: ${analysis_input.change:+,.2f} ({analysis_input.change_percent:+.1f}%)
- Trend Direction: {analysis_input.trend_direction}

HISTORICAL CONTEXT:
- {time_series_summary}
- Recent trend: {recent_trend}

ANALYSIS INSIGHTS:
{analysis_input.narrative}

{factors_text}

Based on this analysis, provide specific, actionable recommendations for how the business owner can improve their {analysis_input.metric_name.lower()}. Focus on practical steps they can take, considering the contributing factors and current trends."""

    def generate_bulk_recommendations(self, 
                                    revenue_analysis: Dict[str, Any],
                                    expenses_analysis: Dict[str, Any], 
                                    profitability_analysis: Dict[str, Any],
                                    free_cash_flow_analysis: Dict[str, Any],
                                    narratives: Dict[str, Any]) -> Dict[str, AdvisorRecommendation]:
        """Generate recommendations for all metrics at once"""
        logger.info("Generating bulk recommendations for all metrics")
        
        recommendations = {}
        
        # Define the metrics to analyze
        metrics_data = {
            "Revenue": revenue_analysis,
            "Expenses": expenses_analysis, 
            "Profitability": profitability_analysis,
            "Free Cash Flow": free_cash_flow_analysis
        }
        
        for metric_name, analysis_data in metrics_data.items():
            try:
                # Map metric names to narrative keys
                narrative_key = {
                    "Revenue": "revenue",
                    "Expenses": "expenses", 
                    "Profitability": "income",  # Note: profitability maps to income narrative
                    "Free Cash Flow": "free_cash_flow"
                }.get(metric_name, metric_name.lower())
                
                # Create input for the advisor
                analysis_input = MetricAnalysisInput(
                    metric_name=metric_name,
                    current_value=analysis_data.get('current_period_value', 0),
                    previous_value=analysis_data.get('previous_period_value', 0),
                    change=analysis_data.get('total_change', 0),
                    change_percent=analysis_data.get('change_percent', 0),
                    trend_direction=analysis_data.get('trend_direction', 'stable'),
                    time_series_data=analysis_data.get('time_series_values', []),
                    time_series_dates=analysis_data.get('time_series_dates', []),
                    top_contributing_factors=analysis_data.get('top_contributing_factors', []),
                    narrative=getattr(narratives.get(narrative_key), 'narrative', f"Analysis for {metric_name}") if narratives.get(narrative_key) else f"Analysis for {metric_name}"
                )
                
                # Generate recommendation
                recommendation = self.generate_recommendation(analysis_input)
                recommendations[narrative_key] = recommendation
                
            except Exception as e:
                logger.error(f"Error generating recommendation for {metric_name}: {str(e)}")
                # Add fallback recommendation
                recommendations[narrative_key] = AdvisorRecommendation(
                    metric=metric_name,
                    recommendation=f"Continue monitoring {metric_name.lower()} performance and consider consulting with a financial advisor for detailed guidance.",
                    priority_level="Medium",
                    implementation_timeframe="Short-term (1-3 months)"
                )
        
        logger.info(f"Generated {len(recommendations)} recommendations successfully")
        return recommendations
