import React, { useState, useEffect } from 'react';
import './App.css';
import FinancialTile from './components/FinancialTile';
import TimeSeriesChart from './components/TimeSeriesChart';
import FileUpload from './components/FileUpload';
import RootCauseAnalysisComponent from './components/RootCauseAnalysis';
import InsightsPanel from './components/InsightsPanel';
import LeftSidebar from './components/LeftSidebar';
import RightNotesPanel from './components/RightNotesPanel';
import { DashboardData } from './types';
import { uploadFile, getHealth } from './services/api';


const App: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isApiHealthy, setIsApiHealthy] = useState<boolean | null>(null);
  const [leftSidebarOpen, setLeftSidebarOpen] = useState(true);
  const [rightNotesOpen, setRightNotesOpen] = useState(true);
  const [notes, setNotes] = useState<string>('');
  const [selectedMetric, setSelectedMetric] = useState<string>('revenue');

  useEffect(() => {
    // Check API health on component mount
    checkApiHealth();
  }, []);

  const checkApiHealth = async () => {
    try {
      await getHealth();
      setIsApiHealthy(true);
    } catch (error) {
      setIsApiHealthy(false);
    }
  };

  const handleFileUpload = async (file: File) => {
    setIsUploading(true);
    setError(null);
    setDashboardData(null);

    try {
      const data = await uploadFile(file);
      setDashboardData(data);
      // Set the first available metric as selected
      const firstMetric = Object.keys(data.tiles)[0];
      if (firstMetric) {
        setSelectedMetric(firstMetric);
      }
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to process file');
    } finally {
      setIsUploading(false);
    }
  };


  const getMetricData = (metric: string) => {
    if (!dashboardData) return null;
    
    const rawValues = dashboardData.time_series[metric as keyof typeof dashboardData.time_series];
    const values = Array.isArray(rawValues) ? rawValues.map(v => typeof v === 'string' ? parseFloat(v) : v) : [];
    
    return {
      dates: dashboardData.time_series.dates,
      values: values
    };
  };

  const getMetricColor = (metric: string) => {
    const colors = {
      revenue: '#10B981', // green
      expenses: '#EF4444', // red
      profitability: '#8B5CF6', // purple
      cash_flow: '#7C3AED', // darker purple
    };
    return colors[metric as keyof typeof colors] || '#8B5CF6';
  };

  const getMetricIcon = (metric: string) => {
    const icons = {
      revenue: '💰',
      expenses: '💸',
      profitability: '📈',
      cash_flow: '💳',
    };
    return icons[metric as keyof typeof icons] || '📊';
  };

  const getMetricDisplayName = (metric: string) => {
    const displayNames = {
      revenue: 'Revenue',
      expenses: 'Expenses',
      profitability: 'Income',
      cash_flow: 'Cash Flow',
    };
    return displayNames[metric as keyof typeof displayNames] || metric.charAt(0).toUpperCase() + metric.slice(1).replace('_', ' ');
  };

  const getMetricColorClass = (metric: string) => {
    const colors = {
      revenue: 'bg-green-500',
      expenses: 'bg-red-500',
      profitability: 'bg-purple-500',
      cash_flow: 'bg-purple-600',
    };
    return colors[metric as keyof typeof colors] || 'bg-purple-500';
  };

  if (isApiHealthy === false) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h1 className="text-2xl font-bold text-gray-800 mb-2">API Unavailable</h1>
          <p className="text-gray-600 mb-4">
            The backend API is not running. Please start the backend server.
          </p>
          <button
            onClick={checkApiHealth}
            className="btn-purple"
          >
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Left Sidebar */}
      <LeftSidebar 
        isOpen={leftSidebarOpen}
        onToggle={() => setLeftSidebarOpen(!leftSidebarOpen)}
        onFileUpload={handleFileUpload}
        isUploading={isUploading}
        error={error}
      />

      {/* Main Content */}
      <div className={`flex-1 flex flex-col transition-all duration-300 ${
        leftSidebarOpen ? 'ml-64' : 'ml-16'
      } ${rightNotesOpen ? 'mr-80' : 'mr-0'}`}>
        {/* Header */}
        <header className="bg-white shadow-sm border-b px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <button
                onClick={() => setLeftSidebarOpen(!leftSidebarOpen)}
                className="mr-4 p-2 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
              <div className="w-10 h-10 rounded-lg flex items-center justify-center mr-3" style={{ backgroundColor: 'var(--purple-primary)' }}>
                <span className="text-white text-xl">📊</span>
              </div>
              <h1 className="text-2xl font-bold text-gray-800">Financial Dashboard</h1>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${isApiHealthy ? 'bg-green-500' : 'bg-red-500'}`}></div>
                <span className="text-sm text-gray-600">
                  {isApiHealthy ? 'API Connected' : 'API Disconnected'}
                </span>
              </div>
              <button
                onClick={() => setRightNotesOpen(!rightNotesOpen)}
                className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </button>
            </div>
          </div>
        </header>

        {/* Main Content Area */}
        <main className="flex-1 p-6 overflow-auto">
          {!dashboardData ? (
            // File Upload Section
            <div className="max-w-4xl mx-auto">
              <div className="text-center mb-8">
                <h2 className="text-3xl font-bold text-gray-800 mb-4">
                  Multi-Agent Financial Analysis
                </h2>
                <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                  Upload your business transaction CSV file and let our AI agents analyze your financial performance with month-over-month insights.
                </p>
              </div>

              <FileUpload onFileUpload={handleFileUpload} isUploading={isUploading} />

              {error && (
                <div className="mt-6 bg-red-50 border border-red-200 rounded-lg p-4">
                  <div className="flex">
                    <div className="text-red-400 mr-3">⚠️</div>
                    <div>
                      <h3 className="text-red-800 font-medium">Error Processing File</h3>
                      <p className="text-red-700 mt-1">{error}</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ) : (
            // Dashboard Section
            <div className="space-y-8">
              {/* Enhanced Summary */}
              <div className="bg-white rounded-lg shadow-sm border p-6">
                <h2 className="text-xl font-semibold text-gray-800 mb-6">Financial Analysis Summary</h2>
                
                {/* Basic Info */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm mb-8 pb-6 border-b border-gray-200">
                  <div>
                    <span className="text-gray-600">Total Transactions:</span>
                    <span className="ml-2 font-medium">{dashboardData.summary.total_transactions}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Current Period:</span>
                    <span className="ml-2 font-medium">{dashboardData.summary.current_period}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Previous Period:</span>
                    <span className="ml-2 font-medium">{dashboardData.summary.previous_period}</span>
                  </div>
                </div>

                {/* Root Cause Analysis Summary for Each Metric */}
                <div className="space-y-6">
                  <h3 className="text-lg font-medium text-gray-800 mb-4">Key Insights by Metric</h3>
                  
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {Object.entries(dashboardData.root_cause_analysis).map(([metric, analysis]) => (
                      <div key={metric} className="summary-metric-card">
                        <div className="flex items-center mb-3">
                          <div className={`w-8 h-8 rounded-lg ${getMetricColorClass(metric)} flex items-center justify-center mr-3`}>
                            <span className="text-white text-sm">{getMetricIcon(metric)}</span>
                          </div>
                          <h4 className="font-semibold text-gray-800">{getMetricDisplayName(metric)}</h4>
                          <span className={`ml-2 trend-badge ${
                            analysis.trend_direction === 'increasing' 
                              ? (metric === 'expenses' ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800')
                              : analysis.trend_direction === 'decreasing'
                              ? (metric === 'expenses' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800')
                              : 'bg-gray-100 text-gray-800'
                          }`}>
                            {analysis.trend_direction}
                          </span>
                        </div>
                        
                        <p className="text-sm text-gray-700 mb-3 leading-relaxed">
                          {analysis.analysis_summary}
                        </p>
                        
                        {analysis.recommendations && analysis.recommendations.length > 0 && (
                          <div className="space-y-1">
                            <h5 className="text-xs font-medium text-gray-600 uppercase tracking-wide">Top Recommendation</h5>
                            <div className="recommendation-highlight">
                              💡 {analysis.recommendations[0]}
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Metric Tabs */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {Object.entries(dashboardData.tiles).map(([metric, data]) => (
                  <FinancialTile
                    key={metric}
                    title={getMetricDisplayName(metric)}
                    data={data}
                    isSelected={selectedMetric === metric}
                    onClick={() => setSelectedMetric(metric)}
                    icon={getMetricIcon(metric)}
                    color={getMetricColorClass(metric)}
                  />
                ))}
              </div>

              {/* Selected Metric Content */}
              {selectedMetric && dashboardData.tiles[selectedMetric as keyof typeof dashboardData.tiles] && (
                <div className="space-y-6">
                  {/* Time Series Chart */}
                  <TimeSeriesChart
                    data={getMetricData(selectedMetric)!}
                    title={getMetricDisplayName(selectedMetric)}
                    color={getMetricColor(selectedMetric)}
                    insight={null}
                  />

                  {/* Root Cause Analysis */}
                  <RootCauseAnalysisComponent
                    analysis={dashboardData.root_cause_analysis[selectedMetric as keyof typeof dashboardData.root_cause_analysis]}
                    metricName={getMetricDisplayName(selectedMetric)}
                  />
                </div>
              )}

              {/* Overall Insights and Priority Actions */}
              <InsightsPanel insights={dashboardData.insights} />
            </div>
          )}
        </main>
      </div>

      {/* Right Notes Panel */}
      <RightNotesPanel 
        isOpen={rightNotesOpen}
        onToggle={() => setRightNotesOpen(!rightNotesOpen)}
        notes={notes}
        onNotesChange={setNotes}
      />
    </div>
  );
};

export default App;