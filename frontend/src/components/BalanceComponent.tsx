import React, { useState, useEffect } from 'react';
import { userAPI, UserBalanceResponse } from '../api/user';
import { useAuth } from '../contexts/AuthContext';

interface BalanceComponentProps {
  compact?: boolean;
  showLabel?: boolean;
}

const BalanceComponent: React.FC<BalanceComponentProps> = ({ 
  compact = false, 
  showLabel = true 
}) => {
  const { isAuthenticated } = useAuth();
  const [balance, setBalance] = useState<UserBalanceResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isAuthenticated) {
      loadBalance();
    } else {
      setLoading(false);
    }
  }, [isAuthenticated]);

  const loadBalance = async () => {
    try {
      setLoading(true);
      setError(null);
      const balanceData = await userAPI.getUserBalance();
      setBalance(balanceData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка загрузки баланса');
      console.error('Failed to load balance:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatBalance = (amount: number) => {
    return new Intl.NumberFormat('ru-RU', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(amount);
  };

  // Не показываем компонент, если пользователь не авторизован
  if (!isAuthenticated) {
    return null;
  }

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: compact ? 4 : 8,
        color: '#718096',
        fontSize: compact ? 14 : 16
      }}>
        <div style={{
          width: compact ? 12 : 16,
          height: compact ? 12 : 16,
          border: '2px solid #e2e8f0',
          borderTop: '2px solid #3182ce',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite'
        }} />
        {!compact && <span>Загрузка...</span>}
      </div>
    );
  }

  if (error || !balance) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: compact ? 4 : 8,
        color: '#e53e3e',
        fontSize: compact ? 14 : 16
      }}>
        <span style={{ fontSize: compact ? 16 : 18 }}>⚠️</span>
        {!compact && <span>Ошибка</span>}
      </div>
    );
  }

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: compact ? 4 : 8,
      color: '#2d3748',
      fontSize: compact ? 14 : 16,
      fontWeight: 500
    }}>
      <span style={{ fontSize: compact ? 16 : 18 }}>💰</span>
      {showLabel && !compact && <span>Баланс:</span>}
      <span style={{
        color: balance.balance > 0 ? '#38a169' : '#e53e3e',
        fontWeight: 600
      }}>
        {formatBalance(balance.balance)}
      </span>
    </div>
  );
};

export default BalanceComponent;
