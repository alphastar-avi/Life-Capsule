import React from 'react';

const Textarea = ({ value, onChange, placeholder, className }) => {
  return (
    <textarea
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      className={`border rounded p-2 w-full ${className}`}
      rows="4"
    />
  );
};

export default Textarea;
