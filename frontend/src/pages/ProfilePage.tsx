import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import WalletComponent from '../components/WalletComponent';
import SubscriptionComponent from '../components/SubscriptionComponent';

type TabType = 'profile' | 'wallet' | 'subscription';

const ProfilePage = () => {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState<TabType>('profile');

  if (!user) {
    return (
      <div style={{ textAlign: 'center', padding: '20px' }}>
        Загрузка профиля...
      </div>
    );
  }

  const renderTabContent = () => {
    switch (activeTab) {
      case 'wallet':
        return <WalletComponent />;
      case 'subscription':
        return <SubscriptionComponent />;
      default:
        return (
          <div style={{ 
            width: 600, 
            background: '#fff', 
            padding: 32, 
            borderRadius: 12, 
            boxShadow: '0 2px 16px rgba(0,0,0,0.07)' 
          }}>
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center', 
              marginBottom: 32 
            }}>
              <h2 style={{ color: '#2d3748', margin: 0 }}>Профиль пользователя</h2>
              <button
                onClick={logout}
                style={{
                  background: '#e53e3e',
                  color: '#fff',
                  border: 'none',
                  borderRadius: 6,
                  padding: '8px 16px',
                  fontSize: 14,
                  fontWeight: 500,
                  cursor: 'pointer',
                  transition: 'background 0.2s'
                }}
              >
                Выйти
              </button>
            </div>

            <div style={{ marginBottom: 24 }}>
              <label style={{ 
                display: 'block', 
                fontSize: 14, 
                fontWeight: 600, 
                color: '#4a5568', 
                marginBottom: 4 
              }}>
                ID пользователя
              </label>
              <div style={{ 
                padding: 12, 
                background: '#f7fafc', 
                borderRadius: 6, 
                border: '1px solid #e2e8f0',
                fontSize: 16,
                color: '#2d3748'
              }}>
                {user.id}
              </div>
            </div>

            <div style={{ marginBottom: 24 }}>
              <label style={{ 
                display: 'block', 
                fontSize: 14, 
                fontWeight: 600, 
                color: '#4a5568', 
                marginBottom: 4 
              }}>
                Email
              </label>
              <div style={{ 
                padding: 12, 
                background: '#f7fafc', 
                borderRadius: 6, 
                border: '1px solid #e2e8f0',
                fontSize: 16,
                color: '#2d3748'
              }}>
                {user.email}
              </div>
            </div>

            <div style={{ marginBottom: 24 }}>
              <label style={{ 
                display: 'block', 
                fontSize: 14, 
                fontWeight: 600, 
                color: '#4a5568', 
                marginBottom: 4 
              }}>
                Имя
              </label>
              <div style={{ 
                padding: 12, 
                background: '#f7fafc', 
                borderRadius: 6, 
                border: '1px solid #e2e8f0',
                fontSize: 16,
                color: '#2d3748'
              }}>
                {user.first_name}
              </div>
            </div>

            <div style={{ marginBottom: 24 }}>
              <label style={{ 
                display: 'block', 
                fontSize: 14, 
                fontWeight: 600, 
                color: '#4a5568', 
                marginBottom: 4 
              }}>
                Фамилия
              </label>
              <div style={{ 
                padding: 12, 
                background: '#f7fafc', 
                borderRadius: 6, 
                border: '1px solid #e2e8f0',
                fontSize: 16,
                color: '#2d3748'
              }}>
                {user.last_name}
              </div>
            </div>

            <div style={{ marginBottom: 24 }}>
              <label style={{ 
                display: 'block', 
                fontSize: 14, 
                fontWeight: 600, 
                color: '#4a5568', 
                marginBottom: 4 
              }}>
                Компания
              </label>
              <div style={{ 
                padding: 12, 
                background: '#f7fafc', 
                borderRadius: 6, 
                border: '1px solid #e2e8f0',
                fontSize: 16,
                color: '#2d3748'
              }}>
                {user.company}
              </div>
            </div>

            <div style={{ marginBottom: 24 }}>
              <label style={{ 
                display: 'block', 
                fontSize: 14, 
                fontWeight: 600, 
                color: '#4a5568', 
                marginBottom: 4 
              }}>
                Статус
              </label>
              <div style={{ 
                padding: 12, 
                background: '#f7fafc', 
                borderRadius: 6, 
                border: '1px solid #e2e8f0',
                fontSize: 16,
                color: '#2d3748'
              }}>
                <span style={{ 
                  color: user.is_active ? '#38a169' : '#e53e3e',
                  fontWeight: 600
                }}>
                  {user.is_active ? 'Активен' : 'Неактивен'}
                </span>
              </div>
            </div>

            <div style={{ 
              marginTop: 32, 
              padding: 16, 
              background: '#f0fff4', 
              borderRadius: 8, 
              border: '1px solid #9ae6b4' 
            }}>
              <h4 style={{ margin: '0 0 8px 0', color: '#22543d' }}>
                🎉 Добро пожаловать в mara-ai!
              </h4>
              <p style={{ margin: 0, color: '#22543d', fontSize: 14 }}>
                Вы успешно вошли в систему. Теперь вы можете использовать все возможности платформы.
              </p>
            </div>
          </div>
        );
    }
  };

  return (
    <div style={{ 
      width: '100%', 
      maxWidth: 1200, 
      margin: '0 auto', 
      padding: '0 20px' 
    }}>
      {/* Навигационные табы */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        marginBottom: 32,
        background: '#fff',
        borderRadius: 12,
        padding: 8,
        boxShadow: '0 2px 16px rgba(0,0,0,0.07)',
        maxWidth: 600,
        margin: '0 auto 32px auto'
      }}>
        <button
          onClick={() => setActiveTab('profile')}
          style={{
            background: activeTab === 'profile' ? '#3182ce' : 'transparent',
            color: activeTab === 'profile' ? '#fff' : '#4a5568',
            border: 'none',
            borderRadius: 8,
            padding: '12px 24px',
            fontSize: 14,
            fontWeight: 600,
            cursor: 'pointer',
            transition: 'all 0.2s',
            flex: 1,
            margin: '0 4px'
          }}
        >
          Профиль
        </button>
        <button
          onClick={() => setActiveTab('wallet')}
          style={{
            background: activeTab === 'wallet' ? '#3182ce' : 'transparent',
            color: activeTab === 'wallet' ? '#fff' : '#4a5568',
            border: 'none',
            borderRadius: 8,
            padding: '12px 24px',
            fontSize: 14,
            fontWeight: 600,
            cursor: 'pointer',
            transition: 'all 0.2s',
            flex: 1,
            margin: '0 4px'
          }}
        >
          Кошелек
        </button>
        <button
          onClick={() => setActiveTab('subscription')}
          style={{
            background: activeTab === 'subscription' ? '#3182ce' : 'transparent',
            color: activeTab === 'subscription' ? '#fff' : '#4a5568',
            border: 'none',
            borderRadius: 8,
            padding: '12px 24px',
            fontSize: 14,
            fontWeight: 600,
            cursor: 'pointer',
            transition: 'all 0.2s',
            flex: 1,
            margin: '0 4px'
          }}
        >
          Подписки
        </button>
      </div>

      {/* Содержимое активного таба */}
      <div style={{ display: 'flex', justifyContent: 'center' }}>
        {renderTabContent()}
      </div>
    </div>
  );
};

export default ProfilePage; 