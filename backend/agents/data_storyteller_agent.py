"""
Data Storyteller Agent for generating financial narratives using OpenAI
"""
import logging
from typing import Dict, List, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field
from typing import Union
from agents.cash_flow_agent import CashFlowRootCauseAnalysis
from agents.revenue_agent import RevenueRootCauseAnalysis  
from agents.expenses_agent import ExpensesRootCauseAnalysis
from agents.income_agent import IncomeRootCauseAnalysis

# Union type for all root cause analysis types
RootCauseAnalysis = Union[CashFlowRootCauseAnalysis, RevenueRootCauseAnalysis, ExpensesRootCauseAnalysis, IncomeRootCauseAnalysis]

# Create logger
logger = logging.getLogger(__name__)


class FinancialNarrative(BaseModel):
    """Schema for financial narrative output"""
    metric: str = Field(description="The metric being analyzed")
    narrative: str = Field(description="Clear, actionable narrative explaining the metric's performance")
    key_insights: List[str] = Field(description="Key insights derived from the analysis")
    actionable_recommendations: List[str] = Field(description="Specific, actionable recommendations")
    business_impact: str = Field(description="Explanation of business impact and implications")


class DataStorytellerAgent:
    """Agent responsible for generating financial narratives using OpenAI"""
    
    def __init__(self, openai_api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",  # Using a more capable model for better narratives
            temperature=0.3,  # Some creativity but still focused
            api_key=openai_api_key
        )
        self.structured_llm = self.llm.with_structured_output(FinancialNarrative)
    
    def generate_metric_narrative(self, root_cause_analysis: RootCauseAnalysis) -> FinancialNarrative:
        """Generate a narrative for a specific metric based on root cause analysis"""
        logger.debug(f"Generating narrative for metric: {root_cause_analysis.metric}")
        logger.debug(f"Metric change: {root_cause_analysis.total_change:.2f} ({root_cause_analysis.change_percent:.1f}%)")
        
        # Prepare the data for the prompt
        analysis_data = self._prepare_analysis_data(root_cause_analysis)
        
        # Create the system message
        system_message = SystemMessage(content="""
You are a data storyteller and financial expert with deep knowledge on how to make financial insights easy to understand and actionable for business users.

Your role is to interpret financial analysis data and package it in a way that is:
- Easy to understand for non-financial stakeholders
- Actionable with clear next steps
- Engaging and narrative-driven
- Focused on business impact

When analyzing financial metrics, always consider:
1. What the numbers mean in business context
2. Why these changes are happening
3. What actions should be taken
4. What the business impact is

Be conversational yet professional. Use clear, jargon-free language when possible, but don't oversimplify important financial concepts.
""")
        
        # Create the human message with the analysis data
        human_message = HumanMessage(content=f"""
Please generate a comprehensive financial narrative for the {root_cause_analysis.metric} metric based on the following analysis:

**Current Performance:**
- Current Period Value: ${root_cause_analysis.current_period_value:,.2f}
- Previous Period Value: ${root_cause_analysis.previous_period_value:,.2f}
- Change: ${root_cause_analysis.total_change:,.2f} ({root_cause_analysis.change_percent:.1f}%)
- Trend Direction: {root_cause_analysis.trend_direction}

**Root Cause Analysis:**
{analysis_data}

**Analysis Summary:**
{root_cause_analysis.analysis_summary}

Please provide:
1. A clear, engaging narrative that explains what these numbers mean
2. Key insights that highlight the most important findings
3. Specific, actionable recommendations
4. An explanation of the business impact

Make it accessible to business stakeholders while maintaining financial accuracy.
""")
        
        try:
            logger.debug("Sending request to OpenAI for narrative generation")
            response = self.structured_llm.invoke([system_message, human_message])
            logger.info(f"Successfully generated narrative for {root_cause_analysis.metric}")
            logger.debug(f"Narrative preview: {response.narrative[:100]}...")
            return response
        except Exception as e:
            logger.warning(f"OpenAI narrative generation failed for {root_cause_analysis.metric}: {str(e)}")
            logger.debug("Using fallback narrative")
            # Fallback to a basic narrative if OpenAI fails
            return self._generate_fallback_narrative(root_cause_analysis)
    
    def generate_comprehensive_narrative(self, 
                                       revenue_analysis: RevenueRootCauseAnalysis,
                                       expenses_analysis: ExpensesRootCauseAnalysis, 
                                       income_analysis: IncomeRootCauseAnalysis,
                                       cash_flow_analysis: CashFlowRootCauseAnalysis,
                                       overall_insights: List[str],
                                       priority_actions: List[str]) -> Dict[str, Any]:
        """Generate comprehensive narratives for all metrics and overall business story"""
        logger.info("Starting comprehensive narrative generation for all metrics")
        logger.debug(f"Overall insights count: {len(overall_insights)}")
        logger.debug(f"Priority actions count: {len(priority_actions)}")
        
        # Generate individual metric narratives
        logger.debug("Generating revenue narrative")
        revenue_narrative = self.generate_metric_narrative(revenue_analysis)
        
        logger.debug("Generating expenses narrative")
        expenses_narrative = self.generate_metric_narrative(expenses_analysis)
        
        logger.debug("Generating income narrative")
        income_narrative = self.generate_metric_narrative(income_analysis)
        
        logger.debug("Generating cash flow narrative")
        cash_flow_narrative = self.generate_metric_narrative(cash_flow_analysis)
        
        # Generate overall business narrative
        logger.debug("Generating overall business narrative")
        overall_narrative = self._generate_overall_business_narrative(
            revenue_analysis, expenses_analysis, income_analysis, cash_flow_analysis,
            overall_insights, priority_actions
        )
        
        logger.info("Comprehensive narrative generation completed successfully")
        return {
            "revenue": revenue_narrative,
            "expenses": expenses_narrative,
            "income": income_narrative,
            "cash_flow": cash_flow_narrative,
            "overall_business_story": overall_narrative,
            "priority_actions": priority_actions,
            "overall_insights": overall_insights
        }
    
    def _prepare_analysis_data(self, root_cause_analysis: RootCauseAnalysis) -> str:
        """Prepare the root cause analysis data in a readable format"""
        if not root_cause_analysis.top_contributing_factors:
            return "No significant contributing factors identified."
        
        factors_text = "Top contributing factors:\n"
        for i, factor in enumerate(root_cause_analysis.top_contributing_factors[:5], 1):
            direction = "increased" if factor.change > 0 else "decreased" if factor.change < 0 else "remained stable"
            factors_text += f"{i}. {factor.factor_name} ({factor.factor_type}): {direction} by ${abs(factor.change):,.2f} ({abs(factor.change_percent):.1f}%) - Impact: {factor.impact_score:.1f}%\n"
        
        return factors_text
    
    def _generate_overall_business_narrative(self, 
                                           revenue_analysis: RevenueRootCauseAnalysis,
                                           expenses_analysis: ExpensesRootCauseAnalysis,
                                           income_analysis: IncomeRootCauseAnalysis,
                                           cash_flow_analysis: CashFlowRootCauseAnalysis,
                                           overall_insights: List[str],
                                           priority_actions: List[str]) -> Dict[str, Any]:
        """Generate an overall business narrative that ties everything together"""
        
        system_message = SystemMessage(content="""
You are a senior financial advisor and business strategist. Your job is to synthesize multiple financial metrics into a cohesive business story that executives and stakeholders can understand and act upon.

Create a compelling narrative that:
1. Tells the overall business performance story
2. Identifies key themes and patterns across metrics
3. Highlights critical business implications
4. Provides strategic recommendations
5. Addresses potential risks and opportunities

Be strategic, forward-looking, and executive-ready.
""")
        
        human_message = HumanMessage(content=f"""
Based on the comprehensive financial analysis below, create an overall business narrative that tells the complete story:

**Revenue Performance:**
- Change: ${revenue_analysis.total_change:,.2f} ({revenue_analysis.change_percent:.1f}%)
- Trend: {revenue_analysis.trend_direction}

**Expenses Performance:**
- Change: ${expenses_analysis.total_change:,.2f} ({expenses_analysis.change_percent:.1f}%)
- Trend: {expenses_analysis.trend_direction}

**Profitability Performance:**
- Change: ${income_analysis.total_change:,.2f} ({income_analysis.change_percent:.1f}%)
- Trend: {income_analysis.trend_direction}

**Cash Flow Performance:**
- Change: ${cash_flow_analysis.total_change:,.2f} ({cash_flow_analysis.change_percent:.1f}%)
- Trend: {cash_flow_analysis.trend_direction}

**Key Insights Identified:**
{chr(10).join(f"- {insight}" for insight in overall_insights)}

**Priority Actions:**
{chr(10).join(f"- {action}" for action in priority_actions)}

Please provide a comprehensive business narrative that synthesizes this information into an executive summary.
""")
        
        try:
            response = self.llm.invoke([system_message, human_message])
            return {
                "narrative": response.content,
                "executive_summary": self._extract_executive_summary(response.content),
                "key_themes": self._extract_key_themes(response.content)
            }
        except Exception as e:
            return self._generate_fallback_overall_narrative(
                revenue_analysis, expenses_analysis, income_analysis, cash_flow_analysis,
                overall_insights, priority_actions
            )
    
    def _extract_executive_summary(self, narrative: str) -> str:
        """Extract or generate an executive summary from the narrative"""
        # Simple extraction of first paragraph as executive summary
        paragraphs = narrative.split('\n\n')
        return paragraphs[0] if paragraphs else narrative[:200] + "..."
    
    def _extract_key_themes(self, narrative: str) -> List[str]:
        """Extract key themes from the narrative"""
        # This is a simplified implementation
        # In a production system, you might use more sophisticated NLP
        themes = []
        if "growth" in narrative.lower():
            themes.append("Growth Strategy")
        if "cost" in narrative.lower() or "expense" in narrative.lower():
            themes.append("Cost Management")
        if "cash" in narrative.lower():
            themes.append("Cash Flow Optimization")
        if "profit" in narrative.lower():
            themes.append("Profitability Enhancement")
        if "risk" in narrative.lower():
            themes.append("Risk Management")
        
        return themes if themes else ["Financial Performance"]
    
    def _generate_fallback_narrative(self, root_cause_analysis: RootCauseAnalysis) -> FinancialNarrative:
        """Generate a basic narrative if OpenAI fails"""
        direction = "improved" if root_cause_analysis.total_change > 0 else "declined" if root_cause_analysis.total_change < 0 else "remained stable"
        
        return FinancialNarrative(
            metric=root_cause_analysis.metric,
            narrative=f"The {root_cause_analysis.metric.lower()} has {direction} by ${abs(root_cause_analysis.total_change):,.2f} ({abs(root_cause_analysis.change_percent):.1f}%) compared to the previous period. This indicates a {root_cause_analysis.trend_direction} trend in business performance.",
            key_insights=[
                f"{root_cause_analysis.metric} {direction} by {abs(root_cause_analysis.change_percent):.1f}%",
                f"Trend direction: {root_cause_analysis.trend_direction}"
            ],
            actionable_recommendations=[
                "Monitor this metric closely for continued trends",
                "Review contributing factors for optimization opportunities"
            ],
            business_impact=f"This {direction} in {root_cause_analysis.metric.lower()} has implications for overall business performance and should be considered in strategic planning."
        )
    
    def _generate_fallback_overall_narrative(self, 
                                           revenue_analysis: RevenueRootCauseAnalysis,
                                           expenses_analysis: ExpensesRootCauseAnalysis,
                                           income_analysis: IncomeRootCauseAnalysis,
                                           cash_flow_analysis: CashFlowRootCauseAnalysis,
                                           overall_insights: List[str],
                                           priority_actions: List[str]) -> Dict[str, Any]:
        """Generate a basic overall narrative if OpenAI fails"""
        return {
            "narrative": f"Business performance shows mixed results across key metrics. Revenue {revenue_analysis.trend_direction}, expenses {expenses_analysis.trend_direction}, income {income_analysis.trend_direction}, and cash flow {cash_flow_analysis.trend_direction}. Key priorities include monitoring these trends and taking appropriate action.",
            "executive_summary": "Financial performance shows varying trends across key metrics requiring strategic attention.",
            "key_themes": ["Financial Performance", "Strategic Planning"]
        }
