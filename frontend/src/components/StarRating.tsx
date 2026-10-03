import React from 'react';

interface StarRatingProps {
  value: number;
  onChange: (value: number) => void;
  max?: number;
}

const StarRating: React.FC<StarRatingProps> = ({ value, onChange, max = 10 }) => {
  const getStarColor = (index: number) => {
    if (index <= value) {
      if (value <= 3) return '#3b82f6';
      if (value <= 6) return '#f59e0b';
      if (value <= 8) return '#ef4444';
      return '#991b1b';
    }
    return '#cbd5e1';
  };

  const getStarColorLight = (index: number) => {
    if (index <= value) {
      if (value <= 3) return '#dbeafe';
      if (value <= 6) return '#fef3c7';
      if (value <= 8) return '#fee2e2';
      return '#fecaca';
    }
    return '#f1f5f9';
  };

  const getLabel = () => {
    if (value <= 3) return 'Low';
    if (value <= 6) return 'Moderate';
    if (value <= 8) return 'High';
    return 'Very High';
  };

  const getLabelColor = () => {
    if (value <= 3) return 'text-blue-600';
    if (value <= 6) return 'text-amber-600';
    if (value <= 8) return 'text-red-600';
    return 'text-red-800';
  };

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="flex gap-1" role="radiogroup" aria-label="Rating">
        {Array.from({ length: max }, (_, i) => {
          const starIndex = i + 1;
          return (
            <button
              key={starIndex}
              type="button"
              role="radio"
              aria-checked={starIndex === value}
              onClick={() => onChange(starIndex)}
              className={`w-10 h-10 sm:w-12 sm:h-12 flex items-center justify-center rounded-lg transition-all duration-150 hover:scale-110 focus:outline-none focus:ring-2 focus:ring-offset-1 ${starIndex <= value ? 'shadow-md' : ''}`}
              style={{ backgroundColor: getStarColorLight(starIndex), color: getStarColor(starIndex) }}
            >
              <svg
                className="w-6 h-6 sm:w-7 sm:h-7"
                fill={starIndex <= value ? 'currentColor' : 'none'}
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"
                />
              </svg>
            </button>
          );
        })}
      </div>
      {value > 0 && (
        <span className={`text-sm font-semibold ${getLabelColor()}`}>
          {value}/10 — {getLabel()}
        </span>
      )}
    </div>
  );
};

export default StarRating;
