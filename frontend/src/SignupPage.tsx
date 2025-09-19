import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { signUp, confirmSignUp, signIn } from '@aws-amplify/auth';
import './assets/css/SignupPage.css';

interface SignupPageProps {
  setIsAuthenticated: (isAuthenticated: boolean) => void;
}

const SignupPage: React.FC<SignupPageProps> = ({ setIsAuthenticated }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [confirmationCode, setConfirmationCode] = useState('');
  const [error, setError] = useState('');
  const [newUser, setNewUser] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    try {
      const { nextStep } = await signUp({
        username: email,
        password,
      });
      setNewUser(nextStep.signUpStep);
    } catch (error: any) {
      setError(error.message);
    }
  };

  const handleConfirmationSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await confirmSignUp({ username: email, confirmationCode });
      await signIn({ username: email, password });
      setIsAuthenticated(true);
      navigate('/upload');
    } catch (error: any) {
      setError(error.message);
    }
  };

  const renderConfirmationForm = () => {
    return (
      <div className="auth-page">
        <div className="auth-card">
          <h2 className="auth-title">Confirm Your Email</h2>
          <p className="auth-subtitle">We've sent a confirmation code to your email.</p>
          <form onSubmit={handleConfirmationSubmit}>
            <div className="form-group">
              <label htmlFor="confirmationCode">Confirmation Code</label>
              <input
                type="text"
                id="confirmationCode"
                name="confirmationCode"
                required
                className="form-control"
                value={confirmationCode}
                onChange={(e) => setConfirmationCode(e.target.value)}
              />
            </div>
            {error && <p className="error-message">{error}</p>}
            <button type="submit" className="btn btn-primary btn-gradient">Confirm</button>
          </form>
        </div>
      </div>
    );
  };

  const renderSignupForm = () => {
    return (
      <div className="auth-page">
        <div className="auth-card">
          <h2 className="auth-title">Create an Account</h2>
          <p className="auth-subtitle">Start your journey with us today</p>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              name="email"
              required
              className="form-control"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              required
              className="form-control"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          <div className="form-group">
            <label htmlFor="confirm-password">Confirm Password</label>
            <input
              type="password"
              id="confirm-password"
              name="confirm-password"
              required
              className="form-control"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
            />
          </div>
          {error && <p className="error-message">{error}</p>}
          <button type="submit" className="btn btn-primary btn-gradient">Sign Up</button>
          </form>
          <p className="auth-switch">
            Already have an account? <Link to="/login">Login</Link>
          </p>
        </div>
      </div>
    );
  };

  return (
    <div>
      {newUser === null ? renderSignupForm() : renderConfirmationForm()}
    </div>
  );
};

export default SignupPage;
