import React, { useState, useEffect } from 'react';

const StatusPage = () => {
  const [uploadStatus, setUploadStatus] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // In a real application, you would fetch the upload status from your backend API.
    // For this example, we'll simulate an API call with a timeout.
    const fetchStatus = () => {
      // Replace with your actual API endpoint to get upload status
      // For example: fetch('/api/status?uploadId=YOUR_UPLOAD_ID')
      setTimeout(() => {
        // Simulate different statuses
        const statuses = ['Processing', 'Completed', 'Failed'];
        const randomStatus = statuses[Math.floor(Math.random() * statuses.length)];
        setUploadStatus(randomStatus);
        setIsLoading(false);
      }, 2000);
    };

    fetchStatus();
  }, []);

  return (
    <div className="container mt-5">
      <div className="row justify-content-center">
        <div className="col-md-6">
          <div className="card">
            <div className="card-body">
              <h2 className="card-title text-center">Upload Status</h2>
              {isLoading ? (
                <div className="text-center">
                  <div className="spinner-border" role="status">
                    <span className="visually-hidden">Loading...</span>
                  </div>
                  <p>Checking status...</p>
                </div>
              ) : (
                <div className="text-center">
                  {uploadStatus === 'Completed' && (
                    <div className="alert alert-success" role="alert">
                      Upload Completed Successfully!
                    </div>
                  )}
                  {uploadStatus === 'Processing' && (
                    <div className="alert alert-info" role="alert">
                      Your statement is being processed.
                    </div>
                  )}
                  {uploadStatus === 'Failed' && (
                    <div className="alert alert-danger" role="alert">
                      Upload Failed. Please try again.
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StatusPage;
