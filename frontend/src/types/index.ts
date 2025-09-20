// Types for the Financial Dashboard

export interface FinancialTile {
  current: number;
  previous: number;
  change: number;
  change_percent: number;
}

export interface DashboardData {
  tiles?: {
    revenue: FinancialTile;
    expenses: FinancialTile;
    income: FinancialTile;
    free_cash_flow: FinancialTile;
  };
  time_series?: {
    dates: string[];
    revenue: number[];
    expenses: number[];
    income: number[];
    free_cash_flow: number[];
    operating_cash_flow?: number[];
    capital_expenditure?: number[];
  };
  root_cause_analysis?: {
    revenue: RootCauseAnalysis;
    expenses: RootCauseAnalysis;
    income: RootCauseAnalysis;
    free_cash_flow: RootCauseAnalysis;
  };
  insights?: Insights;
  summary?: {
    total_transactions: number;
    current_period: string;
    previous_period: string;
  };
  error?: string;
}

export interface FinancialInsight {
  insight: string;
  trend: string;
  recommendation: string;
}

export interface RootCauseFactor {
  factor_name: string;
  factor_type: string;
  change: number;
  change_percent: number;
  impact_score: number;
  rank: number;
}

export interface RootCauseAnalysis {
  metric: string;
  trend_direction: string;
  analysis_summary: string;
  top_factors: RootCauseFactor[];
  recommendations: string[];
}

export interface Insights {
  overall_insights: string[];
  priority_actions: string[];
}

export interface ApiResponse {
  success: boolean;
  data?: DashboardData;
  error?: string;
}
