import React from 'react';
import './assets/css/Features.css';

const Features: React.FC = () => {
  return (
    <div className="features-section section">
      <div className="container">
        <h2>Why Choose Us?</h2>
        <div className="features-grid">
          <div className="feature-card">
            <h3>Secure Uploads</h3>
            <p>Upload your financial statements with confidence. Our platform ensures your data is encrypted and protected.</p>
          </div>
          <div className="feature-card">
            <h3>Automated Parsing</h3>
            <p>Our intelligent parsers automatically extract and categorize data from your statements, saving you time and effort.</p>
          </div>
          <div className="feature-card">
            <h3>Real-time Status</h3>
            <p>Track the status of your uploads and processing in real-time. Know exactly where your data is at all times.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Features;
