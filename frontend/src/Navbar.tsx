import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { signOut } from '@aws-amplify/auth';
import './assets/css/Navbar.css';

interface NavbarProps {
  isAuthenticated: boolean;
  setIsAuthenticated: (isAuthenticated: boolean) => void;
}

const Navbar: React.FC<NavbarProps> = ({ isAuthenticated, setIsAuthenticated }) => {
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await signOut();
      setIsAuthenticated(false);
      navigate('/login');
    } catch (error) {
      console.error('Error signing out: ', error);
    }
  };

  return (
    <nav className="navbar">
      <div className="container">
        <Link to="/home" className="navbar-logo">fintech</Link>
        <div className="navbar-links">
          {isAuthenticated ? (
            <>
              <Link to="/upload">Upload</Link>
              <Link to="/status">Status</Link>
              <button onClick={handleLogout} className="btn btn-primary">Logout</button>
            </>
          ) : (
            <Link to="/login" className="btn btn-primary">Login</Link>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
