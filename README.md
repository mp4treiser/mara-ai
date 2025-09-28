# 🤖 MARA-AI

**Monitoring & Assistance Reactive Agent Platform**

Интеллектуальная платформа для работы с документами и AI-агентами с поддержкой блокчейн кошельков и подписок.

---

## 📋 Обзор / Overview

**Русский:**  
MARA-AI — это комплексная платформа для мониторинга и автоматизации бизнес-процессов с помощью AI-агентов. Система использует принципы RAG (Retrieval-Augmented Generation) для обработки алертов на основе внутренней документации компании и автоматизации типовых реакций. Включает современный web-интерфейс (React + TypeScript), мощный backend (FastAPI + PostgreSQL), поддержку блокчейн кошельков (Arbitrum в сети ETH), систему подписок и Telegram-ботов для мониторинга.

**English:**  
MARA-AI is a comprehensive platform for business monitoring and automation using AI agents. It leverages RAG (Retrieval-Augmented Generation) principles to help companies react to alerts based on internal documentation and automate routine responses. The system includes a modern web UI (React + TypeScript), powerful backend (FastAPI + PostgreSQL), blockchain wallet support (Arbitrum in ETH), subscription management, and Telegram bots for monitoring.

---

## 🏗️ Архитектура / Architecture

### Основные компоненты / Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                    MARA-AI Platform                        │
├─────────────────────────────────────────────────────────────┤
│  Frontend (React + TypeScript)                              │
│  ├── User Dashboard & Profile Management                   │
│  ├── Wallet Management (APTOS, Arbitrum)                  │
│  ├── Subscription Plans & Billing                          │
│  ├── AI Agents Configuration                              │
│  └── Telegram Bot Management                               │
├─────────────────────────────────────────────────────────────┤
│  Backend (FastAPI + PostgreSQL)                           │
│  ├── Authentication & Authorization                        │
│  ├── AI Agents & RAG Processing                            │
│  ├── Document Processing & Analysis                        │
│  ├── Wallet & Blockchain Integration                       │
│  ├── Subscription & Payment Processing                     │
│  └── Telegram Bot Management                               │
├─────────────────────────────────────────────────────────────┤
│  Background Services (Celery + Redis)                      │
│  ├── Document Processing Tasks                             │
│  ├── Wallet Monitoring & Transactions                      │
│  ├── Telegram Notifications                               │
│  └── Subscription Management                               │
├─────────────────────────────────────────────────────────────┤
│  Monitoring & Observability                                │
│  ├── Prometheus + Grafana                                  │
│  ├── Loki + Promtail (Logs)                               │
│  └── Flower (Celery Monitoring)                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Быстрый старт / Quick Start

### 1. Клонирование репозитория / Clone Repository
```bash
git clone https://github.com/mp4treiser/mara-ai.git
cd mara-ai
```

### 2. Настройка переменных окружения / Environment Setup
```bash
# Скопируйте и настройте переменные окружения
cp .env.example .env
# Отредактируйте .env файл с вашими настройками
```

### 3. Запуск через Docker Compose / Run with Docker Compose
```bash
# Запуск всех сервисов
docker-compose up --build

# Или в фоновом режиме
docker-compose up -d --build
```

### 4. Доступ к приложению / Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/docs
- **Telegram Bot Manager**: http://localhost:8001
- **Flower (Celery)**: http://localhost:5555
- **Grafana**: http://localhost:3002 (admin/admin)
- **Prometheus**: http://localhost:9090

---

## 🎯 Основные возможности / Key Features

### 🤖 AI-агенты и RAG
- **Обработка документов**: PDF, DOCX, XLSX, TXT
- **RAG-поиск**: Семантический поиск по документации
- **AI-анализ**: Автоматический анализ контента
- **Настраиваемые агенты**: Создание собственных AI-агентов

### 💰 Блокчейн кошельки
- **APTOS кошельки**: Генерация и управление
- **Arbitrum поддержка**: Мониторинг транзакций
- **USDT балансы**: Отслеживание в реальном времени
- **Безопасность**: Шифрование seed-фраз

### 📱 Telegram интеграция
- **Мониторинг чатов**: Отслеживание сообщений
- **Уведомления**: Автоматические алерты
- **Бот-менеджер**: Управление множественными ботами
- **Webhook поддержка**: Интеграция с внешними системами

