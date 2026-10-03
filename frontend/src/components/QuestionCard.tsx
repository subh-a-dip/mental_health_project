import React, { useState } from 'react';
import StarRating from './StarRating';
import NumberInput from './NumberInput';
import { getRatingDescription } from '@/utils/ageCalculator';
import type { Question } from '@/types/assessment';

interface QuestionCardProps {
  question: Question;
  value: number;
  onChange: (value: number) => void;
  error?: string;
}

const BMICalculator: React.FC<{ onCalculate: (bmi: number) => void }> = ({ onCalculate }) => {
  const [weight, setWeight] = useState<number | ''>('');
  const [height, setHeight] = useState<number | ''>('');
  const [calculatedBMI, setCalculatedBMI] = useState<number | null>(null);

  const calculateBMI = () => {
    const w = typeof weight === 'number' ? weight : parseFloat(weight as any);
    const h = typeof height === 'number' ? height : parseFloat(height as any);
    if (!isNaN(w) && !isNaN(h) && w > 0 && h > 0) {
      const bmi = (w / (h * h)) * 10000;
      const rounded = Math.round(bmi * 10) / 10;
      setCalculatedBMI(rounded);
      onCalculate(rounded);
    }
  };

  return (
    <div className="bg-sage-50 rounded-xl p-4 mb-4 border border-sage-200">
      <h4 className="font-semibold text-sage-800 mb-3 flex items-center gap-2">
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        BMI Calculator
      </h4>
      <p className="text-sm text-sage-600 mb-3">Enter your weight and height to calculate BMI automatically</p>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-3">
        <div>
          <label className="block text-sm font-medium text-sage-700 mb-1">Weight (kg)</label>
          <input
            type="number"
            step="0.1"
            min="20"
            max="300"
            value={weight}
            onChange={(e) => setWeight(e.target.value === '' ? '' : parseFloat(e.target.value))}
            placeholder="e.g., 70"
            className="w-full px-3 py-2 rounded-lg border border-sage-300 bg-white text-slate-800 focus:outline-none focus:ring-2 focus:ring-sage-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-sage-700 mb-1">Height (cm)</label>
          <input
            type="number"
            step="0.1"
            min="50"
            max="250"
            value={height}
            onChange={(e) => setHeight(e.target.value === '' ? '' : parseFloat(e.target.value))}
            placeholder="e.g., 175"
            className="w-full px-3 py-2 rounded-lg border border-sage-300 bg-white text-slate-800 focus:outline-none focus:ring-2 focus:ring-sage-500"
          />
        </div>
      </div>
      <button
        type="button"
        onClick={calculateBMI}
        disabled={!weight || !height}
        className="w-full px-4 py-2 bg-sage-600 text-white rounded-lg hover:bg-sage-700 disabled:bg-sage-300 disabled:cursor-not-allowed transition-colors"
      >
        Calculate BMI
      </button>
      {calculatedBMI !== null && (
        <div className="mt-3 p-3 bg-white rounded-lg border border-sage-200 text-center">
          <p className="text-sm text-sage-600">Your BMI:</p>
          <p className="text-2xl font-bold text-sage-700">{calculatedBMI}</p>
          <p className="text-xs text-sage-500 mt-1">Click "Calculate BMI" to use this value</p>
        </div>
      )}
    </div>
  );
};

const QuestionCard: React.FC<QuestionCardProps> = ({
  question,
  value,
  onChange,
  error,
}) => {
  const isBMI = question.category === 'BMI';
  return (
    <div className="bg-white rounded-2xl p-6 sm:p-8 border border-slate-200 shadow-sm animate-slide-up">
      <div className="mb-1">
        <span className="text-sm font-semibold text-primary-600 uppercase tracking-wider">{question.category}</span>
      </div>
      <h3 className="text-lg sm:text-xl font-semibold text-slate-800 mb-6">{question.question}</h3>
      {isBMI && (
        <BMICalculator onCalculate={onChange} />
      )}
      {question.type === 'rating' && (
        <StarRating value={value} onChange={onChange} max={question.maxValue || 10} />
      )}
      {question.type === 'number' && (
        <NumberInput
          value={value}
          onChange={onChange}
          min={question.minValue || 0}
          max={question.maxValue || 100}
          step={question.step}
          unit={question.unit || ''}
        />
      )}
      {question.type === 'multiple_choice' && question.options && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-6">
          {question.options.map((opt, idx) => (
            <button
              key={opt}
              onClick={() => onChange(idx + 1)}
              className={`p-4 rounded-xl border text-left transition-all ${
                value === idx + 1
                  ? 'border-primary-500 bg-primary-50 text-primary-800'
                  : 'border-slate-200 hover:border-slate-300 hover:bg-slate-50'
              }`}
            >
              {opt}
            </button>
          ))}
        </div>
      )}
      {question.type === 'rating' && value > 0 && (
        <p className="text-sm text-slate-500 mb-4 mt-2">
          Selected: <span className="font-semibold">{value}</span> — {getRatingDescription(value)}
        </p>
      )}
      {error && <p className="text-red-500 text-sm mb-4">{error}</p>}
    </div>
  );
};

export default QuestionCard;
