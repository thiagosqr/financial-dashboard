import React, { useCallback } from 'react';

interface FileUploadProps {
  onFileUpload: (file: File) => void;
  isUploading: boolean;
}

const FileUpload: React.FC<FileUploadProps> = ({ onFileUpload, isUploading }) => {
  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0 && files[0].type === 'text/csv') {
      onFileUpload(files[0]);
    }
  }, [onFileUpload]);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      onFileUpload(files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          isUploading
            ? 'border-purple-400 bg-purple-50'
            : 'border-gray-300 hover:border-purple-400'
        }`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
      >
        {isUploading ? (
          <div className="space-y-4">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
            <p className="text-purple-600 font-medium">Processing your CSV file...</p>
            <p className="text-sm text-gray-500">
              Our AI agents are analyzing your financial data
            </p>
            <div className="bg-purple-50 border border-purple-200 rounded-lg p-3">
              <p className="text-xs text-purple-700">
                ⏱️ This may take 1-2 minutes as our AI agents perform comprehensive analysis
              </p>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="mx-auto w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center">
              <svg
                className="w-8 h-8 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                />
              </svg>
            </div>
            <div>
              <p className="text-lg font-medium text-gray-700">
                Upload your financial data
              </p>
              <p className="text-sm text-gray-500 mt-1">
                Drag and drop your CSV file here, or click to browse
              </p>
            </div>
            <div>
              <label
                htmlFor="file-upload"
                className="btn-purple cursor-pointer"
              >
                Choose File
              </label>
              <input
                id="file-upload"
                type="file"
                accept=".csv"
                onChange={handleFileSelect}
                className="hidden"
              />
            </div>
            <div className="text-xs text-gray-400">
              <p>Supported format: CSV files only</p>
              <p>Required columns: date, amount, description, category, account</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default FileUpload;
