import React from 'react';
import { Link } from 'react-router-dom';
import './assets/css/LoginPage.css';

const LoginPage: React.FC = () => {
  return (
    <div className="auth-page">
      <div className="auth-card">
        <h2 className="auth-title">Welcome Back</h2>
        <p className="auth-subtitle">Enter your credentials to access your account</p>
        <form>
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input type="email" id="email" name="email" required className="form-control" />
          </div>
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input type="password" id="password" name="password" required className="form-control" />
          </div>
          <button type="submit" className="btn btn-primary btn-gradient">Login</button>
        </form>
        <p className="auth-switch">
          Don't have an account? <Link to="/signup">Sign Up</Link>
        </p>
      </div>
    </div>
  );
};

export default LoginPage;
