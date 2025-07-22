# mara-ai

**Monitoring & Assistance Reactive Agent Platform**

---

## Overview / Обзор

**English:**  
mara-ai is a platform for business monitoring and automation using AI agents. It leverages RAG (Retrieval-Augmented Generation) principles to help companies react to alerts based on internal documentation and automate routine responses. The system includes a web UI (React) and a backend (FastAPI), with support for agent configuration, alert routing, analytics, and subscription management.

**Русский:**  
mara-ai — это платформа для мониторинга и автоматизации бизнес-процессов с помощью AI-агентов. Использует принцип RAG (Retrieval-Augmented Generation) для обработки алертов на основе внутренней документации компании и автоматизации типовых реакций. Включает web-интерфейс (React) и backend (FastAPI), поддерживает настройку агентов, маршрутизацию алертов, аналитику и управление подписками.

---

## Project Structure / Структура проекта

```
├── backend/           # Backend (FastAPI, Alembic, Celery, AI agents)
│   ├── src/
│   │   ├── agents/         # AI agents logic
│   │   ├── core/           # Core settings, utils
│   │   ├── notifications/  # Notification logic (Telegram)
│   │   ├── tasks/          # Celery background tasks
│   │   ├── user/           # User management
│   │   └── ...
│   ├── Dockerfile
│   └── pyproject.toml / requirements.txt
│
├── frontend/          # Frontend (React)
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── api/
│   │   ├── hooks/
│   │   ├── utils/
│   │   ├── styles/
│   │   └── app.tsx
│   ├── public/
│   ├── Dockerfile
│   └── package.json
│
├── docs/              # Документация, схемы, диаграммы
├── docker-compose.yml # Сборка всех сервисов
├── .env               # Переменные окружения
└── README.md
```

---

## Quick Start / Быстрый старт

1. **Clone the repository / Клонируйте репозиторий:**
   ```bash
   git clone https://github.com/mp4treiser/mara-ai.git
   cd mara-ai
   ```
2. **Configure environment variables / Настройте .env:**
   - Copy `.env.example` to `.env` and fill in required values.
3. **Run with Docker Compose / Запустите через Docker Compose:**
   ```bash
   docker-compose up --build
   ```
4. **Access the app / Откройте приложение:**
   - Frontend: http://localhost:3000
   - Backend (API docs): http://localhost:8000/docs

---

## Features / Возможности

- AI agents for alert processing / AI-агенты для обработки алертов
- RAG-based document search / Поиск по документации (RAG)
- Telegram & email notifications / Уведомления в Telegram
- User dashboard & analytics / Дашборды и аналитика
- Subscription & billing (USDT TRC20) / Подписки и оплата (USDT TRC20)
- Support ticket system / Система тикетов поддержки

---

## Contributing / Вклад

We welcome contributions! See [docs/CONTRIBUTING.md] for details.  
Будем рады любым PR и предложениям! Подробнее — в [docs/CONTRIBUTING.md].

---

## License / Лицензия

MIT License
