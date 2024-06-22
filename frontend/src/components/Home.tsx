import React from 'react';
import { useNavigate } from 'react-router-dom';
import TextSeparatorTool from './TextSeparatorTool';

const Home: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4">
      <div
        className="p-8 border rounded hover:scale-105 transition-transform cursor-pointer font-bold text-center text-xl"
        onClick={() => navigate('/prestacion')}
      >
        Prestacion
      </div>
      <div
        className="p-8 border rounded hover:scale-105 transition-transform cursor-pointer font-bold text-center text-xl"
        onClick={() => navigate('/benefits')}
      >
        Benefits (Not implemented)
      </div>
      <div
        className="p-8 border rounded hover:scale-105 transition-transform cursor-pointer font-bold text-center text-xl"
        onClick={() => navigate('#')}
      >
        Coming Soon...
      </div>
      <div className="p-8 border rounded transition-transform text-center">
        <TextSeparatorTool />
      </div>
    </div>
  );
};

export default Home;
