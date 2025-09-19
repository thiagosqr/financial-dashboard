import React, { useState, useEffect } from 'react';

interface RightNotesPanelProps {
  isOpen: boolean;
  onToggle: () => void;
  notes: string;
  onNotesChange: (notes: string) => void;
}

const RightNotesPanel: React.FC<RightNotesPanelProps> = ({
  isOpen,
  onToggle,
  notes,
  onNotesChange
}) => {
  const [localNotes, setLocalNotes] = useState(notes);

  useEffect(() => {
    setLocalNotes(notes);
  }, [notes]);

  const handleSave = () => {
    onNotesChange(localNotes);
    // Save to localStorage for persistence
    localStorage.setItem('financial-dashboard-notes', localNotes);
  };

  const handleClear = () => {
    setLocalNotes('');
    onNotesChange('');
    localStorage.removeItem('financial-dashboard-notes');
  };

  // Load notes from localStorage on component mount
  useEffect(() => {
    const savedNotes = localStorage.getItem('financial-dashboard-notes');
    if (savedNotes) {
      setLocalNotes(savedNotes);
      onNotesChange(savedNotes);
    }
  }, [onNotesChange]);

  return (
    <div className={`fixed right-0 top-0 h-full bg-white shadow-lg border-l transition-all duration-300 z-30 ${
      isOpen ? 'w-80' : 'w-0'
    } overflow-hidden`}>
      {isOpen && (
        <div className="flex flex-col h-full">
          {/* Panel Header */}
          <div className="flex items-center justify-between p-4 border-b">
            <div className="flex items-center">
              <svg className="w-5 h-5 mr-2 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
              <h2 className="text-lg font-semibold text-gray-800">Notes</h2>
            </div>
            <button
              onClick={onToggle}
              className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Notes Content */}
          <div className="flex-1 flex flex-col p-4">
            <div className="mb-4">
              <label htmlFor="notes-textarea" className="block text-sm font-medium text-gray-700 mb-2">
                Take notes about your financial analysis
              </label>
              <textarea
                id="notes-textarea"
                value={localNotes}
                onChange={(e) => setLocalNotes(e.target.value)}
                placeholder="Enter your notes here..."
                className="w-full h-64 p-3 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Action Buttons */}
            <div className="flex space-x-2">
              <button
                onClick={handleSave}
                className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
              >
                Save Notes
              </button>
              <button
                onClick={handleClear}
                className="flex-1 bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300 transition-colors text-sm font-medium"
              >
                Clear
              </button>
            </div>

            {/* Notes Statistics */}
            <div className="mt-4 p-3 bg-gray-50 rounded-lg">
              <div className="text-sm text-gray-600">
                <div className="flex justify-between">
                  <span>Characters:</span>
                  <span>{localNotes.length}</span>
                </div>
                <div className="flex justify-between">
                  <span>Words:</span>
                  <span>{localNotes.trim().split(/\s+/).filter(word => word.length > 0).length}</span>
                </div>
                <div className="flex justify-between">
                  <span>Lines:</span>
                  <span>{localNotes.split('\n').length}</span>
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="mt-4">
              <h3 className="text-sm font-medium text-gray-700 mb-2">Quick Actions</h3>
              <div className="space-y-2">
                <button
                  onClick={() => {
                    const timestamp = new Date().toLocaleString();
                    setLocalNotes(prev => prev + `\n\n[${timestamp}] `);
                  }}
                  className="w-full text-left px-3 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  📅 Add timestamp
                </button>
                <button
                  onClick={() => {
                    setLocalNotes(prev => prev + '\n\n---\n');
                  }}
                  className="w-full text-left px-3 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  ➖ Add separator
                </button>
                <button
                  onClick={() => {
                    setLocalNotes(prev => prev + '\n• ');
                  }}
                  className="w-full text-left px-3 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  📝 Add bullet point
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RightNotesPanel;
