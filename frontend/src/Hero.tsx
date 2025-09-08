import React from 'react';
import './assets/css/Hero.css';

const Hero: React.FC = () => {
  return (
    <div className="hero-section section">
      <div className="container">
        <div className="hero-content">
          <h1 className="gradient-text gradient-animation">
            The New Standard in Financial Services
          </h1>
          <p>
            We are dedicated to providing secure, reliable, and efficient solutions for handling financial statements. Our platform simplifies the process of uploading, parsing, and managing your financial data.
          </p>
          <a href="/signup" className="btn btn-primary">Get Started</a>
        </div>
      </div>
    </div>
  );
};

export default Hero;
