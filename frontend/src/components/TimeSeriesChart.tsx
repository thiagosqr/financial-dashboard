import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { FinancialInsight } from '../types';

interface TimeSeriesChartProps {
  data: {
    dates: string[];
    values: number[];
  };
  title: string;
  color: string;
  insight?: FinancialInsight | null;
}

const TimeSeriesChart: React.FC<TimeSeriesChartProps> = ({
  data,
  title,
  color,
  insight
}) => {
  // Transform data for recharts
  const chartData = data.dates.map((date, index) => ({
    date: new Date(date).toLocaleDateString('en-US', { month: 'short', year: '2-digit' }),
    value: data.values[index]
  }));

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <div className="mb-6">
        <h3 className="text-xl font-semibold text-gray-800 mb-4">{title} - 12 Month Trend</h3>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis 
                dataKey="date" 
                stroke="#666"
                fontSize={12}
                tick={{ fill: '#666' }}
              />
              <YAxis 
                stroke="#666"
                fontSize={12}
                tick={{ fill: '#666' }}
                tickFormatter={formatCurrency}
              />
              <Tooltip 
                formatter={(value: number) => [formatCurrency(value), title]}
                labelFormatter={(label) => `Period: ${label}`}
                contentStyle={{
                  backgroundColor: '#fff',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                }}
              />
              <Line 
                type="monotone" 
                dataKey="value" 
                stroke={color} 
                strokeWidth={3}
                dot={{ fill: color, strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6, stroke: color, strokeWidth: 2 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
      
      {insight && (
        <div className="border-t pt-4">
          <h4 className="text-lg font-medium text-gray-700 mb-3">AI Insights</h4>
          <div className="space-y-3">
            <div>
              <span className="text-sm font-medium text-gray-600">Analysis:</span>
              <p className="text-sm text-gray-700 mt-1">{insight.insight}</p>
            </div>
            
            <div className="flex items-center">
              <span className="text-sm font-medium text-gray-600 mr-2">Trend:</span>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                insight.trend === 'increasing' 
                  ? 'bg-green-100 text-green-800' 
                  : insight.trend === 'decreasing'
                  ? 'bg-red-100 text-red-800'
                  : 'bg-gray-100 text-gray-800'
              }`}>
                {insight.trend}
              </span>
            </div>
            
            <div>
              <span className="text-sm font-medium text-gray-600">Recommendation:</span>
              <p className="text-sm text-gray-700 mt-1">{insight.recommendation}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TimeSeriesChart;
