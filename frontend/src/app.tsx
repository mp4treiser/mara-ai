import React from "react";
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./contexts/AuthContext";
import { ProtectedRoute } from "./components/ProtectedRoute";
import LoginPage from "./pages/LoginPage";
import HomePage from "./pages/HomePage";
import RegisterPage from "./pages/RegisterPage";
import ProfilePage from "./pages/ProfilePage";

// Компонент для условного отображения кнопок в хедере
const HeaderButtons = () => {
  const { isAuthenticated, logout } = useAuth();

  if (isAuthenticated) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <Link to="/profile" style={{ textDecoration: 'none' }}>
          <button
            style={{
              background: '#3182ce',
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
            Профиль
          </button>
        </Link>
        <button
          onClick={logout}
          style={{
            background: '#e53e3e',
            color: '#fff',
            border: 'none',
            borderRadius: 6,
            padding: '10px 24px',
            fontSize: 16,
            fontWeight: 500,
            cursor: 'pointer',
            transition: 'background 0.2s',
            boxShadow: '0 1px 4px rgba(0,0,0,0.04)'
          }}
        >
          Выйти
        </button>
      </div>
    );
  }

  return (
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
  );
};

// Компонент для перенаправления аутентифицированных пользователей
const RedirectIfAuthenticated = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        fontSize: '18px',
        color: '#666'
      }}>
        Загрузка...
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/profile" replace />;
  }

  return <>{children}</>;
};

const AppContent = () => {
  return (
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
        <HeaderButtons />
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
          <Route 
            path="/login" 
            element={
              <RedirectIfAuthenticated>
                <LoginPage />
              </RedirectIfAuthenticated>
            } 
          />
          <Route 
            path="/register" 
            element={
              <RedirectIfAuthenticated>
                <RegisterPage />
              </RedirectIfAuthenticated>
            } 
          />
          <Route 
            path="/profile" 
            element={
              <ProtectedRoute>
                <ProfilePage />
              </ProtectedRoute>
            } 
          />
        </Routes>
      </main>
    </div>
  );
};

const App = () => {
  return (
    <AuthProvider>
      <Router>
        <AppContent />
      </Router>
    </AuthProvider>
  );
};

export default App;