### 💳 Подписки и платежи
- **Гибкие планы**: Настраиваемые тарифы
- **USDT платежи**: Поддержка TRC20
- **Автоматическое списание**: Периодические платежи
- **Аналитика**: Детальная статистика использования

### 📊 Мониторинг и аналитика
- **Prometheus метрики**: Система мониторинга
- **Grafana дашборды**: Визуализация данных
- **Логирование**: Централизованные логи
- **Health checks**: Проверка состояния сервисов

---

## 🛠️ Технологический стек / Tech Stack

### Backend
- **FastAPI** - Современный Python web-фреймворк
- **PostgreSQL** - Основная база данных
- **Redis** - Кэширование и очереди
- **Celery** - Фоновые задачи
- **SQLAlchemy** - ORM
- **Alembic** - Миграции БД
- **Pydantic** - Валидация данных
- **LangChain** - AI/ML интеграция
- **ChromaDB** - Векторная база данных
- **Ollama** - Локальные LLM модели

### Frontend
- **React 18** - Современный UI фреймворк
- **TypeScript** - Типизированный JavaScript
- **React Router** - Клиентская маршрутизация
- **Webpack** - Сборка проекта
- **Context API** - Управление состоянием

### DevOps & Monitoring
- **Docker & Docker Compose** - Контейнеризация
- **Prometheus** - Метрики и мониторинг
- **Grafana** - Визуализация данных
- **Loki + Promtail** - Централизованные логи
- **Flower** - Мониторинг Celery
- **Nginx** - Обратный прокси

### Blockchain & Crypto
- **Web3.py** - Ethereum интеграция
- **ARBITRUM** - ARBITRUM
- **USDT** - Платежи
- **HD Wallet** - Генерация кошельков
- **BIP39/BIP44** - Стандарты кошельков

---

## 📁 Структура проекта / Project Structure

```
mara-ai/
├── backend/                    # Backend сервис
│   ├── src/
│   │   ├── account/            # Управление пользователями
│   │   ├── agents/             # AI-агенты и RAG
│   │   ├── auth/               # Аутентификация
│   │   ├── core/               # Основные настройки
│   │   ├── tasks/              # Celery задачи
│   │   └── aiogram_bot/        # Telegram боты
│   ├── alembic/                # Миграции БД
│   ├── tests/                  # Тесты
│   └── Dockerfile*             # Docker конфигурации
├── frontend/                   # Frontend приложение
│   ├── src/
│   │   ├── components/         # React компоненты
│   │   ├── pages/              # Страницы приложения
│   │   ├── api/                # API клиенты
│   │   └── contexts/           # React контексты
│   └── Dockerfile              # Frontend Docker
├── docs/                       # Документация
├── docker-compose.yml          # Основная конфигурация
├── docker-compose-*.yml        # Дополнительные сервисы
└── README.md                   # Этот файл
```

---

## 🔧 Разработка / Development

### Backend разработка
```bash
cd backend
poetry install
poetry run uvicorn main:app --reload
```

### Frontend разработка
```bash
cd frontend
npm install
npm start
```

### Запуск тестов
```bash
# Backend тесты
cd backend
poetry run pytest

# Frontend тесты
cd frontend
npm test
```

---

## 📈 Мониторинг / Monitoring

### Доступные сервисы
- **Grafana**: http://localhost:3002 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Flower**: http://localhost:5555
- **PostgreSQL Exporter**: http://localhost:9187

### Основные метрики
- Производительность API
- Использование ресурсов
- Статус Celery задач
- Блокчейн транзакции
- Telegram боты

---

## 🔒 Безопасность / Security

- **JWT токены** для аутентификации
- **bcrypt** для хеширования паролей
- **Шифрование** seed-фраз кошельков
- **CORS** настройки
- **Rate limiting** для API
- **Валидация** всех входных данных

---

## 📄 Лицензия / License

MIT License - см. файл [LICENSE](LICENSE) для деталей.

---

## 🤝 Поддержка / Support

- **Issues**: [GitHub Issues](https://github.com/mp4treiser/mara-ai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/mp4treiser/mara-ai/discussions)
- **Email**: mp4treiser@gmail.com

---

## 🚀 Roadmap

- [ ] Поддержка дополнительных блокчейнов
- [ ] Мобильное приложение
- [ ] Расширенная аналитика
- [ ] API для внешних интеграций
- [ ] Машинное обучение для оптимизации
