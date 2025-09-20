import React from 'react';
import { FinancialTile as FinancialTileType } from '../types';

interface FinancialTileProps {
  title: string;
  data: FinancialTileType;
  isSelected: boolean;
  onClick: () => void;
  icon: string;
  color: string;
}

const FinancialTile: React.FC<FinancialTileProps> = ({
  title,
  data,
  isSelected,
  onClick,
  icon,
  color
}) => {
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

  const getChangeColor = (change: number) => {
    if (title === 'Expenses') {
      // For expenses, increase is bad (red), decrease is good (green)
      return change > 0 ? 'text-red-600' : 'text-green-600';
    } else {
      // For revenue, profitability, free cash flow, increase is good (green), decrease is bad (red)
      return change > 0 ? 'text-green-600' : 'text-red-600';
    }
  };

  return (
    <div
      className={`bg-white rounded-lg shadow-sm border p-6 transition-all duration-200 hover:shadow-md cursor-pointer ${
        isSelected ? 'ring-2 ring-purple-500 shadow-lg border-purple-200 bg-purple-50' : 'hover:border-purple-200'
      }`}
      onClick={onClick}
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center">
          <div className={`w-12 h-12 rounded-lg ${color} flex items-center justify-center mr-3`}>
            <span className="text-white text-xl">{icon}</span>
          </div>
          <h3 className="text-lg font-semibold text-gray-700">{title}</h3>
        </div>
      </div>
      
      <div className="space-y-3">
        <div className="text-3xl font-bold text-gray-900">
          {formatCurrency(data.current)}
        </div>
        
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-500">
            vs {formatCurrency(data.previous)}
          </div>
          <div className={`text-sm font-medium ${getChangeColor(data.change)}`}>
            {formatPercentage(data.change_percent)}
          </div>
        </div>
        
        <div className="text-xs text-gray-400">
          {data.change > 0 ? '↗' : '↘'} {formatCurrency(Math.abs(data.change))}
        </div>
      </div>
    </div>
  );
};

export default FinancialTile;
