import React, { useState, useEffect } from 'react';
import { agentsAPI, Agent, UserAgent, Document } from '../api/agents';
import TelegramConfigComponent from './TelegramConfigComponent';
import TelegramMonitoringComponent from './TelegramMonitoringComponent';
import AiogramBotManagementComponent from './AiogramBotManagementComponent';

const AgentsComponent = () => {
  const [availableAgents, setAvailableAgents] = useState<Agent[]>([]);
  const [myAgents, setMyAgents] = useState<UserAgent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedAgent, setSelectedAgent] = useState<UserAgent | null>(null);
  const [analysisText, setAnalysisText] = useState('');
  const [analysisResult, setAnalysisResult] = useState<string | null>(null);
  const [uploadingFile, setUploadingFile] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [uploadedDocuments, setUploadedDocuments] = useState<string[]>([]);
  const [showMetrics, setShowMetrics] = useState(false);
  const [agentDocuments, setAgentDocuments] = useState<Document[]>([]);
  const [loadingDocuments, setLoadingDocuments] = useState(false);

  useEffect(() => {
    loadAgents();
  }, []);

  const loadAgents = async () => {
    try {
      setLoading(true);
      setError(null);
      const [available, my] = await Promise.all([
        agentsAPI.getAvailableAgents(),
        agentsAPI.getMyAgents()
      ]);
      setAvailableAgents(available);
      setMyAgents(my);
    } catch (err) {
      console.error('Ошибка загрузки агентов:', err);
      
      // Обрабатываем различные типы ошибок
      let errorMessage = 'Ошибка при загрузке агентов';
      
      if (err instanceof Error) {
        const message = err.message;
        console.log('Error message:', message);
        
        // Проверяем, содержит ли сообщение информацию о подписке
        if (message.includes('подписк') || message.includes('subscription') || message.includes('403') || message.includes('Forbidden')) {
          errorMessage = '❌ У вас нет активной подписки. Пожалуйста, оформите подписку для доступа к агентам.';
        } else if (message.includes('401') || message.includes('Unauthorized') || message.includes('авторизац')) {
          errorMessage = '❌ Необходима авторизация. Пожалуйста, войдите в систему.';
        } else {
          errorMessage = message;
        }
      } else {
        // Если err не является Error объектом
        errorMessage = String(err);
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleConnectToAgent = async (agentId: number) => {
    try {
      const userAgent = await agentsAPI.connectToAgent(agentId);
      setMyAgents(prev => [...prev, userAgent]);
      setAvailableAgents(prev => 
        prev.map(agent => 
          agent.id === agentId 
            ? { ...agent, is_user_agent: true, user_agent_id: userAgent.id }
            : agent
        )
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка при подключении к агенту');
    }
  };

  const handleDisconnectFromAgent = async (userAgentId: number) => {
    try {
      await agentsAPI.disconnectFromAgent(userAgentId);
      const disconnectedAgent = myAgents.find(ua => ua.id === userAgentId);
      if (disconnectedAgent) {
        setMyAgents(prev => prev.filter(ua => ua.id !== userAgentId));
        setAvailableAgents(prev => 
          prev.map(agent => 
            agent.id === disconnectedAgent.agent_id 
              ? { ...agent, is_user_agent: false, user_agent_id: undefined }
              : agent
          )
        );
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка при отключении от агента');
    }
  };

  // Загрузка документов агента
  const loadAgentDocuments = async (userAgentId: number) => {
    try {
      setLoadingDocuments(true);
      const documents = await agentsAPI.getAgentDocuments(userAgentId);
      setAgentDocuments(documents);
    } catch (err) {
      console.error('Ошибка загрузки документов:', err);
      setAgentDocuments([]);
    } finally {
      setLoadingDocuments(false);
    }
  };

  // Удаление отдельного документа
  const handleDeleteDocument = async (documentId: number) => {
    if (!window.confirm('Вы уверены, что хотите удалить этот документ?')) {
      return;
    }

    try {
      await agentsAPI.deleteDocument(documentId);
      setAgentDocuments(prev => prev.filter(doc => doc.id !== documentId));
      setUploadedDocuments(prev => prev.filter(doc => doc !== documentId.toString()));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка при удалении документа');
    }
  };

  // Очистка всех документов агента
  const handleClearAllDocuments = async (userAgentId: number) => {
    if (!window.confirm('Вы уверены, что хотите удалить все документы этого агента?')) {
      return;
    }

    try {
      await agentsAPI.clearAgentDocuments(userAgentId);
      setAgentDocuments([]);
      setUploadedDocuments([]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка при очистке документов');
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleFileUpload = async () => {
    if (!selectedFile || !selectedAgent) return;

    try {
      setUploadingFile(true);
      await agentsAPI.uploadDocument(selectedAgent.id, selectedFile);
      setSelectedFile(null);
      setError(null);
      
      // Перезагружаем список документов
      await loadAgentDocuments(selectedAgent.id);
      
      // Можно добавить уведомление об успешной загрузке
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка при загрузке файла');
    } finally {
      setUploadingFile(false);
    }
  };

  const handleAnalyzeText = async () => {
    if (!analysisText.trim() || !selectedAgent) return;

    try {
      setAnalyzing(true);
      setError(null);
      const result = await agentsAPI.analyzeText(selectedAgent.id, analysisText);
      if (result.success) {
        setAnalysisResult(result.response);
      } else {
        setError(result.error_message || 'Ошибка при анализе текста');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка при анализе текста');
    } finally {
      setAnalyzing(false);
    }
  };

  const handleClearDocuments = async () => {
    if (!selectedAgent) return;
    
    if (!confirm('Вы уверены, что хотите удалить все документы этого агента?')) {
      return;
    }
    
    try {
      setError(null);
      const result = await agentsAPI.clearAgentDocuments(selectedAgent.id);
      if (result.success) {
        alert('Все документы агента удалены');
        setUploadedDocuments([]);
      } else {
        setError(result.message || 'Ошибка при удалении документов');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка при удалении документов');
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '20px' }}>
        Загрузка агентов...
      </div>
    );
  }

  return (
    <div style={{ 
      width: '100%', 
      maxWidth: 1200, 
      margin: '0 auto', 
      padding: '0 20px' 
    }}>
      <style>
        {`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}
      </style>
      {error && (
        <div style={{ 
          marginBottom: '20px', 
          padding: '16px', 
          background: error.includes('подписки') ? '#fef5e7' : '#fed7d7', 
          color: error.includes('подписки') ? '#d69e2e' : '#c53030', 
          borderRadius: '8px',
          border: `1px solid ${error.includes('подписки') ? '#f6e05e' : '#feb2b2'}`,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: '16px', fontWeight: '600', marginBottom: '8px' }}>
              {error}
            </div>
            {error.includes('подписки') && (
              <div style={{ fontSize: '14px', opacity: 0.8 }}>
                Перейдите во вкладку "Подписки" для оформления подписки
              </div>
            )}
          </div>
          <button 
            onClick={() => setError(null)}
            style={{ 
              marginLeft: '10px', 
              background: 'none', 
              border: 'none', 
              color: error.includes('подписки') ? '#d69e2e' : '#c53030', 
              cursor: 'pointer',
              fontSize: '20px',
              padding: '4px',
              borderRadius: '4px',
              transition: 'background 0.2s'
            }}
            onMouseOver={(e) => e.currentTarget.style.background = 'rgba(0,0,0,0.1)'}
            onMouseOut={(e) => e.currentTarget.style.background = 'none'}
          >
            ×
          </button>
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '32px' }}>
        {/* Доступные агенты */}
        <div style={{ 
          background: '#fff', 
          padding: '24px', 
          borderRadius: '12px', 
          boxShadow: '0 2px 16px rgba(0,0,0,0.07)' 
        }}>
          <h3 style={{ margin: '0 0 20px 0', color: '#2d3748' }}>
            Доступные агенты ({availableAgents.length})
          </h3>
          
          {availableAgents.length === 0 ? (
            <p style={{ color: '#718096', textAlign: 'center' }}>
              Нет доступных агентов
            </p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {availableAgents.map(agent => (
                <div key={agent.id} style={{ 
                  padding: '16px', 
                  border: '1px solid #e2e8f0', 
                  borderRadius: '8px',
                  background: agent.is_user_agent ? '#f0fff4' : '#fff'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                    <h4 style={{ margin: 0, color: '#2d3748' }}>{agent.name}</h4>
                    {agent.is_user_agent ? (
                      <span style={{ 
                        background: '#38a169', 
                        color: '#fff', 
                        padding: '4px 8px', 
                        borderRadius: '4px', 
                        fontSize: '12px' 
                      }}>
                        Подключен
                      </span>
                    ) : (
                      <button
                        onClick={() => handleConnectToAgent(agent.id)}
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
                        Подключиться
                      </button>
                    )}
                  </div>
                  <p style={{ 
                    margin: '0 0 12px 0', 
                    color: '#4a5568', 
                    fontSize: '14px',
                    lineHeight: '1.5'
                  }}>
                    {agent.prompt}
                  </p>
                  <div style={{ fontSize: '12px', color: '#718096' }}>
                    Создан: {new Date(agent.created_at).toLocaleDateString()}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Мои агенты */}
        <div style={{ 
          background: '#fff', 
          padding: '24px', 
          borderRadius: '12px', 
          boxShadow: '0 2px 16px rgba(0,0,0,0.07)' 
        }}>
          <h3 style={{ margin: '0 0 20px 0', color: '#2d3748' }}>
            Мои агенты ({myAgents.length})
          </h3>
          
          {myAgents.length === 0 ? (
            <p style={{ color: '#718096', textAlign: 'center' }}>
              У вас пока нет подключенных агентов
            </p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {myAgents.map(userAgent => (
                <div key={userAgent.id} style={{ 
                  padding: '16px', 
                  border: '1px solid #e2e8f0', 
                  borderRadius: '8px',
                  background: selectedAgent?.id === userAgent.id ? '#ebf8ff' : '#fff'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                    <h4 style={{ margin: 0, color: '#2d3748' }}>{userAgent.agent_name}</h4>
                    <button
                      onClick={() => handleDisconnectFromAgent(userAgent.id)}
                      style={{
                        background: '#e53e3e',
                        color: '#fff',
                        border: 'none',
                        borderRadius: '6px',
                        padding: '6px 12px',
                        fontSize: '12px',
                        cursor: 'pointer',
                        transition: 'background 0.2s'
                      }}
                    >
                      Отключиться
                    </button>
                  </div>
                  <p style={{ 
                    margin: '0 0 12px 0', 
                    color: '#4a5568', 
                    fontSize: '14px',
                    lineHeight: '1.5'
                  }}>
                    {userAgent.agent_prompt}
                  </p>
                  <button
                    onClick={() => setSelectedAgent(userAgent)}
                    style={{
                      background: selectedAgent?.id === userAgent.id ? '#3182ce' : '#edf2f7',
                      color: selectedAgent?.id === userAgent.id ? '#fff' : '#4a5568',
                      border: 'none',
                      borderRadius: '6px',
                      padding: '8px 16px',
                      fontSize: '14px',
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      width: '100%'
                    }}
                  >
                    {selectedAgent?.id === userAgent.id ? 'Выбран' : 'Выбрать'}
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Работа с выбранным агентом */}
      {selectedAgent && (
        <div style={{ 
          marginTop: '32px',
          background: '#fff', 
          padding: '24px', 
          borderRadius: '12px', 
          boxShadow: '0 2px 16px rgba(0,0,0,0.07)' 
        }}>
          <h3 style={{ margin: '0 0 20px 0', color: '#2d3748' }}>
            Работа с агентом: {selectedAgent.agent_name}
          </h3>
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
            {/* Загрузка документов */}
            <div>
              <h4 style={{ margin: '0 0 16px 0', color: '#4a5568' }}>Загрузка документов</h4>
              <div style={{ marginBottom: '16px' }}>
                <input
                  type="file"
                  onChange={handleFileSelect}
                  accept=".txt,.pdf,.docx,.doc,.xlsx,.xls"
                  style={{ marginBottom: '12px' }}
                />
                {selectedFile && (
                  <div style={{ 
                    padding: '8px', 
                    background: '#f7fafc', 
                    borderRadius: '4px',
                    fontSize: '14px',
                    color: '#4a5568'
                  }}>
                    Выбран файл: {selectedFile.name}
                  </div>
                )}
              </div>
              <button
                onClick={handleFileUpload}
                disabled={!selectedFile || uploadingFile}
                style={{
                  background: selectedFile && !uploadingFile ? '#3182ce' : '#cbd5e0',
                  color: '#fff',
                  border: 'none',
                  borderRadius: '6px',
                  padding: '10px 20px',
                  fontSize: '14px',
                  cursor: selectedFile && !uploadingFile ? 'pointer' : 'not-allowed',
                  transition: 'background 0.2s'
                }}
              >
                {uploadingFile ? 'Загрузка...' : 'Загрузить документ'}
              </button>
              
              {/* Кнопка очистки документов */}
              <button
                onClick={() => handleClearAllDocuments(selectedAgent.id)}
                style={{
                  marginLeft: '12px',
                  backgroundColor: '#e53e3e',
                  color: '#fff',
                  border: 'none',
                  borderRadius: '6px',
                  padding: '10px 20px',
                  fontSize: '14px',
                  cursor: 'pointer',
                  transition: 'background 0.2s'
                }}
              >
                Очистить документы
              </button>

              {/* Кнопка загрузки списка документов */}
              <button
                onClick={() => loadAgentDocuments(selectedAgent.id)}
                disabled={loadingDocuments}
                style={{
                  marginLeft: '12px',
                  backgroundColor: '#38a169',
                  color: '#fff',
                  border: 'none',
                  borderRadius: '6px',
                  padding: '10px 20px',
                  fontSize: '14px',
                  cursor: 'pointer',
                  transition: 'background 0.2s',
                  opacity: loadingDocuments ? 0.6 : 1
                }}
              >
                {loadingDocuments ? 'Загрузка...' : 'Обновить список'}
              </button>

              {/* Список документов */}
              {agentDocuments.length > 0 && (
                <div style={{ marginTop: '20px' }}>
                  <h5 style={{ margin: '0 0 12px 0', color: '#4a5568', fontSize: '16px' }}>
                    Загруженные документы ({agentDocuments.length})
                  </h5>
                  <div style={{ 
                    maxHeight: '200px', 
                    overflowY: 'auto',
                    border: '1px solid #e2e8f0',
                    borderRadius: '6px',
                    padding: '8px'
                  }}>
                    {agentDocuments.map((doc) => (
                      <div key={doc.id} style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        padding: '8px 12px',
                        marginBottom: '4px',
                        background: '#f7fafc',
                        borderRadius: '4px',
                        fontSize: '14px'
                      }}>
                        <div style={{ flex: 1 }}>
                          <div style={{ fontWeight: '500', color: '#2d3748' }}>
                            {doc.filename}
                          </div>
                          <div style={{ fontSize: '12px', color: '#718096' }}>
                            {doc.file_type} • {(doc.file_size / 1024).toFixed(1)} KB • 
                            {doc.processed ? ' ✅ Обработан' : ' ⏳ В обработке'}
                          </div>
                        </div>
                        <button
                          onClick={() => handleDeleteDocument(doc.id)}
                          style={{
                            background: '#e53e3e',
                            color: '#fff',
                            border: 'none',
                            borderRadius: '4px',
                            padding: '4px 8px',
                            fontSize: '12px',
                            cursor: 'pointer',
                            transition: 'background 0.2s'
                          }}
                        >
                          Удалить
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Анализ текста */}
            <div>
              <h4 style={{ margin: '0 0 16px 0', color: '#4a5568' }}>Анализ текста</h4>
              <textarea
                value={analysisText}
                onChange={(e) => setAnalysisText(e.target.value)}
                placeholder="Введите текст для анализа..."
                style={{
                  width: '100%',
                  minHeight: '100px',
                  padding: '12px',
                  border: '1px solid #e2e8f0',
                  borderRadius: '6px',
                  fontSize: '14px',
                  resize: 'vertical',
                  marginBottom: '12px'
                }}
              />
              <button
                onClick={handleAnalyzeText}
                disabled={!analysisText.trim() || analyzing}
                style={{
                  background: analysisText.trim() && !analyzing ? '#38a169' : '#cbd5e0',
                  color: '#fff',
                  border: 'none',
                  borderRadius: '6px',
                  padding: '10px 20px',
                  fontSize: '14px',
                  cursor: analysisText.trim() && !analyzing ? 'pointer' : 'not-allowed',
                  transition: 'background 0.2s',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}
              >
                {analyzing && (
                  <div style={{
                    width: '16px',
                    height: '16px',
                    border: '2px solid #fff',
                    borderTop: '2px solid transparent',
                    borderRadius: '50%',
                    animation: 'spin 1s linear infinite'
                  }} />
                )}
                {analyzing ? 'Анализирую...' : 'Анализировать'}
              </button>
            </div>
          </div>

          {/* Результат анализа */}
          {analysisResult && (
            <div style={{ 
              marginTop: '24px',
              padding: '16px',
              background: '#f0fff4',
              borderRadius: '8px',
              border: '1px solid #9ae6b4'
            }}>
              <h4 style={{ margin: '0 0 12px 0', color: '#22543d' }}>Результат анализа:</h4>
              <p style={{ margin: 0, color: '#22543d', lineHeight: '1.6' }}>
                {analysisResult}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Настройки Telegram для выбранного агента */}
      {selectedAgent && (
        <TelegramConfigComponent 
          userAgentId={selectedAgent.id}
          agentId={selectedAgent.agent_id}
        />
      )}

        {/* Мониторинг чатов для выбранного агента */}
        {selectedAgent && (
          <TelegramMonitoringComponent 
            userAgentId={selectedAgent.id}
            agentId={selectedAgent.agent_id}
          />
        )}


        {/* Управление aiogram ботом для выбранного агента */}
        {selectedAgent && (
          <AiogramBotManagementComponent 
            userAgentId={selectedAgent.id}
            agentId={selectedAgent.agent_id}
          />
        )}
    </div>
  );
};

export default AgentsComponent;
