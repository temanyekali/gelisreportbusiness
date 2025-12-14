import React from 'react';
import { Input } from './input';

export function CurrencyInput({ value, onChange, className, ...props }) {
  const formatNumber = (num) => {
    if (!num) return '';
    // Remove non-digit characters
    const cleaned = num.toString().replace(/\D/g, '');
    // Format with thousand separators
    return cleaned.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  };

  const handleChange = (e) => {
    let inputValue = e.target.value;
    
    // Remove all non-digit characters
    const cleaned = inputValue.replace(/\D/g, '');
    
    // Prevent leading zeros (except for "0")
    const numericValue = cleaned === '' ? '' : parseInt(cleaned, 10).toString();
    
    // Call parent onChange with numeric value (without formatting)
    onChange(numericValue);
  };

  const handleBlur = (e) => {
    // Optional: trigger validation or other blur events
    if (props.onBlur) {
      props.onBlur(e);
    }
  };

  const displayValue = formatNumber(value);

  return (
    <div className="relative">
      <div className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 text-sm">
        Rp
      </div>
      <Input
        {...props}
        type="text"
        inputMode="numeric"
        value={displayValue}
        onChange={handleChange}
        onBlur={handleBlur}
        className={`pl-12 ${className || ''}`}
      />
    </div>
  );
}
