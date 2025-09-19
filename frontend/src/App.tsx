import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import { Amplify } from 'aws-amplify';
import { getCurrentUser } from '@aws-amplify/auth';
import awsExports from './aws-exports';
import HomePage from './HomePage';
import UploadPage from './UploadPage';
import StatusPage from './StatusPage';
import LoginPage from './LoginPage';
import SignupPage from './SignupPage';
import Navbar from './Navbar';

Amplify.configure(awsExports);

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkUser = async () => {
      try {
        await getCurrentUser();
        setIsAuthenticated(true);
      } catch (error) {
        setIsAuthenticated(false);
      }
      setIsLoading(false);
    };

    checkUser();
  }, []);

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <Router>
      <Navbar isAuthenticated={isAuthenticated} setIsAuthenticated={setIsAuthenticated} />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/home" element={<HomePage />} />
        <Route
          path="/upload"
          element={isAuthenticated ? <UploadPage /> : <Navigate to="/login" />}
        />
        <Route
          path="/status"
          element={isAuthenticated ? <StatusPage /> : <Navigate to="/login" />}
        />
        <Route path="/signup" element={<SignupPage setIsAuthenticated={setIsAuthenticated} />} />
        <Route path="/login" element={<LoginPage setIsAuthenticated={setIsAuthenticated} />} />
      </Routes>
    </Router>
  );
}

export default App;
