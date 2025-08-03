import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { authAPI } from "../api/auth";

const RegisterPage = () => {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    confirm_password: "",
    company: "",
    first_name: "",
    last_name: ""
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (formData.password !== formData.confirm_password) {
      setError("Пароли не совпадают");
      return;
    }

    if (formData.password.length < 6) {
      setError("Пароль должен содержать минимум 6 символов");
      return;
    }

    setError("");
    setIsLoading(true);

    try {
      await authAPI.register(formData);
      // После успешной регистрации перенаправляем на страницу входа
      navigate("/login", { 
        state: { message: "Регистрация успешна! Теперь вы можете войти в систему." }
      });
    } catch (error) {
      setError(error instanceof Error ? error.message : "Ошибка регистрации");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ width: 400, background: '#fff', padding: 32, borderRadius: 12, boxShadow: '0 2px 16px rgba(0,0,0,0.07)' }}>
      <h2 style={{ color: '#2d3748', marginBottom: 24 }}>Регистрация</h2>
      
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

      <form onSubmit={handleRegister}>
        <input
          type="email"
          name="email"
          placeholder="Email"
          value={formData.email}
          onChange={handleChange}
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
          type="text"
          name="first_name"
          placeholder="Имя"
          value={formData.first_name}
          onChange={handleChange}
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
          type="text"
          name="last_name"
          placeholder="Фамилия"
          value={formData.last_name}
          onChange={handleChange}
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
          type="text"
          name="company"
          placeholder="Наименование компании"
          value={formData.company}
          onChange={handleChange}
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
          name="password"
          placeholder="Пароль"
          value={formData.password}
          onChange={handleChange}
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
          name="confirm_password"
          placeholder="Повторите пароль"
          value={formData.confirm_password}
          onChange={handleChange}
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
          {isLoading ? 'Регистрация...' : 'Зарегистрироваться'}
        </button>
      </form>
      
      <div style={{ textAlign: 'center' }}>
        Уже есть аккаунт? <Link to="/login" style={{ color: '#3182ce', textDecoration: 'none' }}>Войти</Link>
      </div>
    </div>
  );
};

export default RegisterPage; 