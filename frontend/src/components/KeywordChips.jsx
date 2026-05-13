import React from 'react';

const KeywordChips = ({ keywords }) => {
  if (!keywords || keywords.length === 0) return null;

  return (
    <div className="flex flex-wrap gap-2 mt-2">
      {keywords.map((keyword, index) => (
        <span 
          key={index} 
          className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium"
        >
          {keyword}
        </span>
      ))}
    </div>
  );
};

export default KeywordChips;
