import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

const LoginPage = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    console.log('=== LOGIN START ===');
    console.log('Email:', email);
    console.log('Password length:', password.length);
    
    setErrorMessage("");
    setIsLoading(true);

    try {
      console.log('Calling login API...');
      await login({ email, password });
      console.log('Login successful!');
      navigate("/profile");
    } catch (error) {
      console.log('=== LOGIN ERROR ===');
      console.log('Error object:', error);
      
      const message = error instanceof Error ? error.message : "Ошибка входа в систему";
      console.log('Error message:', message);
      
      setErrorMessage(message);
      console.log('Error set to state:', message);
    } finally {
      setIsLoading(false);
      console.log('=== LOGIN END ===');
    }
  };

  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setEmail(e.target.value);
    if (errorMessage) {
      setErrorMessage("");
    }
  };

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setPassword(e.target.value);
    if (errorMessage) {
      setErrorMessage("");
    }
  };

  return (
    <div style={{ 
      width: 340, 
      background: '#fff', 
      padding: 32, 
      borderRadius: 12, 
      boxShadow: '0 2px 16px rgba(0,0,0,0.07)'
    }}>
      <h2 style={{ color: '#2d3748', marginBottom: 24 }}>Вход</h2>
      
      {/* ПРОСТОЕ ОТОБРАЖЕНИЕ ОШИБКИ */}
      {errorMessage && (
        <div 
          style={{
            background: '#fed7d7',
            color: '#c53030',
            padding: 16,
            borderRadius: 8,
            marginBottom: 20,
            fontSize: 14,
            border: '2px solid #feb2b2',
            fontWeight: '500',
            textAlign: 'center',
            boxShadow: '0 2px 8px rgba(197, 48, 48, 0.1)'
          }}
        >
          ⚠️ {errorMessage}
        </div>
      )}
      

      <form onSubmit={handleLogin}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={handleEmailChange}
          required
          disabled={isLoading}
          style={{ 
            width: '100%', 
            padding: 10, 
            marginBottom: 16, 
            borderRadius: 6, 
            border: errorMessage ? '2px solid #e53e3e' : '1px solid #cbd5e1', 
            fontSize: 16,
            opacity: isLoading ? 0.7 : 1
          }}
        />
        <input
          type="password"
          placeholder="Пароль"
          value={password}
          onChange={handlePasswordChange}
          required
          disabled={isLoading}
          style={{ 
            width: '100%', 
            padding: 10, 
            marginBottom: 24, 
            borderRadius: 6, 
            border: errorMessage ? '2px solid #e53e3e' : '1px solid #cbd5e1', 
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
            marginBottom: 16
          }}
        >
          {isLoading ? 'Вход...' : 'Войти'}
        </button>
      </form>
      
      <div style={{ textAlign: 'center' }}>
        Нет аккаунта? <Link to="/register" style={{ color: '#3182ce', textDecoration: 'none' }}>Зарегистрироваться</Link>
      </div>
    </div>
  );
};

export default LoginPage;
