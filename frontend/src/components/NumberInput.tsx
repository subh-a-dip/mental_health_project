import React, { useRef, useState, useEffect } from 'react';

interface NumberInputProps {
  value: number;
  onChange: (value: number) => void;
  min?: number;
  max?: number;
  step?: number;
  unit?: string;
}

const NumberInput: React.FC<NumberInputProps> = ({ value, onChange, min = 0, max = 100, step = 0.01, unit = '' }) => {
  const inputRef = useRef<HTMLInputElement>(null);
  const [displayValue, setDisplayValue] = useState<string>(value !== 0 ? String(value) : '');

  // Sync displayValue when parent value changes (e.g., reset from blur)
  useEffect(() => {
    if (value !== 0) {
      setDisplayValue(String(value));
    } else if (value === 0) {
      setDisplayValue('');
    }
  }, [value]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const inputValue = e.target.value;
    // Allow empty, just digits, or digits with decimal point
    if (inputValue === '' || /^[0-9]*\.?[0-9]*$/.test(inputValue)) {
      setDisplayValue(inputValue);
      // Don't call onChange here - let user type freely
    }
  };

  const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
    const inputValue = e.target.value;
    if (inputValue === '' || !/^[0-9]*\.?[0-9]*$/.test(inputValue)) {
      // Invalid - reset to parent value
      setDisplayValue(value !== 0 ? String(value) : '');
      return;
    }
    const val = parseFloat(inputValue);
    if (isNaN(val)) {
      setDisplayValue(value !== 0 ? String(value) : '');
      return;
    }
    const clamped = Math.max(min, Math.min(max, val));
    setDisplayValue(String(clamped));
    onChange(clamped);
  };

  return (
    <div className="flex items-center gap-3">
      <input
        ref={inputRef}
        type="text"
        inputMode="decimal"
        min={min}
        max={max}
        step={step}
        value={displayValue}
        onChange={handleChange}
        onBlur={handleBlur}
        className="w-32 px-4 py-3 rounded-xl border border-slate-300 text-slate-800 text-lg font-semibold focus:outline-none focus:ring-2 focus:ring-primary-400 focus:border-transparent"
        pattern="[0-9]*\.?[0-9]*"
      />
      <span className="text-slate-500 text-sm">{unit}</span>
    </div>
  );
};

export default NumberInput;