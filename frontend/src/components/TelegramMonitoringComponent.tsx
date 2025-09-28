import React, { useState, useEffect } from 'react';

interface MonitoredChat {
  id: number;
  telegram_config_id: number;
  chat_id: string;
  chat_title: string | null;
  chat_type: string;
  is_active: boolean;
  keywords: string[] | null;
  created_at: string;
  updated_at: string;
}

interface TelegramMonitoringComponentProps {
  userAgentId: number;
  agentId: number;
}

const TelegramMonitoringComponent: React.FC<TelegramMonitoringComponentProps> = ({ 
  userAgentId, 
  agentId 
}) => {
  const [monitoredChats, setMonitoredChats] = useState<MonitoredChat[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);
  
  // Форма добавления
  const [newChatId, setNewChatId] = useState('');
  const [newChatTitle, setNewChatTitle] = useState('');
  const [newChatType, setNewChatType] = useState('group');
  const [newKeywords, setNewKeywords] = useState<string[]>([]);
  const [newKeywordInput, setNewKeywordInput] = useState('');

  useEffect(() => {
    loadMonitoredChats();
  }, [agentId]);

  const loadMonitoredChats = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`/api/v1/user/agents/${agentId}/telegram-config/monitored-chats`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const chats = await response.json();
        setMonitoredChats(chats);
      } else {
        throw new Error('Ошибка загрузки мониторингов');
      }
    } catch (err) {
      console.error('Ошибка загрузки мониторингов:', err);
      setError(err instanceof Error ? err.message : 'Ошибка загрузки мониторингов');
    } finally {
      setLoading(false);
    }
  };

  const addKeyword = () => {
    if (newKeywordInput.trim() && !newKeywords.includes(newKeywordInput.trim())) {
      setNewKeywords([...newKeywords, newKeywordInput.trim()]);
      setNewKeywordInput('');
    }
  };

  const removeKeyword = (index: number) => {
    setNewKeywords(newKeywords.filter((_, i) => i !== index));
  };

  const addMonitoredChat = async () => {
    try {
      setSaving(true);
      setError(null);
      setSuccess(null);

      const chatData = {
        chat_id: newChatId.trim(),
        chat_title: newChatTitle.trim() || null,
        chat_type: newChatType,
        keywords: newKeywords.length > 0 ? newKeywords : null
      };

      const response = await fetch(`/api/v1/user/agents/${agentId}/telegram-config/monitored-chats`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(chatData)
      });

      if (response.ok) {
        setSuccess('Мониторинг чата добавлен успешно!');
        setShowAddForm(false);
        setNewChatId('');
        setNewChatTitle('');
        setNewChatType('group');
        setNewKeywords([]);
        await loadMonitoredChats();
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Ошибка добавления мониторинга');
      }
    } catch (err) {
      console.error('Ошибка добавления мониторинга:', err);
      setError(err instanceof Error ? err.message : 'Ошибка добавления мониторинга');
    } finally {
      setSaving(false);
    }
  };

  const toggleChatStatus = async (chatId: number, isActive: boolean) => {
    try {
      setSaving(true);
      setError(null);

      const response = await fetch(`/api/v1/user/agents/${agentId}/telegram-config/monitored-chats/${chatId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ is_active: !isActive })
      });

      if (response.ok) {
        setSuccess(`Мониторинг чата ${!isActive ? 'активирован' : 'деактивирован'}!`);
        await loadMonitoredChats();
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Ошибка обновления мониторинга');
      }
    } catch (err) {
      console.error('Ошибка обновления мониторинга:', err);
      setError(err instanceof Error ? err.message : 'Ошибка обновления мониторинга');
    } finally {
      setSaving(false);
    }
  };

  const deleteMonitoredChat = async (chatId: number) => {
    if (!window.confirm('Вы уверены, что хотите удалить мониторинг этого чата?')) {
      return;
    }

    try {
      setSaving(true);
      setError(null);

      const response = await fetch(`/api/v1/user/agents/${agentId}/telegram-config/monitored-chats/${chatId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (response.ok) {
        setSuccess('Мониторинг чата удален успешно!');
        await loadMonitoredChats();
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Ошибка удаления мониторинга');
      }
    } catch (err) {
      console.error('Ошибка удаления мониторинга:', err);
      setError(err instanceof Error ? err.message : 'Ошибка удаления мониторинга');
    } finally {
      setSaving(false);
    }
  };

  const testMonitoredChat = async (chatId: number) => {
    try {
      setSaving(true);
      setError(null);
      setSuccess(null);

      const response = await fetch(`/api/v1/user/agents/${agentId}/telegram-config/monitored-chats/${chatId}/test`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        setSuccess('Тестовое сообщение отправлено успешно!');
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Ошибка отправки тестового сообщения');
      }
    } catch (err) {
      console.error('Ошибка тестирования мониторинга:', err);
      setError(err instanceof Error ? err.message : 'Ошибка тестирования мониторинга');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '20px' }}>
        <div>Загрузка мониторингов чатов...</div>
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
        <h4 style={{ margin: 0, color: '#2d3748' }}>🔍 Мониторинг чатов</h4>
        <button
          onClick={() => setShowAddForm(true)}
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
          Добавить чат
        </button>
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

      {showAddForm && (
        <div style={{ 
          padding: '20px', 
          background: '#f7fafc', 
          borderRadius: '8px',
          marginBottom: '20px',
          border: '1px solid #e2e8f0'
        }}>
          <h5 style={{ margin: '0 0 16px 0', color: '#2d3748' }}>Добавить чат для мониторинга</h5>
          
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
              value={newChatId}
              onChange={(e) => setNewChatId(e.target.value)}
              placeholder="-1001234567890 или @channel_name"
              style={{
                width: '100%',
                padding: '8px 12px',
                border: '1px solid #e2e8f0',
                borderRadius: '6px',
                fontSize: '14px'
              }}
            />
          </div>

          <div style={{ marginBottom: '16px' }}>
            <label style={{ 
              display: 'block', 
              marginBottom: '8px', 
              fontWeight: '500',
              color: '#2d3748'
            }}>
              Название чата (опционально):
            </label>
            <input
              type="text"
              value={newChatTitle}
              onChange={(e) => setNewChatTitle(e.target.value)}
              placeholder="Название чата для удобства"
              style={{
                width: '100%',
                padding: '8px 12px',
                border: '1px solid #e2e8f0',
                borderRadius: '6px',
                fontSize: '14px'
              }}
            />
          </div>

          <div style={{ marginBottom: '16px' }}>
            <label style={{ 
              display: 'block', 
              marginBottom: '8px', 
              fontWeight: '500',
              color: '#2d3748'
            }}>
              Тип чата:
            </label>
            <select
              value={newChatType}
              onChange={(e) => setNewChatType(e.target.value)}
              style={{
                width: '100%',
                padding: '8px 12px',
                border: '1px solid #e2e8f0',
                borderRadius: '6px',
                fontSize: '14px'
              }}
            >
              <option value="group">Группа</option>
              <option value="supergroup">Супергруппа</option>
              <option value="channel">Канал</option>
              <option value="private">Личный чат</option>
            </select>
          </div>

          <div style={{ marginBottom: '16px' }}>
            <label style={{ 
              display: 'block', 
              marginBottom: '8px', 
              fontWeight: '500',
              color: '#2d3748'
            }}>
              Ключевые слова (опционально):
            </label>
            <div style={{ display: 'flex', gap: '8px', marginBottom: '8px' }}>
              <input
                type="text"
                value={newKeywordInput}
                onChange={(e) => setNewKeywordInput(e.target.value)}
                placeholder="Введите ключевое слово"
                style={{
                  flex: 1,
                  padding: '8px 12px',
                  border: '1px solid #e2e8f0',
                  borderRadius: '6px',
                  fontSize: '14px'
                }}
                onKeyPress={(e) => e.key === 'Enter' && addKeyword()}
              />
              <button
                onClick={addKeyword}
                style={{
                  background: '#38a169',
                  color: '#fff',
                  border: 'none',
                  borderRadius: '6px',
                  padding: '8px 16px',
                  fontSize: '14px',
                  cursor: 'pointer'
                }}
              >
                Добавить
              </button>
            </div>
            {newKeywords.length > 0 && (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                {newKeywords.map((keyword, index) => (
                  <span
                    key={index}
                    style={{
                      background: '#e2e8f0',
                      color: '#4a5568',
                      padding: '4px 8px',
                      borderRadius: '4px',
                      fontSize: '12px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px'
                    }}
                  >
                    {keyword}
                    <button
                      onClick={() => removeKeyword(index)}
                      style={{
                        background: 'none',
                        border: 'none',
                        color: '#e53e3e',
                        cursor: 'pointer',
                        fontSize: '12px'
                      }}
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>

          <div style={{ display: 'flex', gap: '12px' }}>
            <button
              onClick={addMonitoredChat}
              disabled={saving || !newChatId.trim()}
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
              {saving ? 'Добавление...' : 'Добавить мониторинг'}
            </button>

            <button
              onClick={() => setShowAddForm(false)}
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
          </div>
        </div>
      )}

      {monitoredChats.length === 0 ? (
        <div style={{ 
          textAlign: 'center', 
          padding: '40px', 
          color: '#718096',
          background: '#f7fafc',
          borderRadius: '8px'
        }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>🔍</div>
          <div style={{ fontSize: '18px', marginBottom: '8px' }}>Нет мониторингов чатов</div>
          <div style={{ fontSize: '14px' }}>Добавьте чаты для мониторинга алертов</div>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {monitoredChats.map((chat) => (
            <div
              key={chat.id}
              style={{
                padding: '16px',
                background: chat.is_active ? '#f0fff4' : '#f7fafc',
                borderRadius: '8px',
                border: `1px solid ${chat.is_active ? '#9ae6b4' : '#e2e8f0'}`,
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}
            >
              <div style={{ flex: 1 }}>
                <div style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: '8px', 
                  marginBottom: '8px' 
                }}>
                  <span style={{ 
                    fontWeight: '600', 
                    color: '#2d3748',
                    fontSize: '16px'
                  }}>
                    {chat.chat_title || chat.chat_id}
                  </span>
                  <span style={{
                    background: chat.is_active ? '#38a169' : '#e2e8f0',
                    color: chat.is_active ? '#fff' : '#4a5568',
                    padding: '2px 8px',
                    borderRadius: '12px',
                    fontSize: '12px',
                    fontWeight: '500'
                  }}>
                    {chat.is_active ? 'Активен' : 'Неактивен'}
                  </span>
                </div>
                
                <div style={{ fontSize: '14px', color: '#718096', marginBottom: '4px' }}>
                  <strong>ID:</strong> {chat.chat_id} | <strong>Тип:</strong> {chat.chat_type}
                </div>
                
                {chat.keywords && chat.keywords.length > 0 && (
                  <div style={{ fontSize: '14px', color: '#718096' }}>
                    <strong>Ключевые слова:</strong> {chat.keywords.join(', ')}
                  </div>
                )}
              </div>

              <div style={{ display: 'flex', gap: '8px' }}>
                <button
                  onClick={() => testMonitoredChat(chat.id)}
                  disabled={saving || !chat.is_active}
                  style={{
                    background: saving || !chat.is_active ? '#cbd5e0' : '#3182ce',
                    color: '#fff',
                    border: 'none',
                    borderRadius: '6px',
                    padding: '6px 12px',
                    fontSize: '12px',
                    cursor: saving || !chat.is_active ? 'not-allowed' : 'pointer',
                    transition: 'background 0.2s'
                  }}
                >
                  Тест
                </button>

                <button
                  onClick={() => toggleChatStatus(chat.id, chat.is_active)}
                  disabled={saving}
                  style={{
                    background: saving ? '#cbd5e0' : (chat.is_active ? '#e53e3e' : '#38a169'),
                    color: '#fff',
                    border: 'none',
                    borderRadius: '6px',
                    padding: '6px 12px',
                    fontSize: '12px',
                    cursor: saving ? 'not-allowed' : 'pointer',
                    transition: 'background 0.2s'
                  }}
                >
                  {chat.is_active ? 'Отключить' : 'Включить'}
                </button>

                <button
                  onClick={() => deleteMonitoredChat(chat.id)}
                  disabled={saving}
                  style={{
                    background: saving ? '#cbd5e0' : '#e53e3e',
                    color: '#fff',
                    border: 'none',
                    borderRadius: '6px',
                    padding: '6px 12px',
                    fontSize: '12px',
                    cursor: saving ? 'not-allowed' : 'pointer',
                    transition: 'background 0.2s'
                  }}
                >
                  Удалить
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default TelegramMonitoringComponent;
