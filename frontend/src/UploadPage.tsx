import React, { useState } from 'react';
import axios, { AxiosProgressEvent } from 'axios';
import './assets/css/UploadPage.css';

const UploadPage: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  type UploadStatus = 'idle' | 'uploading' | 'success' | 'error';
  const [uploadStatus, setUploadStatus] = useState<UploadStatus>('idle');
  const [uploadProgress, setUploadProgress] = useState(0);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      setFile(event.target.files[0]);
      setUploadProgress(0);
      setUploadStatus('idle');
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploadStatus('uploading');
    setUploadProgress(0);

    try {
      const apiEndpoint = process.env.REACT_APP_API_GATEWAY_ENDPOINT;
      if (!apiEndpoint) {
        throw new Error("API endpoint is not configured. Please set REACT_APP_API_GATEWAY_ENDPOINT.");
      }
      // Step 1: Get a presigned URL from your API Gateway
      const presignedUrlResponse = await axios.post(
        `${apiEndpoint}/generate-presigned-url`,
        {
          fileName: file.name,
          fileType: file.type,
        }
      );

      const { uploadUrl } = presignedUrlResponse.data;

      // Step 2: Upload the file to S3 using the presigned URL
      await axios.put(uploadUrl, file, {
        headers: {
          'Content-Type': file.type,
        },
        onUploadProgress: (progressEvent: AxiosProgressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / (progressEvent.total ?? 1)
          );
          setUploadProgress(percentCompleted);
        },
      });

      setUploadStatus('success');
    } catch (error) {
      console.error('Error uploading file:', error);
      setUploadStatus('error');
    }
  };

  const getButtonText = () => {
    switch (uploadStatus) {
      case 'uploading':
        return `Uploading... ${uploadProgress}%`;
      case 'success':
        return 'Upload Successful!';
      case 'error':
        return 'Upload Failed. Try Again.';
      default:
        return 'Upload';
    }
  };

  return (
    <div className="upload-page">
      <div className="upload-card">
        <div className="upload-icon">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
            <path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96zM14 13v4h-4v-4H7l5-5 5 5h-3z" />
          </svg>
        </div>
        <h2 className="upload-title">Upload Your Statement</h2>
        <p className="upload-subtitle">Drag and drop your PDF file here or click to browse</p>
        <div className="upload-dropzone">
          <input type="file" onChange={handleFileChange} accept=".pdf" disabled={uploadStatus === 'uploading'} />
          {file ? (
            <p>Selected file: {file.name}</p>
          ) : (
            <p>Drag 'n' drop a file here, or click to select a file</p>
          )}
        </div>
        {uploadStatus === 'uploading' && (
          <div className="progress-bar">
            <div className="progress" style={{ width: `${uploadProgress}%` }}></div>
          </div>
        )}
        {uploadStatus === 'success' && <p className="upload-status success">File uploaded successfully!</p>}
        {uploadStatus === 'error' && <p className="upload-status error">An error occurred. Please try again.</p>}
        <button
          onClick={handleUpload}
          className={`btn btn-primary btn-gradient ${uploadStatus === 'success' ? 'success' : ''} ${uploadStatus === 'error' ? 'error' : ''}`}
          disabled={!file || uploadStatus === 'uploading' || uploadStatus === 'success'}
        >
          {getButtonText()}
        </button>
      </div>
    </div>
  );
};

export default UploadPage;
