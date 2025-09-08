import React from 'react';
import { Link } from 'react-router-dom';
import './assets/css/Navbar.css';

const Navbar: React.FC = () => {
  return (
    <nav className="navbar">
      <div className="container">
        <Link to="/home" className="navbar-logo">fintech</Link>
        <div className="navbar-links">
          <Link to="/upload">Upload</Link>
          <Link to="/status">Status</Link>
          <Link to="/login" className="btn btn-primary">Login</Link>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
