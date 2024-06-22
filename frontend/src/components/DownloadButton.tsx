import React from 'react';

const DownloadButton: React.FC = () => {
  const handleDownload = async () => {
    try {
      const response = await fetch('http://localhost:8080/api/v1/benefits/example/excel', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        },
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);

      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'INPUT.xlsx'); // or any other extension
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);

      // Release the object URL after the download
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Download error:', error);
    }
  };

  return (
    <button onClick={handleDownload}>
      Download Excel
    </button>
  );
};

export default DownloadButton;