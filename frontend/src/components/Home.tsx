import React from 'react';
import { useNavigate } from 'react-router-dom';
import TextSeparatorTool from './TextSeparatorTool';

const Home: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4">
      <div
        className="p-8 border-4 border-gray-300 rounded hover:border-gray-500 hover:scale-105 transition-transform cursor-pointer font-bold text-center text-xl text-gray-700"
        onClick={() => navigate('/prestacion')}
      >
        Prestacion
      </div>
      <div
        className="p-8 border-4 border-gray-300 rounded hover:border-gray-500 hover:scale-105 transition-transform cursor-pointer font-bold text-center text-xl text-gray-700"
        onClick={() => navigate('/forms')}
      >
        Formularios
      </div>
      <div
        className="p-8 border-4 border-gray-300 rounded hover:border-gray-500 hover:scale-105 transition-transform cursor-pointer font-bold text-center text-xl text-gray-700"
        onClick={() => navigate('#')}
      >
        Coming Soon...
      </div>
      <div className="p-8 border-4 border-gray-300 rounded transition-transform text-center">
        <TextSeparatorTool />
      </div>
    </div>
  );
};

export default Home;
