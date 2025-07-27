import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";

const RegisterPage = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [password2, setPassword2] = useState("");
  const [company, setCompany] = useState("");
  const navigate = useNavigate();

  const handleRegister = (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== password2) {
      alert("Пароли не совпадают");
      return;
    }
    // TODO: Реализовать регистрацию
    alert("Регистрация не реализована");
  };

  return (
    <div style={{ width: 360, background: '#fff', padding: 32, borderRadius: 12, boxShadow: '0 2px 16px rgba(0,0,0,0.07)' }}>
      <h2 style={{ color: '#2d3748', marginBottom: 24 }}>Регистрация</h2>
      <form onSubmit={handleRegister}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={e => setEmail(e.target.value)}
          required
          style={{ width: '100%', padding: 10, marginBottom: 16, borderRadius: 6, border: '1px solid #cbd5e1', fontSize: 16 }}
        />
        <input
          type="text"
          placeholder="Наименование компании"
          value={company}
          onChange={e => setCompany(e.target.value)}
          required
          style={{ width: '100%', padding: 10, marginBottom: 16, borderRadius: 6, border: '1px solid #cbd5e1', fontSize: 16 }}
        />
        <input
          type="password"
          placeholder="Пароль"
          value={password}
          onChange={e => setPassword(e.target.value)}
          required
          style={{ width: '100%', padding: 10, marginBottom: 16, borderRadius: 6, border: '1px solid #cbd5e1', fontSize: 16 }}
        />
        <input
          type="password"
          placeholder="Повторите пароль"
          value={password2}
          onChange={e => setPassword2(e.target.value)}
          required
          style={{ width: '100%', padding: 10, marginBottom: 24, borderRadius: 6, border: '1px solid #cbd5e1', fontSize: 16 }}
        />
        <button
          type="submit"
          style={{ width: '100%', background: '#2d3748', color: '#fff', border: 'none', borderRadius: 6, padding: '10px 0', fontSize: 16, fontWeight: 500, cursor: 'pointer', marginBottom: 16 }}
        >
          Зарегистрироваться
        </button>
      </form>
      <div style={{ textAlign: 'center' }}>
        Уже есть аккаунт? <Link to="/login">Войти</Link>
      </div>
    </div>
  );
};

export default RegisterPage; 