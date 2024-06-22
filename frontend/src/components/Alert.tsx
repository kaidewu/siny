import React from 'react';

interface AlertProps {
  type: 'success' | 'error';
  message: string;
  code?: string;
}

const Alert: React.FC<AlertProps> = ({ type, message, code }) => {
  return (
    <div className={`p-4 mb-4 rounded ${type === 'error' ? 'bg-red-500 text-white' : 'bg-green-500 text-white'}`}>
      <p>{message}</p>
      {code && <p className="text-sm mt-2">Error Code: {code}</p>}
    </div>
  );
};

export default Alert;