import React, { useState, useEffect } from 'react';
import { agentsAPI } from '../api/agents';

interface TelegramConfig {
  id: number;
  agent_id: number;
  user_id: number;
  bot_token: string;
  chat_id: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface TelegramConfigComponentProps {
  userAgentId: number;
  agentId: number;
}

const TelegramConfigComponent: React.FC<TelegramConfigComponentProps> = ({ 
  userAgentId, 
  agentId 
}) => {
  const [config, setConfig] = useState<TelegramConfig | null>(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  // const [settingWebhook, setSettingWebhook] = useState(false); // Отключено - используем aiogram
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  
  // Форма
  const [botToken, setBotToken] = useState('');
  const [chatId, setChatId] = useState('');
  const [isActive, setIsActive] = useState(true);
  const [testMessage, setTestMessage] = useState('Тестовое сообщение от mara-ai');

  useEffect(() => {
    loadConfig();
  }, [agentId]);

  const loadConfig = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Получаем конфигурацию Telegram для агента
      const response = await fetch(`/api/v1/user/agents/${agentId}/telegram-config`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const configData = await response.json();
        setConfig(configData);
        setBotToken(configData.bot_token || '');
        setChatId(configData.chat_id || '');
        setIsActive(configData.is_active || false);
      } else if (response.status === 404) {
        // Конфигурация не найдена - это нормально
        setConfig(null);
      } else {
        throw new Error('Ошибка загрузки конфигурации');
      }
    } catch (err) {
      console.error('Ошибка загрузки конфигурации Telegram:', err);
      setError(err instanceof Error ? err.message : 'Ошибка загрузки конфигурации');
    } finally {
      setLoading(false);
    }
  };

  const saveConfig = async () => {
    try {
      setSaving(true);
      setError(null);
      setSuccess(null);

      const configData = {
        bot_token: botToken.trim(),
        chat_id: chatId.trim(),
        is_active: isActive
      };

      const url = config 
        ? `/api/v1/user/agents/${agentId}/telegram-config`  // Обновление
        : `/api/v1/user/agents/${agentId}/telegram-config`; // Создание

      const method = config ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(configData)
      });

