import React, { useEffect, useMemo, useState, useCallback } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import './App.css';
import Dashboard from './Table';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import axios from 'axios';
import Login from './pages/Login';

const PrivateRoute = ({ token, children }) => {
    const location = useLocation();
    if (!token) {
        return <Navigate to="/login" replace state={{ from: location }} />;
    }
    return children;
};

function App() {
  const [token, setToken] = useState(() => localStorage.getItem('auth_token'));

  const applyAuthHeader = useCallback(
    (value) => {
      if (value) {
        axios.defaults.headers.common.Authorization = `Bearer ${value}`;
      } else {
        delete axios.defaults.headers.common.Authorization;
      }
    },
    []
  );

  useEffect(() => {
    applyAuthHeader(token);
  }, [token, applyAuthHeader]);

  useEffect(() => {
    const interceptor = axios.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('auth_token');
          setToken(null);
        }
        return Promise.reject(error);
      }
    );
    return () => axios.interceptors.response.eject(interceptor);
  }, []);

  const handleLogin = useCallback((newToken) => {
    localStorage.setItem('auth_token', newToken);
    setToken(newToken);
  }, []);

  const handleLogout = useCallback(() => {
    localStorage.removeItem('auth_token');
    setToken(null);
  }, []);

  return (
    <BrowserRouter>
      <div className="App">
        <Routes>
          <Route path="/login" element={<Login onLogin={handleLogin} />} />
          <Route
            path="/*"
            element={
              <PrivateRoute token={token}>
                <Dashboard onLogout={handleLogout} />
              </PrivateRoute>
            }
          />
        </Routes>
        <ToastContainer position="top-right" theme="colored" autoClose={3000} />
      </div>
    </BrowserRouter>
  );
}

export default App;
