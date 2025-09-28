import React, { useState, useEffect } from 'react';

interface AiogramBotManagementComponentProps {
  userAgentId: number;
  agentId: number;
}

interface AiogramBotStatus {
  bot_token: string;
  is_active: boolean;
  monitored_chats_count: number;
  chat_ids: string[];
}

const AiogramBotManagementComponent: React.FC<AiogramBotManagementComponentProps> = ({ 
  userAgentId, 
  agentId 
}) => {
  const [botStatus, setBotStatus] = useState<AiogramBotStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  useEffect(() => {
    loadBotStatus();
  }, [agentId]);

  const loadBotStatus = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`/api/v1/user/agents/${agentId}/aiogram-bot/status`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setBotStatus(data);
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Ошибка загрузки статуса aiogram бота');
      }
    } catch (err) {
      console.error('Ошибка загрузки статуса aiogram бота:', err);
      setError(err instanceof Error ? err.message : 'Ошибка загрузки статуса aiogram бота');
    } finally {
      setLoading(false);
    }
  };

  const restartBot = async () => {
    try {
      setActionLoading('restart');
      setError(null);
      setSuccess(null);
      
      const response = await fetch(`/api/v1/user/agents/${agentId}/aiogram-bot/restart`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setSuccess(data.message || 'Команда перезапуска отправлена!');
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Ошибка перезапуска aiogram бота');
      }
    } catch (err) {
      console.error('Ошибка перезапуска aiogram бота:', err);
      setError(err instanceof Error ? err.message : 'Ошибка перезапуска aiogram бота');
    } finally {
      setActionLoading(null);
    }
  };

  if (loading) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <p>Загрузка статуса aiogram бота...</p>
      </div>
    );
  }

  return (
    <div style={{ 
      marginTop: '20px', 
      padding: '20px', 
      border: '1px solid #e2e8f0', 
      borderRadius: '8px', 
      background: '#fff' 
    }}>
      <h3 style={{ color: '#2d3748', marginBottom: '20px' }}>
        <span role="img" aria-label="robot">🤖</span> Управление Aiogram ботом
      </h3>

      {error && (
        <div style={{ 
          padding: '10px', 
          background: '#fed7d7', 
          color: '#c53030', 
          borderRadius: '6px', 
          marginBottom: '15px' 
        }}>
          {error}
        </div>
      )}

      {success && (
        <div style={{ 
          padding: '10px', 
          background: '#c6f6d5', 
          color: '#2f855a', 
          borderRadius: '6px', 
          marginBottom: '15px' 
        }}>
          {success}
        </div>
      )}

      {botStatus && (
        <div style={{ marginBottom: '20px' }}>
          <div style={{ 
            padding: '15px', 
            background: botStatus.is_active ? '#f0fff4' : '#fef5e7', 
            border: `1px solid ${botStatus.is_active ? '#9ae6b4' : '#fbd38d'}`, 
            borderRadius: '6px',
            marginBottom: '15px'
          }}>
            <h4 style={{ margin: '0 0 10px 0', color: '#2d3748' }}>
              Статус aiogram бота: {botStatus.is_active ? '🟢 Активен' : '🔴 Неактивен'}
            </h4>
            
            <p style={{ margin: '5px 0', fontSize: '14px', color: '#4a5568' }}>
              <strong>Токен бота:</strong> {botStatus.bot_token}
            </p>
            
            <p style={{ margin: '5px 0', fontSize: '14px', color: '#4a5568' }}>
              <strong>Мониторится чатов:</strong> {botStatus.monitored_chats_count}
            </p>
            
            {botStatus.chat_ids.length > 0 && (
              <p style={{ margin: '5px 0', fontSize: '14px', color: '#4a5568' }}>
                <strong>ID чатов:</strong> {botStatus.chat_ids.join(', ')}
              </p>
            )}
          </div>

          <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
            <button
              onClick={restartBot}
              disabled={actionLoading === 'restart'}
              style={{
                background: actionLoading === 'restart' ? '#cbd5e0' : '#3182ce',
                color: '#fff',
                border: 'none',
                borderRadius: '6px',
                padding: '10px 20px',
                fontSize: '14px',
                cursor: actionLoading === 'restart' ? 'not-allowed' : 'pointer',
                transition: 'background 0.2s'
              }}
            >
              {actionLoading === 'restart' ? 'Перезапуск...' : '🔄 Перезапустить бота'}
            </button>

            <button
              onClick={loadBotStatus}
              disabled={loading}
              style={{
                background: loading ? '#cbd5e0' : '#4a5568',
                color: '#fff',
                border: 'none',
                borderRadius: '6px',
                padding: '10px 20px',
                fontSize: '14px',
                cursor: loading ? 'not-allowed' : 'pointer',
                transition: 'background 0.2s'
              }}
            >
              {loading ? 'Обновление...' : '🔄 Обновить статус'}
            </button>
          </div>
        </div>
      )}

      <div style={{ 
        padding: '15px', 
        background: '#f7fafc', 
        borderRadius: '6px',
        fontSize: '14px',
        color: '#4a5568'
      }}>
        <h4 style={{ margin: '0 0 10px 0', color: '#2d3748' }}>Как работает aiogram бот:</h4>
        <ul style={{ margin: '0', paddingLeft: '20px' }}>
          <li>Бот работает в отдельном контейнере</li>
          <li>Автоматически мониторит указанные чаты</li>
          <li>При получении сообщения с ключевыми словами запускается анализ</li>
          <li>Агент анализирует сообщение и отправляет ответ в настроенный чат</li>
          <li>Бот работает независимо от основного приложения</li>
        </ul>
      </div>
    </div>
  );
};

export default AiogramBotManagementComponent;
