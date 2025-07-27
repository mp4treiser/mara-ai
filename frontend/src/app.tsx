import React from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import LoginPage from "./pages/LoginPage";
import HomePage from "./pages/HomePage";
import RegisterPage from "./pages/RegisterPage";

const App = () => {
  return (
    <Router>
      <div style={{ minHeight: '100vh', background: '#f7f7fa', fontFamily: 'sans-serif' }}>
        {/* Header */}
        <header style={{
          width: '100%',
          height: 64,
          background: '#fff',
          boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0 16px 0 40px',
          position: 'fixed',
          top: 0,
          left: 0,
          zIndex: 10,
          boxSizing: 'border-box'
        }}>
          <Link to="/" style={{ textDecoration: 'none' }}>
            <div style={{ fontWeight: 700, fontSize: 24, color: '#2d3748', letterSpacing: 1, cursor: 'pointer' }}>
              mara-ai
            </div>
          </Link>
          <Link to="/login" style={{ textDecoration: 'none' }}>
            <button
              style={{
                background: '#2d3748',
                color: '#fff',
                border: 'none',
                borderRadius: 6,
                padding: '10px 24px',
                fontSize: 16,
                fontWeight: 500,
                cursor: 'pointer',
                transition: 'background 0.2s',
                boxShadow: '0 1px 4px rgba(0,0,0,0.04)',
                marginRight: 8
              }}
            >
              Войти
            </button>
          </Link>
        </header>

        {/* Main content */}
        <main style={{
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          paddingTop: 100
        }}>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
};

export default App;
