import React from 'react';
import './assets/css/HomePage.css';
import Hero from './Hero';
import Features from './Features';
import TrustLogos from './TrustLogos';
import Testimonial from './Testimonial';
import Footer from './Footer';

const HomePage: React.FC = () => {
  return (
    <div className="homepage">
      <Hero />
      <Features />
      <TrustLogos />
      <Testimonial />
      <Footer />
    </div>
  );
};

export default HomePage;
