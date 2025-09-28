import React, { useState, useEffect } from 'react';
import { agentsAPI, UserMetrics, SystemMetrics, PerformanceMetrics } from '../api/agents';

const MetricsComponent = () => {
  const [myMetrics, setMyMetrics] = useState<UserMetrics | null>(null);
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics | null>(null);
  const [performanceMetrics, setPerformanceMetrics] = useState<PerformanceMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'my' | 'system' | 'performance'>('my');

  useEffect(() => {
    loadMetrics();
  }, []);

  const loadMetrics = async () => {
    try {
      setLoading(true);
      const [my, system, performance] = await Promise.all([
        agentsAPI.getMyMetrics(),
        agentsAPI.getSystemMetrics(),
        agentsAPI.getPerformanceMetrics()
      ]);
      setMyMetrics(my);
      setSystemMetrics(system);
      setPerformanceMetrics(performance);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка при загрузке метрик');
    } finally {
      setLoading(false);
    }
  };

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('ru-RU').format(num);
  };

  const formatTime = (seconds: number) => {
    return `${seconds.toFixed(2)}с`;
  };

  const formatPercentage = (num: number) => {
    return `${num.toFixed(1)}%`;
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '40px' }}>
        <div style={{ fontSize: '18px', color: '#4a5568' }}>Загрузка метрик...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ 
        textAlign: 'center', 
        padding: '40px',
        background: '#fed7d7',
        color: '#c53030',
        borderRadius: '8px',
        border: '1px solid #feb2b2'
      }}>
        <div style={{ fontSize: '18px', marginBottom: '16px' }}>Ошибка загрузки метрик</div>
        <div style={{ fontSize: '14px', marginBottom: '16px' }}>{error}</div>
        <button
          onClick={loadMetrics}
          style={{
            background: '#e53e3e',
            color: '#fff',
            border: 'none',
            borderRadius: '6px',
            padding: '8px 16px',
            fontSize: '14px',
            cursor: 'pointer'
          }}
        >
          Попробовать снова
        </button>
      </div>
    );
  }

  const renderMyMetrics = () => {
    if (!myMetrics) return null;

    return (
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px' }}>
        <div style={{ 
          background: '#fff', 
          padding: '20px', 
          borderRadius: '12px', 
          boxShadow: '0 2px 16px rgba(0,0,0,0.07)',
          border: '1px solid #e2e8f0'
        }}>
          <h4 style={{ margin: '0 0 12px 0', color: '#2d3748' }}>📊 Общая статистика</h4>
          <div style={{ fontSize: '14px', color: '#4a5568', lineHeight: '1.6' }}>
            <div>Подключенных агентов: <strong>{myMetrics.connected_agents}</strong></div>
            <div>Всего запросов: <strong>{formatNumber(myMetrics.total_requests)}</strong></div>
            <div>Среднее время: <strong>{formatTime(myMetrics.avg_processing_time)}</strong></div>
          </div>
        </div>

        <div style={{ 
          background: '#fff', 
          padding: '20px', 
          borderRadius: '12px', 
          boxShadow: '0 2px 16px rgba(0,0,0,0.07)',
          border: '1px solid #e2e8f0'
        }}>
          <h4 style={{ margin: '0 0 12px 0', color: '#2d3748' }}>🤖 По агентам</h4>
          {myMetrics.agent_breakdown.length > 0 ? (
            <div style={{ fontSize: '14px', color: '#4a5568' }}>
              {myMetrics.agent_breakdown.map((agent, index) => (
                <div key={index} style={{ 
                  padding: '8px 0', 
                  borderBottom: index < myMetrics.agent_breakdown.length - 1 ? '1px solid #e2e8f0' : 'none'
                }}>
                  <div>Агент {agent.agent_id}: {agent.requests} запросов</div>
                  <div style={{ fontSize: '12px', color: '#718096' }}>
                    Среднее время: {formatTime(agent.avg_processing_time)}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div style={{ color: '#718096', fontSize: '14px' }}>Нет данных по агентам</div>
          )}
        </div>
      </div>
    );
  };

  const renderSystemMetrics = () => {
    if (!systemMetrics) return null;

    return (
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px' }}>
        <div style={{ 
          background: '#fff', 
          padding: '20px', 
          borderRadius: '12px', 
          boxShadow: '0 2px 16px rgba(0,0,0,0.07)',
          border: '1px solid #e2e8f0'
        }}>
          <h4 style={{ margin: '0 0 12px 0', color: '#2d3748' }}>🌐 Система</h4>
          <div style={{ fontSize: '14px', color: '#4a5568', lineHeight: '1.6' }}>
            <div>Всего агентов: <strong>{systemMetrics.total_agents}</strong></div>
            <div>Активных соединений: <strong>{formatNumber(systemMetrics.active_connections)}</strong></div>
            <div>Всего запросов: <strong>{formatNumber(systemMetrics.total_requests)}</strong></div>
            <div>За последние 7 дней: <strong>{formatNumber(systemMetrics.recent_requests_7d)}</strong></div>
          </div>
        </div>

        <div style={{ 
          background: '#fff', 
          padding: '20px', 
          borderRadius: '12px', 
          boxShadow: '0 2px 16px rgba(0,0,0,0.07)',
          border: '1px solid #e2e8f0'
        }}>
          <h4 style={{ margin: '0 0 12px 0', color: '#2d3748' }}>🏆 Топ агентов</h4>
          {systemMetrics.top_agents.length > 0 ? (
            <div style={{ fontSize: '14px', color: '#4a5568' }}>
              {systemMetrics.top_agents.map((agent, index) => (
                <div key={index} style={{ 
                  padding: '8px 0', 
                  borderBottom: index < systemMetrics.top_agents.length - 1 ? '1px solid #e2e8f0' : 'none'
                }}>
                  <div>#{index + 1} Агент {agent.agent_id}: {agent.requests} запросов</div>
                  <div style={{ fontSize: '12px', color: '#718096' }}>
                    Среднее время: {formatTime(agent.avg_processing_time)}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div style={{ color: '#718096', fontSize: '14px' }}>Нет данных</div>
          )}
        </div>
      </div>
    );
  };

  const renderPerformanceMetrics = () => {
    if (!performanceMetrics) return null;

    return (
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px' }}>
        <div style={{ 
          background: '#fff', 
          padding: '20px', 
          borderRadius: '12px', 
          boxShadow: '0 2px 16px rgba(0,0,0,0.07)',
          border: '1px solid #e2e8f0'
        }}>
          <h4 style={{ margin: '0 0 12px 0', color: '#2d3748' }}>⚡ Производительность</h4>
          <div style={{ fontSize: '14px', color: '#4a5568', lineHeight: '1.6' }}>
            <div>Среднее время: <strong>{formatTime(performanceMetrics.avg_processing_time)}</strong></div>
            <div>Медианное время: <strong>{formatTime(performanceMetrics.median_processing_time)}</strong></div>
            <div>Всего запросов: <strong>{formatNumber(performanceMetrics.total_requests)}</strong></div>
          </div>
        </div>

        <div style={{ 
          background: '#fff', 
          padding: '20px', 
          borderRadius: '12px', 
          boxShadow: '0 2px 16px rgba(0,0,0,0.07)',
          border: '1px solid #e2e8f0'
        }}>
          <h4 style={{ margin: '0 0 12px 0', color: '#2d3748' }}>🚨 Ошибки</h4>
          <div style={{ fontSize: '14px', color: '#4a5568', lineHeight: '1.6' }}>
            <div>Процент ошибок: <strong style={{ 
              color: performanceMetrics.error_rate_percent > 5 ? '#e53e3e' : '#38a169'
            }}>{formatPercentage(performanceMetrics.error_rate_percent)}</strong></div>
            <div>Медленных запросов: <strong>{formatNumber(performanceMetrics.slow_requests)}</strong></div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div style={{ width: '100%', maxWidth: 1200, margin: '0 auto', padding: '0 20px' }}>
      {/* Навигационные табы */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        marginBottom: '32px',
        background: '#fff',
        borderRadius: '12px',
        padding: '8px',
        boxShadow: '0 2px 16px rgba(0,0,0,0.07)',
        maxWidth: '600px',
        margin: '0 auto 32px auto'
      }}>
        <button
          onClick={() => setActiveTab('my')}
          style={{
            background: activeTab === 'my' ? '#3182ce' : 'transparent',
            color: activeTab === 'my' ? '#fff' : '#4a5568',
            border: 'none',
            borderRadius: '8px',
            padding: '12px 24px',
            fontSize: '14px',
            fontWeight: '600',
            cursor: 'pointer',
            transition: 'all 0.2s',
            flex: 1,
            margin: '0 4px'
          }}
        >
          Мои метрики
        </button>
        <button
          onClick={() => setActiveTab('system')}
          style={{
            background: activeTab === 'system' ? '#3182ce' : 'transparent',
            color: activeTab === 'system' ? '#fff' : '#4a5568',
            border: 'none',
            borderRadius: '8px',
            padding: '12px 24px',
            fontSize: '14px',
            fontWeight: '600',
            cursor: 'pointer',
            transition: 'all 0.2s',
            flex: 1,
            margin: '0 4px'
          }}
        >
          Система
        </button>
        <button
          onClick={() => setActiveTab('performance')}
          style={{
            background: activeTab === 'performance' ? '#3182ce' : 'transparent',
            color: activeTab === 'performance' ? '#fff' : '#4a5568',
            border: 'none',
            borderRadius: '8px',
            padding: '12px 24px',
            fontSize: '14px',
            fontWeight: '600',
            cursor: 'pointer',
            transition: 'all 0.2s',
            flex: 1,
            margin: '0 4px'
          }}
        >
          Производительность
        </button>
      </div>

      {/* Содержимое активного таба */}
      <div>
        {activeTab === 'my' && renderMyMetrics()}
        {activeTab === 'system' && renderSystemMetrics()}
        {activeTab === 'performance' && renderPerformanceMetrics()}
      </div>
    </div>
  );
};

export default MetricsComponent;
