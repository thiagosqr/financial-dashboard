import React from 'react';
import { Insights } from '../types';

interface InsightsPanelProps {
  insights: Insights;
}

const InsightsPanel: React.FC<InsightsPanelProps> = ({ insights }) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-xl font-semibold text-gray-800 mb-6">Business Insights & Actions</h3>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Overall Insights */}
        <div>
          <h4 className="text-lg font-medium text-gray-700 mb-3 flex items-center">
            <span className="mr-2">🔍</span>
            Overall Insights
          </h4>
          {insights.overall_insights && insights.overall_insights.length > 0 ? (
            <div className="space-y-3">
              {insights.overall_insights.map((insight: string, index: number) => (
                <div key={index} className="bg-blue-50 border-l-4 border-blue-400 p-3 rounded-r-lg">
                  <p className="text-blue-800 text-sm leading-relaxed">{insight}</p>
                </div>
              ))}
            </div>
          ) : (
            <div className="bg-gray-50 border-l-4 border-gray-400 p-3 rounded-r-lg">
              <p className="text-gray-600 text-sm">No significant insights identified for this period.</p>
            </div>
          )}
        </div>

        {/* Priority Actions */}
        <div>
          <h4 className="text-lg font-medium text-gray-700 mb-3 flex items-center">
            <span className="mr-2">⚡</span>
            Priority Actions
          </h4>
          {insights.priority_actions && insights.priority_actions.length > 0 ? (
            <div className="space-y-3">
              {insights.priority_actions.map((action: string, index: number) => (
                <div key={index} className="bg-orange-50 border-l-4 border-orange-400 p-3 rounded-r-lg">
                  <p className="text-orange-800 text-sm leading-relaxed">{action}</p>
                </div>
              ))}
            </div>
          ) : (
            <div className="bg-gray-50 border-l-4 border-gray-400 p-3 rounded-r-lg">
              <p className="text-gray-600 text-sm">Continue monitoring current performance.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default InsightsPanel;
