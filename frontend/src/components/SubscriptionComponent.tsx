import React, { useState, useEffect } from 'react';
import { subscriptionAPI, SubscriptionResponse } from '../api/subscription';
import { planAPI, PlanSchema } from '../api/subscription';
import { userAPI } from '../api/user';
import { useAuth } from '../contexts/AuthContext';

const SubscriptionComponent: React.FC = () => {
  const { user } = useAuth();
  const [plans, setPlans] = useState<PlanSchema[]>([]);
  const [userSubscriptions, setUserSubscriptions] = useState<SubscriptionResponse[]>([]);
  const [userBalance, setUserBalance] = useState<number>(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedPlan, setSelectedPlan] = useState<PlanSchema | null>(null);
  const [showSubscriptionModal, setShowSubscriptionModal] = useState(false);

  // Загрузка баланса пользователя
  const loadUserBalance = async () => {
    try {
      const balanceData = await userAPI.getUserBalance();
      setUserBalance(balanceData.balance);
    } catch (err) {
      console.error('Ошибка загрузки баланса:', err);
      setUserBalance(0);
    }
  };

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

  // Загрузка подписок пользователя
  const loadUserSubscriptions = async () => {
    try {
      const subscriptions = await subscriptionAPI.getUserSubscriptions();
      // Фильтруем только активные подписки
      const activeSubscriptions = subscriptions.filter(sub => sub.is_active);
      setUserSubscriptions(activeSubscriptions);
    } catch (err) {
      console.error('Ошибка загрузки подписок:', err);
      setUserSubscriptions([]);
    }
  };

  // Получение информации о плане по ID
  const getPlanById = (planId: number): PlanSchema | null => {
    return plans.find(plan => plan.id === planId) || null;
  };

  // Расчет финальной цены с учетом скидки
  const calculateFinalPrice = (plan: PlanSchema): number => {
    let finalPrice = plan.price;
    if (plan.discount_percent) {
      finalPrice = plan.price * (1 - plan.discount_percent / 100);
    }
    return Math.round(finalPrice * 100) / 100; // Округляем до 2 знаков
  };

  // Открытие модального окна подписки
  const openSubscriptionModal = (plan: PlanSchema) => {
    const finalPrice = calculateFinalPrice(plan);
    
    // Проверяем баланс перед открытием модалки
    if (userBalance < finalPrice) {
      setError(`Недостаточно средств на балансе. Требуется: $${finalPrice}, доступно: $${userBalance}`);
      return;
    }
    
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
    
    const finalPrice = calculateFinalPrice(selectedPlan);
    
    // Дополнительная проверка баланса перед отправкой запроса
    if (userBalance < finalPrice) {
      setError(`Недостаточно средств на балансе. Требуется: $${finalPrice}, доступно: $${userBalance}`);
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      
      console.log('Создаем подписку на план:', selectedPlan.name, 'Цена:', finalPrice, 'Баланс:', userBalance);
      
      // Создаем подписку через API
      const subscription = await subscriptionAPI.createSubscription(selectedPlan.id);
      
      console.log('Подписка успешно создана:', subscription);
      
      // Обновляем баланс пользователя и подписки
      await Promise.all([
        loadUserBalance(),
        loadUserSubscriptions()
      ]);
      
      // Закрываем модальное окно
      closeSubscriptionModal();
      
      // Показываем сообщение об успехе
      alert(`Вы успешно подписались на план "${selectedPlan.name}" за $${finalPrice}!`);
      
    } catch (err) {
      console.error('Ошибка создания подписки:', err);
      
      // Обрабатываем различные типы ошибок
      let errorMessage = 'Ошибка подписки на план';
      
      if (err instanceof Error) {
        if (err.message.includes('Insufficient balance')) {
          errorMessage = 'Недостаточно средств на балансе';
        } else if (err.message.includes('Plan not found')) {
          errorMessage = 'План подписки не найден';
        } else {
          errorMessage = err.message;
        }
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const loadData = async () => {
      await Promise.all([
        loadPlans(),
        loadUserBalance(),
        loadUserSubscriptions()
      ]);
    };
    loadData();
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
        <div>
          <h2 style={{ color: '#2d3748', margin: '0 0 8px 0' }}>Планы подписки</h2>
          <div style={{ 
            color: '#4a5568', 
            fontSize: 14,
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            marginBottom: 8
          }}>
            <span>💰 Ваш баланс:</span>
            <span style={{ 
              fontWeight: 600,
              color: userBalance > 0 ? '#38a169' : '#e53e3e'
            }}>
              ${userBalance.toFixed(2)}
            </span>
          </div>
        </div>
        <button
          onClick={() => {
            loadPlans();
            loadUserBalance();
            loadUserSubscriptions();
          }}
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

      {/* Текущие подписки пользователя */}
      {userSubscriptions.length > 0 && (
        <div style={{ marginBottom: 24 }}>
          <h3 style={{ color: '#2d3748', margin: '0 0 16px 0', fontSize: 18 }}>
            Ваши подписки
          </h3>
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', 
            gap: 16 
          }}>
            {userSubscriptions.map((subscription) => {
              const endDate = new Date(subscription.end_date);
              const daysLeft = Math.ceil((endDate.getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24));
              const plan = getPlanById(subscription.plan_id);
              
              return (
                <div key={subscription.id} style={{ 
                  padding: 20, 
                  background: '#f0fff4', 
                  borderRadius: 8, 
                  border: '2px solid #9ae6b4',
                  position: 'relative'
                }}>
                  <div style={{ 
                    display: 'flex', 
                    justifyContent: 'space-between', 
                    alignItems: 'flex-start',
                    marginBottom: 12
                  }}>
                    <div>
                      <h4 style={{ 
                        margin: '0 0 4px 0', 
                        color: '#2d3748', 
                        fontSize: 16 
                      }}>
                        {plan?.name || `План #${subscription.plan_id}`}
                      </h4>
                      <div style={{ 
                        fontSize: 14, 
                        color: '#718096' 
                      }}>
                        Статус: <span style={{ 
                          color: '#38a169',
                          fontWeight: 600
                        }}>
                          Активна
                        </span>
                      </div>
                    </div>
                    <div style={{
                      background: '#3182ce',
                      color: '#fff',
                      padding: '4px 8px',
                      borderRadius: 4,
                      fontSize: 12,
                      fontWeight: 600
                    }}>
                      {daysLeft > 0 ? `${daysLeft} дн.` : 'Сегодня'}
                    </div>
                  </div>
                  
                  <div style={{ 
                    fontSize: 14, 
                    color: '#4a5568',
                    lineHeight: 1.5
                  }}>
                    <div><strong>Начало:</strong> {new Date(subscription.start_date).toLocaleDateString('ru-RU')}</div>
                    <div><strong>Окончание:</strong> {endDate.toLocaleDateString('ru-RU')}</div>
                    <div><strong>Стоимость:</strong> ${plan?.price || subscription.total_paid || 'N/A'}</div>
                  </div>
                </div>
              );
            })}
          </div>
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
                  marginBottom: 4,
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                  gap: 8
                }}>
                  ${calculateFinalPrice(plan)}
                  {plan.discount_percent && plan.discount_percent > 0 && (
                    <span style={{
                      fontSize: 18,
                      color: '#e53e3e',
                      textDecoration: 'line-through',
                      fontWeight: 400
                    }}>
                      ${plan.price}
                    </span>
                  )}
                </div>
                <div style={{ 
                  fontSize: 14, 
                  color: '#718096' 
                }}>
                  за {plan.days} {plan.days === 1 ? 'день' : plan.days < 5 ? 'дня' : 'дней'}
                </div>
                {plan.discount_percent && plan.discount_percent > 0 && (
                  <div style={{
                    fontSize: 12,
                    color: '#38a169',
                    fontWeight: 600,
                    marginTop: 4
                  }}>
                    Экономия: ${(plan.price - calculateFinalPrice(plan)).toFixed(2)}
                  </div>
                )}
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

              {(() => {
                const finalPrice = calculateFinalPrice(plan);
                const hasEnoughBalance = userBalance >= finalPrice;
                const isDisabled = !plan.is_active || !hasEnoughBalance;
                
                return (
                  <button
                    onClick={() => openSubscriptionModal(plan)}
                    disabled={isDisabled}
                    style={{
                      width: '100%',
                      background: isDisabled ? '#a0aec0' : '#3182ce',
                      color: '#fff',
                      border: 'none',
                      borderRadius: 8,
                      padding: '12px 24px',
                      fontSize: 16,
                      fontWeight: 600,
                      cursor: isDisabled ? 'not-allowed' : 'pointer',
                      transition: 'all 0.2s',
                      opacity: isDisabled ? 0.6 : 1
                    }}
                  >
                    {!plan.is_active ? 'Недоступно' : 
                     !hasEnoughBalance ? `Недостаточно средств ($${finalPrice})` : 
                     'Подписаться'}
                  </button>
                );
              })()}
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
                disabled={loading}
                style={{
                  background: loading ? '#a0aec0' : '#3182ce',
                  color: '#fff',
                  border: 'none',
                  borderRadius: 6,
                  padding: '12px 24px',
                  fontSize: 14,
                  fontWeight: 600,
                  cursor: loading ? 'not-allowed' : 'pointer',
                  transition: 'background 0.2s',
                  opacity: loading ? 0.7 : 1
                }}
              >
                {loading ? 'Подписка...' : 'Подписаться'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SubscriptionComponent;
