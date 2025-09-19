import React from 'react';
import { RootCauseAnalysis, RootCauseFactor } from '../types';

interface RootCauseAnalysisProps {
  analysis: RootCauseAnalysis;
  metricName: string;
}

const RootCauseAnalysisComponent: React.FC<RootCauseAnalysisProps> = ({ analysis, metricName }) => {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatPercentage = (percent: number) => {
    const sign = percent >= 0 ? '+' : '';
    return `${sign}${percent.toFixed(1)}%`;
  };

  const getTrendIcon = (direction: string) => {
    switch (direction) {
      case 'increasing':
        return '📈';
      case 'decreasing':
        return '📉';
      default:
        return '➡️';
    }
  };

  const getTrendColor = (direction: string, metricName: string) => {
    if (metricName === 'Expenses') {
      return direction === 'increasing' ? 'text-red-600' : 'text-green-600';
    } else {
      return direction === 'increasing' ? 'text-green-600' : 'text-red-600';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <div className="flex items-center mb-6">
        <span className="text-2xl mr-3">{getTrendIcon(analysis.trend_direction)}</span>
        <h3 className="text-xl font-semibold text-gray-800">Root Cause Analysis - {metricName}</h3>
        <span className={`ml-3 text-sm font-medium ${getTrendColor(analysis.trend_direction, metricName)}`}>
          {analysis.trend_direction.charAt(0).toUpperCase() + analysis.trend_direction.slice(1)}
        </span>
      </div>

      {/* Analysis Summary */}
      <div className="mb-6">
        <h4 className="text-lg font-medium text-gray-700 mb-2">Summary</h4>
        <p className="text-gray-600 leading-relaxed">{analysis.analysis_summary}</p>
      </div>

      {/* Top Contributing Factors */}
      {analysis.top_factors && analysis.top_factors.length > 0 && (
        <div className="mb-6">
          <h4 className="text-lg font-medium text-gray-700 mb-3">Top Contributing Factors</h4>
          <div className="space-y-3">
            {analysis.top_factors.map((factor: RootCauseFactor, index: number) => (
              <div key={index} className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center">
                    <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded-full mr-3">
                      #{factor.rank}
                    </span>
                    <h5 className="font-medium text-gray-800">{factor.factor_name}</h5>
                  </div>
                  <span className="text-sm text-gray-500">{factor.factor_type}</span>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Change:</span>
                    <span className={`ml-2 font-medium ${factor.change > 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {formatCurrency(factor.change)}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-600">Percentage:</span>
                    <span className={`ml-2 font-medium ${factor.change_percent > 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {formatPercentage(factor.change_percent)}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-600">Impact:</span>
                    <span className="ml-2 font-medium text-blue-600">
                      {factor.impact_score.toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {analysis.recommendations && analysis.recommendations.length > 0 && (
        <div>
          <h4 className="text-lg font-medium text-gray-700 mb-3">Recommendations</h4>
          <div className="space-y-2">
            {analysis.recommendations.map((recommendation: string, index: number) => (
              <div key={index} className="flex items-start">
                <span className="text-blue-500 mr-3 mt-1">💡</span>
                <p className="text-gray-600">{recommendation}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default RootCauseAnalysisComponent;
