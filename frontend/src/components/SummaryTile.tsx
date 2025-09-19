import React from 'react';
import { RootCauseAnalysis } from '../types';

interface SummaryTileProps {
  selectedMetric: string;
  analysis: RootCauseAnalysis;
  getMetricDisplayName: (metric: string) => string;
  getMetricIcon: (metric: string) => string;
  getMetricColorClass: (metric: string) => string;
}

const SummaryTile: React.FC<SummaryTileProps> = ({
  selectedMetric,
  analysis,
  getMetricDisplayName,
  getMetricIcon,
  getMetricColorClass
}) => {
  return (
    <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-800">Top Recommendation</h2>
        <div className="flex items-center space-x-2">
          <div className={`w-8 h-8 rounded-lg ${getMetricColorClass(selectedMetric)} flex items-center justify-center`}>
            <span className="text-white text-sm">{getMetricIcon(selectedMetric)}</span>
          </div>
          <span className="text-lg font-medium text-gray-700">{getMetricDisplayName(selectedMetric)}</span>
          <span className={`trend-badge ${
            analysis.trend_direction === 'increasing' 
              ? (selectedMetric === 'expenses' ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800')
              : analysis.trend_direction === 'decreasing'
              ? (selectedMetric === 'expenses' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800')
              : 'bg-gray-100 text-gray-800'
          }`}>
            {analysis.trend_direction}
          </span>
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Analysis Summary */}
        <div>
          <h3 className="text-lg font-medium text-gray-800 mb-3 flex items-center">
            <span className="mr-2">📊</span>
            Analysis Summary
          </h3>
          <div className="bg-blue-50 border-l-4 border-blue-400 p-4 rounded-r-lg">
            <p className="text-blue-800 leading-relaxed">
              {analysis.analysis_summary}
            </p>
          </div>
        </div>

        {/* Top Recommendation */}
        <div>
          <h3 className="text-lg font-medium text-gray-800 mb-3 flex items-center">
            <span className="mr-2">💡</span>
            Top Recommendation
          </h3>
          {analysis.recommendations && analysis.recommendations.length > 0 ? (
            <div className="bg-orange-50 border-l-4 border-orange-400 p-4 rounded-r-lg">
              <p className="text-orange-800 font-medium leading-relaxed">
                {analysis.recommendations[0]}
              </p>
              {analysis.recommendations.length > 1 && (
                <div className="mt-3 pt-3 border-t border-orange-200">
                  <p className="text-orange-700 text-sm">
                    <strong>Additional recommendations:</strong> {analysis.recommendations.length - 1} more available in detailed analysis below.
                  </p>
                </div>
              )}
            </div>
          ) : (
            <div className="bg-gray-50 border-l-4 border-gray-400 p-4 rounded-r-lg">
              <p className="text-gray-600">No specific recommendations available for this metric.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SummaryTile;
