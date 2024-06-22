import React from 'react';

interface ResponseBoxProps {
  response: Record<string, any> | null;
}

const ResponseBox: React.FC<ResponseBoxProps> = ({ response }) => {

  let codes = ""

  if (response) {
      codes = response.prestacion
  } else {
      codes = "No response to display"
  }


  return (
    <div className="border p-4 mt-4 bg-gray-100">
        <textarea
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:border-blue-500"
            rows={3}
            value={codes}
            readOnly
        />
    </div>
  );
};

export default ResponseBox;