      if (response.ok) {
        const savedConfig = await response.json();
        setConfig(savedConfig);
        setSuccess('Конфигурация Telegram сохранена успешно!');
        setShowForm(false);
        await loadConfig(); // Перезагружаем конфигурацию
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Ошибка сохранения конфигурации');
      }
    } catch (err) {
      console.error('Ошибка сохранения конфигурации:', err);
      setError(err instanceof Error ? err.message : 'Ошибка сохранения конфигурации');
    } finally {
      setSaving(false);
    }
  };

  const testConfig = async () => {
    try {
      setTesting(true);
      setError(null);
      setSuccess(null);

      const response = await fetch(`/api/v1/user/agents/${agentId}/telegram-config/test`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: testMessage })
      });

      if (response.ok) {
        setSuccess('Тестовое сообщение отправлено успешно!');
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Ошибка отправки тестового сообщения');
      }
    } catch (err) {
      console.error('Ошибка тестирования конфигурации:', err);
      setError(err instanceof Error ? err.message : 'Ошибка тестирования конфигурации');
    } finally {
      setTesting(false);
    }
  };

  // Функция setupWebhook отключена - используем aiogram для мониторинга

  const deleteConfig = async () => {
    if (!window.confirm('Вы уверены, что хотите удалить конфигурацию Telegram?')) {
      return;
    }

    try {
      setSaving(true);
      setError(null);
      setSuccess(null);

      const response = await fetch(`/api/v1/user/agents/${agentId}/telegram-config`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (response.ok) {
        setConfig(null);
        setBotToken('');
        setChatId('');
        setIsActive(false);
        setSuccess('Конфигурация Telegram удалена успешно!');
        setShowForm(false);
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Ошибка удаления конфигурации');
      }
    } catch (err) {
      console.error('Ошибка удаления конфигурации:', err);
      setError(err instanceof Error ? err.message : 'Ошибка удаления конфигурации');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '20px' }}>
        <div>Загрузка конфигурации Telegram...</div>
      </div>
    );
  }

  return (
    <div style={{ 
      background: '#fff', 
      padding: '20px', 
      borderRadius: '8px', 
      border: '1px solid #e2e8f0',
      marginTop: '20px'
    }}>
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        marginBottom: '16px' 
      }}>
        <h4 style={{ margin: 0, color: '#2d3748' }}>📱 Настройки Telegram</h4>
        {!showForm && (
          <button
            onClick={() => setShowForm(true)}
            style={{
              background: '#3182ce',
              color: '#fff',
              border: 'none',
              borderRadius: '6px',
              padding: '8px 16px',
              fontSize: '14px',
              cursor: 'pointer',
              transition: 'background 0.2s'
            }}
          >
            {config ? 'Изменить' : 'Настроить'}
          </button>
        )}
      </div>

      {error && (
        <div style={{ 
          marginBottom: '16px', 
          padding: '12px', 
          background: '#fed7d7', 
          color: '#c53030', 
          borderRadius: '6px',
          border: '1px solid #feb2b2'
        }}>
          {error}
        </div>
      )}

      {success && (
        <div style={{ 
          marginBottom: '16px', 
          padding: '12px', 
          background: '#c6f6d5', 
          color: '#2f855a', 
          borderRadius: '6px',
          border: '1px solid #9ae6b4'
        }}>
          {success}
        </div>
      )}

      {config && !showForm && (
        <div style={{ 
          padding: '16px', 
          background: '#f7fafc', 
          borderRadius: '6px',
          marginBottom: '16px'
        }}>
          <div style={{ marginBottom: '8px' }}>
            <strong>Статус:</strong> {config.is_active ? '✅ Активен' : '❌ Неактивен'}
          </div>
          <div style={{ marginBottom: '8px' }}>
            <strong>Chat ID:</strong> {config.chat_id}
          </div>
          <div style={{ marginBottom: '8px' }}>
            <strong>Bot Token:</strong> {config.bot_token.substring(0, 10)}...
          </div>
          <div style={{ fontSize: '12px', color: '#718096' }}>
            Обновлено: {new Date(config.updated_at).toLocaleString('ru-RU')}
          </div>
        </div>
      )}

      {showForm && (
        <div style={{ marginBottom: '20px' }}>
          <div style={{ marginBottom: '16px' }}>
            <label style={{ 
              display: 'block', 
              marginBottom: '8px', 
              fontWeight: '500',
              color: '#2d3748'
            }}>
              Bot Token:
            </label>
            <input
              type="text"
              value={botToken}
              onChange={(e) => setBotToken(e.target.value)}
              placeholder="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
              style={{
                width: '100%',
                padding: '8px 12px',
                border: '1px solid #e2e8f0',
                borderRadius: '6px',
                fontSize: '14px'
              }}
            />
            <div style={{ fontSize: '12px', color: '#718096', marginTop: '4px' }}>
              Получите токен у @BotFather в Telegram
            </div>
          </div>

          <div style={{ marginBottom: '16px' }}>
            <label style={{ 
              display: 'block', 
              marginBottom: '8px', 
              fontWeight: '500',
              color: '#2d3748'
            }}>
              Chat ID:
            </label>
            <input
              type="text"
              value={chatId}
              onChange={(e) => setChatId(e.target.value)}
              placeholder="-1001234567890"
              style={{
                width: '100%',
                padding: '8px 12px',
                border: '1px solid #e2e8f0',
                borderRadius: '6px',
                fontSize: '14px'
              }}
            />
            <div style={{ fontSize: '12px', color: '#718096', marginTop: '4px' }}>
              ID чата, куда будут отправляться сообщения
            </div>
          </div>

          <div style={{ marginBottom: '16px' }}>
            <label style={{ 
              display: 'flex', 
              alignItems: 'center', 
              cursor: 'pointer'
            }}>
              <input
                type="checkbox"
                checked={isActive}
                onChange={(e) => setIsActive(e.target.checked)}
                style={{ marginRight: '8px' }}
              />
              <span style={{ color: '#2d3748' }}>Активна</span>
            </label>
          </div>

          <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
            <button
              onClick={saveConfig}
              disabled={saving || !botToken.trim() || !chatId.trim()}
              style={{
                background: saving ? '#cbd5e0' : '#38a169',
                color: '#fff',
                border: 'none',
                borderRadius: '6px',
                padding: '10px 20px',
                fontSize: '14px',
                cursor: saving ? 'not-allowed' : 'pointer',
                transition: 'background 0.2s'
              }}
            >
              {saving ? 'Сохранение...' : 'Сохранить'}
            </button>

            <button
              onClick={() => setShowForm(false)}
              style={{
                background: '#e2e8f0',
                color: '#4a5568',
                border: 'none',
                borderRadius: '6px',
                padding: '10px 20px',
                fontSize: '14px',
                cursor: 'pointer',
                transition: 'background 0.2s'
              }}
            >
              Отмена
            </button>

            {config && (
              <button
                onClick={deleteConfig}
                disabled={saving}
                style={{
                  background: saving ? '#cbd5e0' : '#e53e3e',
                  color: '#fff',
                  border: 'none',
                  borderRadius: '6px',
                  padding: '10px 20px',
                  fontSize: '14px',
                  cursor: saving ? 'not-allowed' : 'pointer',
                  transition: 'background 0.2s'
                }}
              >
                Удалить
              </button>
            )}
          </div>
        </div>
      )}

      {config && config.is_active && (
        <div style={{ 
          padding: '16px', 
          background: '#f0fff4', 
          borderRadius: '6px',
          border: '1px solid #9ae6b4'
        }}>
          <h5 style={{ margin: '0 0 12px 0', color: '#2f855a' }}>Тестирование</h5>
          <div style={{ marginBottom: '12px' }}>
            <input
              type="text"
              value={testMessage}
              onChange={(e) => setTestMessage(e.target.value)}
              placeholder="Введите тестовое сообщение"
              style={{
                width: '100%',
                padding: '8px 12px',
                border: '1px solid #9ae6b4',
                borderRadius: '6px',
                fontSize: '14px'
              }}
            />
          </div>
          <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
            <button
              onClick={testConfig}
              disabled={testing || !testMessage.trim()}
              style={{
                background: testing ? '#cbd5e0' : '#38a169',
                color: '#fff',
                border: 'none',
                borderRadius: '6px',
                padding: '8px 16px',
                fontSize: '14px',
                cursor: testing ? 'not-allowed' : 'pointer',
                transition: 'background 0.2s'
              }}
            >
              {testing ? 'Отправка...' : 'Отправить тестовое сообщение'}
            </button>

            {/* Webhook кнопка отключена - используем aiogram для мониторинга */}
          </div>
        </div>
      )}
    </div>
  );
};

export default TelegramConfigComponent;
