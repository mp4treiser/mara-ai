import React from "react";
import { useAuth } from "../contexts/AuthContext";

const HomePage = () => {
  const { user } = useAuth();

  return (
    <div style={{ 
      width: '100%', 
      maxWidth: 1200, 
      margin: '0 auto', 
      padding: '0 20px' 
    }}>
      {/* Hero Section */}
      <div style={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        borderRadius: '16px',
        padding: '60px 40px',
        textAlign: 'center',
        color: 'white',
        marginBottom: '60px',
        position: 'relative',
        overflow: 'hidden'
      }}>
        <div style={{
          position: 'absolute',
          top: '-50px',
          right: '-50px',
          width: '200px',
          height: '200px',
          background: 'rgba(255,255,255,0.1)',
          borderRadius: '50%',
          zIndex: 1
        }} />
        <div style={{
          position: 'absolute',
          bottom: '-30px',
          left: '-30px',
          width: '150px',
          height: '150px',
          background: 'rgba(255,255,255,0.05)',
          borderRadius: '50%',
          zIndex: 1
        }} />
        
        <div style={{ position: 'relative', zIndex: 2 }}>
          <h1 style={{ 
            fontSize: '48px', 
            fontWeight: '700', 
            margin: '0 0 20px 0',
            textShadow: '0 2px 4px rgba(0,0,0,0.3)'
          }}>
            🤖 MARA-AI
          </h1>
          <p style={{ 
            fontSize: '24px', 
            margin: '0 0 30px 0',
            opacity: 0.9,
            fontWeight: '300'
          }}>
            Интеллектуальная платформа для работы с документами и AI-агентами
          </p>
          <div style={{
            display: 'inline-block',
            background: 'rgba(255,255,255,0.2)',
            padding: '12px 24px',
            borderRadius: '25px',
            fontSize: '16px',
            fontWeight: '500',
            backdropFilter: 'blur(10px)'
          }}>
            {user ? `Добро пожаловать, ${user.email}!` : 'Начните работу прямо сейчас'}
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div style={{ marginBottom: '60px' }}>
        <h2 style={{ 
          textAlign: 'center', 
          fontSize: '36px', 
          fontWeight: '600', 
          color: '#2d3748',
          marginBottom: '50px'
        }}>
          Возможности платформы
        </h2>
        
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: '30px'
        }}>
          {/* Feature 1 */}
          <div style={{
            background: '#fff',
            padding: '30px',
            borderRadius: '12px',
            boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
            border: '1px solid #e2e8f0',
            transition: 'transform 0.2s, box-shadow 0.2s'
          }}>
            <div style={{ fontSize: '48px', marginBottom: '20px' }}>📄</div>
            <h3 style={{ 
              fontSize: '20px', 
              fontWeight: '600', 
              color: '#2d3748',
              margin: '0 0 15px 0'
            }}>
              Умная обработка документов
            </h3>
            <p style={{ 
              color: '#4a5568', 
              lineHeight: '1.6',
              margin: 0
            }}>
              Загружайте PDF, Excel, Word документы и получайте интеллектуальный анализ с помощью AI-агентов. Каждый пользователь имеет свой изолированный набор документов.
            </p>
          </div>

          {/* Feature 2 */}
          <div style={{
            background: '#fff',
            padding: '30px',
            borderRadius: '12px',
            boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
            border: '1px solid #e2e8f0',
            transition: 'transform 0.2s, box-shadow 0.2s'
          }}>
            <div style={{ fontSize: '48px', marginBottom: '20px' }}>🤖</div>
            <h3 style={{ 
              fontSize: '20px', 
              fontWeight: '600', 
              color: '#2d3748',
              margin: '0 0 15px 0'
            }}>
              Персональные AI-агенты
            </h3>
            <p style={{ 
              color: '#4a5568', 
              lineHeight: '1.6',
              margin: 0
            }}>
              Создавайте и настраивайте собственных AI-агентов для решения специфических задач. Каждый агент может быть настроен под ваши потребности.
            </p>
          </div>

          {/* Feature 3 */}
          <div style={{
            background: '#fff',
            padding: '30px',
            borderRadius: '12px',
            boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
            border: '1px solid #e2e8f0',
            transition: 'transform 0.2s, box-shadow 0.2s'
          }}>
            <div style={{ fontSize: '48px', marginBottom: '20px' }}>💬</div>
            <h3 style={{ 
              fontSize: '20px', 
              fontWeight: '600', 
              color: '#2d3748',
              margin: '0 0 15px 0'
            }}>
              Telegram интеграция
            </h3>
            <p style={{ 
              color: '#4a5568', 
              lineHeight: '1.6',
              margin: 0
            }}>
              Получайте ответы от AI-агентов прямо в Telegram. Настройте бота и получайте уведомления о результатах анализа документов.
            </p>
          </div>

          {/* Feature 4 */}
          <div style={{
            background: '#fff',
            padding: '30px',
            borderRadius: '12px',
            boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
            border: '1px solid #e2e8f0',
            transition: 'transform 0.2s, box-shadow 0.2s'
          }}>
            <div style={{ fontSize: '48px', marginBottom: '20px' }}>📊</div>
            <h3 style={{ 
              fontSize: '20px', 
              fontWeight: '600', 
              color: '#2d3748',
              margin: '0 0 15px 0'
            }}>
              Детальная аналитика
            </h3>
            <p style={{ 
              color: '#4a5568', 
              lineHeight: '1.6',
              margin: 0
            }}>
              Отслеживайте производительность агентов, время обработки запросов и получайте подробную статистику использования платформы.
            </p>
          </div>

          {/* Feature 5 */}
          <div style={{
            background: '#fff',
            padding: '30px',
            borderRadius: '12px',
            boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
            border: '1px solid #e2e8f0',
            transition: 'transform 0.2s, box-shadow 0.2s'
          }}>
            <div style={{ fontSize: '48px', marginBottom: '20px' }}>🔒</div>
            <h3 style={{ 
              fontSize: '20px', 
              fontWeight: '600', 
              color: '#2d3748',
              margin: '0 0 15px 0'
            }}>
              Безопасность данных
            </h3>
            <p style={{ 
              color: '#4a5568', 
              lineHeight: '1.6',
              margin: 0
            }}>
              Все ваши документы и данные надежно защищены. Каждый пользователь имеет изолированное рабочее пространство с собственной базой документов.
            </p>
          </div>

          {/* Feature 6 */}
          <div style={{
            background: '#fff',
            padding: '30px',
            borderRadius: '12px',
            boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
            border: '1px solid #e2e8f0',
            transition: 'transform 0.2s, box-shadow 0.2s'
          }}>
            <div style={{ fontSize: '48px', marginBottom: '20px' }}>💰</div>
            <h3 style={{ 
              fontSize: '20px', 
              fontWeight: '600', 
              color: '#2d3748',
              margin: '0 0 15px 0'
            }}>
              Гибкая система подписок
            </h3>
            <p style={{ 
              color: '#4a5568', 
              lineHeight: '1.6',
              margin: 0
            }}>
              Выберите подходящий тарифный план. Оплачивайте только за то, что используете. Система автоматически списывает средства с вашего баланса.
            </p>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div style={{
        background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
        borderRadius: '16px',
        padding: '50px 40px',
        textAlign: 'center',
        color: 'white',
        marginBottom: '40px'
      }}>
        <h2 style={{ 
          fontSize: '32px', 
          fontWeight: '600', 
          margin: '0 0 20px 0'
        }}>
          Готовы начать работу?
        </h2>
        <p style={{ 
          fontSize: '18px', 
          margin: '0 0 30px 0',
          opacity: 0.9
        }}>
          Присоединяйтесь к тысячам пользователей, которые уже используют MARA-AI для автоматизации работы с документами
        </p>
        {!user && (
          <div style={{ display: 'flex', gap: '20px', justifyContent: 'center', flexWrap: 'wrap' }}>
            <button style={{
              background: 'rgba(255,255,255,0.2)',
              color: 'white',
              border: '2px solid rgba(255,255,255,0.3)',
              padding: '12px 30px',
              borderRadius: '25px',
              fontSize: '16px',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'all 0.2s',
              backdropFilter: 'blur(10px)'
            }}>
              Зарегистрироваться
            </button>
            <button style={{
              background: 'white',
              color: '#f5576c',
              border: 'none',
              padding: '12px 30px',
              borderRadius: '25px',
              fontSize: '16px',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}>
              Войти
            </button>
          </div>
        )}
      </div>

      {/* Stats Section */}
      <div style={{
        background: '#f7fafc',
        borderRadius: '12px',
        padding: '40px',
        textAlign: 'center'
      }}>
        <h3 style={{ 
          fontSize: '24px', 
          fontWeight: '600', 
          color: '#2d3748',
          margin: '0 0 30px 0'
        }}>
          Платформа в цифрах
        </h3>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '30px'
        }}>
          <div>
            <div style={{ fontSize: '36px', fontWeight: '700', color: '#3182ce', marginBottom: '8px' }}>1000+</div>
            <div style={{ color: '#4a5568', fontSize: '14px' }}>Обработанных документов</div>
          </div>
          <div>
            <div style={{ fontSize: '36px', fontWeight: '700', color: '#38a169', marginBottom: '8px' }}>50+</div>
            <div style={{ color: '#4a5568', fontSize: '14px' }}>Активных пользователей</div>
          </div>
          <div>
            <div style={{ fontSize: '36px', fontWeight: '700', color: '#d69e2e', marginBottom: '8px' }}>99.9%</div>
            <div style={{ color: '#4a5568', fontSize: '14px' }}>Время работы</div>
          </div>
          <div>
            <div style={{ fontSize: '36px', fontWeight: '700', color: '#e53e3e', marginBottom: '8px' }}>24/7</div>
            <div style={{ color: '#4a5568', fontSize: '14px' }}>Техническая поддержка</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage; 