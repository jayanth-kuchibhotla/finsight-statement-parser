import React from 'react';
import './assets/css/Footer.css';

const Footer: React.FC = () => {
  return (
    <footer className="footer">
      <div className="footer-social">
        <a href="#YOUR_TWITTER_LINK">Twitter</a>
        <a href="#YOUR_LINKEDIN_LINK">LinkedIn</a>
        <a href="#YOUR_GITHUB_LINK">GitHub</a>
      </div>
      <div className="footer-legal">
        <p>&copy; 2025 Fintech. All rights reserved.</p>
      </div>
    </footer>
  );
};

export default Footer;
