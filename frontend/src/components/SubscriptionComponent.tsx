import React, { useState, useEffect } from 'react';
import { planAPI, PlanSchema } from '../api/subscription';

const SubscriptionComponent: React.FC = () => {
  const [plans, setPlans] = useState<PlanSchema[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedPlan, setSelectedPlan] = useState<PlanSchema | null>(null);
  const [showSubscriptionModal, setShowSubscriptionModal] = useState(false);

  // Загрузка активных планов
  const loadPlans = async () => {
    try {
      setLoading(true);
      setError(null);
      const activePlans = await planAPI.getActivePlans();
      setPlans(activePlans);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка загрузки планов');
    } finally {
      setLoading(false);
    }
  };

  // Открытие модального окна подписки
  const openSubscriptionModal = (plan: PlanSchema) => {
    setSelectedPlan(plan);
    setShowSubscriptionModal(true);
  };

  // Закрытие модального окна
  const closeSubscriptionModal = () => {
    setShowSubscriptionModal(false);
    setSelectedPlan(null);
  };

  // Обработка подписки на план
  const handleSubscribe = async () => {
    if (!selectedPlan) return;
    
    try {
      // Здесь будет логика подписки на план
      // Пока что просто закрываем модальное окно
      console.log('Подписка на план:', selectedPlan);
      closeSubscriptionModal();
      
      // Показываем сообщение об успехе (в реальном приложении здесь будет API вызов)
      alert(`Вы успешно подписались на план "${selectedPlan.name}"!`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка подписки на план');
    }
  };

  useEffect(() => {
    loadPlans();
  }, []);

  if (loading && plans.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '20px' }}>
        <div>Загрузка планов подписки...</div>
      </div>
    );
  }

  return (
    <div style={{ 
      width: '100%', 
      maxWidth: 800, 
      background: '#fff', 
      padding: 24, 
      borderRadius: 12, 
      boxShadow: '0 2px 16px rgba(0,0,0,0.07)' 
    }}>
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        marginBottom: 24 
      }}>
        <h2 style={{ color: '#2d3748', margin: 0 }}>Планы подписки</h2>
        <button
          onClick={loadPlans}
          style={{
            background: '#38a169',
            color: '#fff',
            border: 'none',
            borderRadius: 6,
            padding: '8px 16px',
            fontSize: 14,
            cursor: 'pointer',
            transition: 'background 0.2s'
          }}
        >
          Обновить
        </button>
      </div>

      {error && (
        <div style={{ 
          marginBottom: 16, 
          padding: 12, 
          background: '#fed7d7', 
          borderRadius: 6, 
          border: '1px solid #feb2b2',
          color: '#c53030'
        }}>
          {error}
        </div>
      )}

      {plans.length === 0 ? (
        <div style={{ 
          textAlign: 'center', 
          padding: 40, 
          color: '#718096',
          background: '#f7fafc',
          borderRadius: 8,
          border: '2px dashed #e2e8f0'
        }}>
          <div style={{ fontSize: 18, marginBottom: 8 }}>Планы не найдены</div>
          <div style={{ fontSize: 14 }}>В данный момент нет доступных планов подписки</div>
        </div>
      ) : (
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', 
          gap: 20 
        }}>
          {plans.map((plan) => (
            <div key={plan.id} style={{ 
              padding: 24, 
              background: '#f7fafc', 
              borderRadius: 12, 
              border: '2px solid #e2e8f0',
              position: 'relative',
              transition: 'all 0.2s',
              cursor: 'pointer'
            }}>
              {plan.discount_percent && plan.discount_percent > 0 && (
                <div style={{
                  position: 'absolute',
                  top: -10,
                  right: 20,
                  background: '#e53e3e',
                  color: '#fff',
                  padding: '4px 12px',
                  borderRadius: 12,
                  fontSize: 12,
                  fontWeight: 600
                }}>
                  -{plan.discount_percent}%
                </div>
              )}

              <div style={{ textAlign: 'center', marginBottom: 20 }}>
                <h3 style={{ 
                  margin: '0 0 8px 0', 
                  color: '#2d3748', 
                  fontSize: 20 
                }}>
                  {plan.name}
                </h3>
                {plan.description && (
                  <p style={{ 
                    margin: 0, 
                    color: '#718096', 
                    fontSize: 14,
                    lineHeight: 1.5
                  }}>
                    {plan.description}
                  </p>
                )}
              </div>

              <div style={{ 
                textAlign: 'center', 
                marginBottom: 20 
              }}>
                <div style={{ 
                  fontSize: 32, 
                  fontWeight: 700, 
                  color: '#2d3748',
                  marginBottom: 4
                }}>
                  ${plan.price}
                </div>
                <div style={{ 
                  fontSize: 14, 
                  color: '#718096' 
                }}>
                  за {plan.days} {plan.days === 1 ? 'день' : plan.days < 5 ? 'дня' : 'дней'}
                </div>
              </div>

              <div style={{ 
                marginBottom: 20,
                padding: '12px 0',
                borderTop: '1px solid #e2e8f0',
                borderBottom: '1px solid #e2e8f0'
              }}>
                <div style={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  alignItems: 'center',
                  marginBottom: 8
                }}>
                  <span style={{ fontSize: 14, color: '#718096' }}>Длительность:</span>
                  <span style={{ fontSize: 14, fontWeight: 600, color: '#2d3748' }}>
                    {plan.days} {plan.days === 1 ? 'день' : plan.days < 5 ? 'дня' : 'дней'}
                  </span>
                </div>
                <div style={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  alignItems: 'center'
                }}>
                  <span style={{ fontSize: 14, color: '#718096' }}>Статус:</span>
                  <span style={{ 
                    fontSize: 14, 
                    fontWeight: 600, 
                    color: plan.is_active ? '#38a169' : '#e53e3e'
                  }}>
                    {plan.is_active ? 'Активен' : 'Неактивен'}
                  </span>
                </div>
              </div>

              <button
                onClick={() => openSubscriptionModal(plan)}
                disabled={!plan.is_active}
                style={{
                  width: '100%',
                  background: plan.is_active ? '#3182ce' : '#a0aec0',
                  color: '#fff',
                  border: 'none',
                  borderRadius: 8,
                  padding: '12px 24px',
                  fontSize: 16,
                  fontWeight: 600,
                  cursor: plan.is_active ? 'pointer' : 'not-allowed',
                  transition: 'all 0.2s',
                  opacity: plan.is_active ? 1 : 0.6
                }}
              >
                {plan.is_active ? 'Подписаться' : 'Недоступно'}
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Модальное окно подписки */}
      {showSubscriptionModal && selectedPlan && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.5)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          zIndex: 1000
        }}>
          <div style={{
            background: '#fff',
            padding: 32,
            borderRadius: 12,
            maxWidth: 500,
            width: '90%',
            maxHeight: '90vh',
            overflow: 'auto'
          }}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: 24
            }}>
              <h3 style={{ margin: 0, color: '#2d3748' }}>
                Подписка на план "{selectedPlan.name}"
              </h3>
              <button
                onClick={closeSubscriptionModal}
                style={{
                  background: 'none',
                  border: 'none',
                  fontSize: 24,
                  cursor: 'pointer',
                  color: '#718096',
                  padding: 0,
                  width: 32,
                  height: 32,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
              >
                ×
              </button>
            </div>

            <div style={{ marginBottom: 24 }}>
              <div style={{
                padding: 20,
                background: '#f7fafc',
                borderRadius: 8,
                border: '1px solid #e2e8f0'
              }}>
                <div style={{ marginBottom: 16 }}>
                  <h4 style={{ margin: '0 0 8px 0', color: '#2d3748' }}>
                    Детали плана
                  </h4>
                  <div style={{ fontSize: 14, color: '#718096', lineHeight: 1.6 }}>
                    <div><strong>Название:</strong> {selectedPlan.name}</div>
                    <div><strong>Стоимость:</strong> ${selectedPlan.price}</div>
                    <div><strong>Длительность:</strong> {selectedPlan.days} {selectedPlan.days === 1 ? 'день' : selectedPlan.days < 5 ? 'дня' : 'дней'}</div>
                    {selectedPlan.description && (
                      <div><strong>Описание:</strong> {selectedPlan.description}</div>
                    )}
                    {selectedPlan.discount_percent && selectedPlan.discount_percent > 0 && (
                      <div><strong>Скидка:</strong> {selectedPlan.discount_percent}%</div>
                    )}
                  </div>
                </div>
              </div>
            </div>

            <div style={{
              display: 'flex',
              gap: 12,
              justifyContent: 'flex-end'
            }}>
              <button
                onClick={closeSubscriptionModal}
                style={{
                  background: '#e2e8f0',
                  color: '#4a5568',
                  border: 'none',
                  borderRadius: 6,
                  padding: '12px 24px',
                  fontSize: 14,
                  fontWeight: 500,
                  cursor: 'pointer',
                  transition: 'background 0.2s'
                }}
              >
                Отмена
              </button>
              <button
                onClick={handleSubscribe}
                style={{
                  background: '#3182ce',
                  color: '#fff',
                  border: 'none',
                  borderRadius: 6,
                  padding: '12px 24px',
                  fontSize: 14,
                  fontWeight: 600,
                  cursor: 'pointer',
                  transition: 'background 0.2s'
                }}
              >
                Подписаться
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SubscriptionComponent;
