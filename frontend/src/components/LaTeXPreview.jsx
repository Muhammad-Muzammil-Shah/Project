import React from 'react';

const LaTeXPreview = ({ texContent }) => {
  if (!texContent) return null;

  return (
    <div className="mt-4 p-4 bg-gray-50 border rounded-md">
      <h3 className="text-lg font-semibold mb-2">LaTeX Preview</h3>
      <pre className="overflow-x-auto text-sm text-gray-800">
        <code>{texContent}</code>
      </pre>
    </div>
  );
};

export default LaTeXPreview;
