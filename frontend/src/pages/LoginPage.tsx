import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

const LoginPage = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      await login({ email, password });
      // После успешного входа перенаправляем на профиль
      navigate("/profile");
    } catch (error) {
      setError(error instanceof Error ? error.message : "Ошибка входа в систему");
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleLogin = () => {
    // TODO: Реализовать OAuth через Google
    alert("Вход через Google не реализован");
  };

  return (
    <div style={{ width: 340, background: '#fff', padding: 32, borderRadius: 12, boxShadow: '0 2px 16px rgba(0,0,0,0.07)' }}>
      <h2 style={{ color: '#2d3748', marginBottom: 24 }}>Вход</h2>
      
      {error && (
        <div style={{
          background: '#fed7d7',
          color: '#c53030',
          padding: 12,
          borderRadius: 6,
          marginBottom: 16,
          fontSize: 14,
          border: '1px solid #feb2b2'
        }}>
          {error}
        </div>
      )}

      <form onSubmit={handleLogin}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={e => setEmail(e.target.value)}
          required
          disabled={isLoading}
          style={{ 
            width: '100%', 
            padding: 10, 
            marginBottom: 16, 
            borderRadius: 6, 
            border: '1px solid #cbd5e1', 
            fontSize: 16,
            opacity: isLoading ? 0.7 : 1
          }}
        />
        <input
          type="password"
          placeholder="Пароль"
          value={password}
          onChange={e => setPassword(e.target.value)}
          required
          disabled={isLoading}
          style={{ 
            width: '100%', 
            padding: 10, 
            marginBottom: 24, 
            borderRadius: 6, 
            border: '1px solid #cbd5e1', 
            fontSize: 16,
            opacity: isLoading ? 0.7 : 1
          }}
        />
        <button
          type="submit"
          disabled={isLoading}
          style={{ 
            width: '100%', 
            background: isLoading ? '#a0aec0' : '#2d3748', 
            color: '#fff', 
            border: 'none', 
            borderRadius: 6, 
            padding: '10px 0', 
            fontSize: 16, 
            fontWeight: 500, 
            cursor: isLoading ? 'not-allowed' : 'pointer', 
            marginBottom: 16,
            transition: 'background 0.2s'
          }}
        >
          {isLoading ? 'Вход...' : 'Войти'}
        </button>
      </form>
      
      <button
        onClick={handleGoogleLogin}
        disabled={isLoading}
        style={{ 
          width: '100%', 
          background: '#fff', 
          color: '#2d3748', 
          border: '1px solid #2d3748', 
          borderRadius: 6, 
          padding: '10px 0', 
          fontSize: 16, 
          fontWeight: 500, 
          cursor: isLoading ? 'not-allowed' : 'pointer', 
          marginBottom: 16,
          opacity: isLoading ? 0.7 : 1
        }}
      >
        Войти через Google
      </button>
      
      <div style={{ textAlign: 'center' }}>
        Нет аккаунта? <Link to="/register" style={{ color: '#3182ce', textDecoration: 'none' }}>Зарегистрироваться</Link>
      </div>
    </div>
  );
};

export default LoginPage; 