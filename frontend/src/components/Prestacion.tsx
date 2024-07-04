import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import '../index.css';
import Alert from './Alert';
import DragAndDrop from './DragAndDrop';
import Button from './Button';
import BenefitsResponseBox from './BenefitsResponseBox';
import { Spinner } from './Spinner';

const Prestacion: React.FC = () => {
  const [alert, setAlert] = useState<{ type: 'success' | 'error', message: string, code?: string } | null>(null);
  const [apiResponse, setApiResponse] = useState<Record<string, any> | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const navigate = useNavigate();
  const [environment, setEnvironment] = useState<string>('PRE');
  const [loading, setLoading] = useState<boolean>(false); // Loading state

  useEffect(() => {
    if (alert) {
      const timer = setTimeout(() => {
        setAlert(null);
      }, 5000);

      // Cleanup the timer if the alert changes or the component unmounts
      return () => clearTimeout(timer);
    }
  }, [alert]);

  const handleDrop = (files: FileList | null) => {
    if (files && files.length > 0) {
      const file = files[0];
      // Assuming you want to send the file to the API here
      console.log('File dropped:', file);
      // Simulating API response
      if (file.name.endsWith('.xls') || file.name.endsWith('.xlsx')) {
        setFile(file);
      } else {
        setAlert({ type: 'error', message: 'Invalid file format. Please upload an Excel file.' });
      }
    }
  };

  const handleDownloadExcel = async () => {
    setLoading(true); // Start loading
    try {
      const response = await fetch('http://localhost:8080/api/v1/benefits/example/excel');
      if (!response.ok) {
        const errorData = await response.json();
        throw errorData;
      }
      // Assuming response is a blob and you want to display it
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      window.open(url, '_blank');
    } catch (error) {
      const errorMsg = error as { message: string, code: string };
      console.error('Download Excel error:', error);
      setAlert({
        type: 'error',
        message: errorMsg.message || 'Failed to download Excel file.',
        code: errorMsg.code,
      });
    } finally {
      setLoading(false); // End loading
    }
  };

  const handleSendToApi = async () => {
    if (!file) {
      setAlert({ type: 'error', message: 'No file selected.' });
      return;
    }

    setLoading(true); // Start loading

    try {
      const formData = new FormData();
      formData.append('file', file);

      // Simulating sending file to API
      const response = await fetch(`http://localhost:8080/api/v1/create/benefits/upload?environment=${environment}`, {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw errorData;
      }
      const data = await response.json();
      setApiResponse(data);
      setAlert({ type: 'success', message: 'File sent to API successfully!' });
    } catch (error) {
      const errorMsg = error as { message: string, code: string };
      console.error('Send to API error:', error);
      setAlert({
        type: 'error',
        message: errorMsg.message || 'Failed to send file to API.',
        code: errorMsg.code,
      });
    } finally {
      setLoading(false); // End loading
    }
  };

  const handleCopyResponse = () => {
    if (apiResponse) {
      navigator.clipboard.writeText(JSON.stringify(apiResponse, null, 2));
      setAlert({ type: 'success', message: 'Response copied to clipboard!' });
    }
  };

  const handleReturnHome = () => {
    navigate('/');
  };

  return (
    <div className="flex justify-center p-4">
      {loading && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-500 bg-opacity-50 z-50">
          <Spinner />
        </div>
      )}
      <div className="w-full max-w-3xl border p-4">
        {alert && <Alert type={alert.type} message={alert.message} code={alert.code} />}
        <div className="absolute top-4 left-4">
          <Button onClick={handleReturnHome}>Go Home</Button>
        </div>
        <DndProvider backend={HTML5Backend}>
          <div className="my-4">
            <DragAndDrop onDrop={handleDrop} />
          </div>
        </DndProvider>
        <div className="flex justify-end items-center my-4 space-x-4">
          <Button onClick={handleSendToApi}>GO</Button>
        </div>
        <BenefitsResponseBox response={apiResponse} />
        <div className="flex justify-end my-4">
          <Button onClick={handleCopyResponse}>Copy</Button>
        </div>
      </div>
      <div className="absolute top-4 right-4">
        <Button onClick={handleDownloadExcel}>Download Excel</Button>
      </div>
    </div>
  );
};

export default Prestacion;