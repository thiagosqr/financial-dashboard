import React from 'react';
import FileUpload from './FileUpload';

interface LeftSidebarProps {
  isOpen: boolean;
  onToggle: () => void;
  onFileUpload: (file: File) => void;
  isUploading: boolean;
  error: string | null;
}

const LeftSidebar: React.FC<LeftSidebarProps> = ({
  isOpen,
  onToggle,
  onFileUpload,
  isUploading,
  error
}) => {
  return (
    <div className={`fixed left-0 top-0 h-full bg-white shadow-lg border-r transition-all duration-300 z-30 ${
      isOpen ? 'w-64' : 'w-16'
    }`}>
      {/* Sidebar Header */}
      <div className="flex items-center justify-between p-4 border-b">
        {isOpen && (
          <div className="flex items-center">
            {/* MYOB Logo */}
            <div className="w-10 h-8 mr-3 flex items-center justify-center">
              <svg 
                viewBox="0 0 200 60" 
                className="w-full h-full"
                style={{ fill: 'var(--purple-primary)' }}
              >
                <path d="M20 10h20v40H20V10zm0-5h20v10H20V5zm0 50h20v10H20v-10z"/>
                <text x="50" y="40" fontSize="24" fontWeight="bold" fill="var(--purple-primary)">MYOB</text>
              </svg>
            </div>
            <h2 className="text-lg font-semibold text-gray-800">Dashboard</h2>
          </div>
        )}
        {!isOpen && (
          <div className="w-full flex justify-center">
            {/* MYOB Logo - Compact */}
            <div className="w-8 h-6 flex items-center justify-center">
              <svg 
                viewBox="0 0 100 30" 
                className="w-full h-full"
                style={{ fill: 'var(--purple-primary)' }}
              >
                <path d="M10 5h10v20H10V5zm0-3h10v6H10V2zm0 25h10v5H10v-5z"/>
                <text x="25" y="20" fontSize="12" fontWeight="bold" fill="var(--purple-primary)">MYOB</text>
              </svg>
            </div>
          </div>
        )}
        <button
          onClick={onToggle}
          className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
      </div>

      {/* Navigation Menu */}
      <nav className="p-4 space-y-2">
        <div className="space-y-1">
          <button className="w-full flex items-center px-3 py-2 text-sm font-medium text-gray-700 rounded-lg hover:bg-purple-50 hover:text-purple-600 transition-colors">
            <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 5a2 2 0 012-2h4a2 2 0 012 2v6H8V5z" />
            </svg>
            {isOpen && <span>Dashboard</span>}
          </button>

          <button className="w-full flex items-center px-3 py-2 text-sm font-medium text-gray-700 rounded-lg hover:bg-purple-50 hover:text-purple-600 transition-colors">
            <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            {isOpen && <span>Reports</span>}
          </button>

          <button className="w-full flex items-center px-3 py-2 text-sm font-medium text-gray-700 rounded-lg hover:bg-purple-50 hover:text-purple-600 transition-colors">
            <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            {isOpen && <span>Settings</span>}
          </button>
        </div>

        {/* File Upload Section */}
        <div className="pt-4 border-t">
          <div className="mb-3">
            <h3 className={`text-sm font-medium text-gray-500 mb-2 ${!isOpen && 'hidden'}`}>
              Upload Data
            </h3>
            <FileUpload onFileUpload={onFileUpload} isUploading={isUploading} />
          </div>

          {error && (
            <div className="mt-3 bg-red-50 border border-red-200 rounded-lg p-3">
              <div className="flex">
                <div className="text-red-400 mr-2">⚠️</div>
                <div>
                  <h4 className="text-red-800 font-medium text-xs">Error</h4>
                  <p className="text-red-700 text-xs mt-1">{error}</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </nav>
    </div>
  );
};

export default LeftSidebar;
