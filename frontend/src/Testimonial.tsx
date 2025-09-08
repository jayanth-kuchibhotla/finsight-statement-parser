import React from 'react';
import './assets/css/Testimonial.css';

const Testimonial: React.FC = () => {
  return (
    <div className="testimonial-section section">
      <div className="container">
        <div className="testimonial-content">
          <p className="testimonial-text">
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
          </p>
          <p className="testimonial-author">
            <span>Jane Doe</span> / CEO, Acme Inc.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Testimonial;