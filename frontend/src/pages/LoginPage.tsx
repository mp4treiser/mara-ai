import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";

const LoginPage = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Реализовать авторизацию
    alert("Вход по email/паролю не реализован");
  };

  const handleGoogleLogin = () => {
    // TODO: Реализовать OAuth через Google
    alert("Вход через Google не реализован");
  };

  return (
    <div style={{ width: 340, background: '#fff', padding: 32, borderRadius: 12, boxShadow: '0 2px 16px rgba(0,0,0,0.07)' }}>
      <h2 style={{ color: '#2d3748', marginBottom: 24 }}>Вход</h2>
      <form onSubmit={handleLogin}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={e => setEmail(e.target.value)}
          required
          style={{ width: '100%', padding: 10, marginBottom: 16, borderRadius: 6, border: '1px solid #cbd5e1', fontSize: 16 }}
        />
        <input
          type="password"
          placeholder="Пароль"
          value={password}
          onChange={e => setPassword(e.target.value)}
          required
          style={{ width: '100%', padding: 10, marginBottom: 24, borderRadius: 6, border: '1px solid #cbd5e1', fontSize: 16 }}
        />
        <button
          type="submit"
          style={{ width: '100%', background: '#2d3748', color: '#fff', border: 'none', borderRadius: 6, padding: '10px 0', fontSize: 16, fontWeight: 500, cursor: 'pointer', marginBottom: 16 }}
        >
          Войти
        </button>
      </form>
      <button
        onClick={handleGoogleLogin}
        style={{ width: '100%', background: '#fff', color: '#2d3748', border: '1px solid #2d3748', borderRadius: 6, padding: '10px 0', fontSize: 16, fontWeight: 500, cursor: 'pointer', marginBottom: 16 }}
      >
        Войти через Google
      </button>
      <div style={{ textAlign: 'center' }}>
        Нет аккаунта? <Link to="/register">Зарегистрироваться</Link>
      </div>
    </div>
  );
};

export default LoginPage; 