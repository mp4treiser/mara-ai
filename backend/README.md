# 🚀 MARA-AI Backend

**FastAPI Backend для платформы MARA-AI**

Высокопроизводительный backend сервис с поддержкой AI-агентов, блокчейн кошельков, Telegram ботов и системы подписок.

---

## 🏗️ Архитектура

### Основные модули

```
backend/src/
├── account/              # Управление пользователями и профилями
│   ├── models/           # SQLAlchemy модели
│   ├── repositories/     # Слой доступа к данным
│   ├── services/         # Бизнес-логика
│   ├── schemas/          # Pydantic схемы
│   └── routers/          # API эндпоинты
├── agents/               # AI-агенты и RAG система
│   ├── models/           # Модели агентов и документов
│   ├── repositories/     # Работа с агентами
│   ├── services/         # Логика AI-агентов
│   ├── routers/          # API для агентов
│   └── utils/           # Утилиты для RAG
├── auth/                 # Аутентификация и авторизация
│   ├── models/           # Модели пользователей
│   ├── services/         # JWT и безопасность
│   ├── routers/          # Login/Register
│   └── schemas/          # Схемы аутентификации
├── core/                 # Основные настройки
│   ├── config.py         # Конфигурация приложения
│   ├── database.py       # Подключение к БД
│   ├── celery_app.py     # Celery конфигурация
│   ├── middlewares/      # Middleware компоненты
│   └── monitoring/       # Мониторинг и метрики
├── tasks/                # Celery фоновые задачи
│   ├── document_tasks.py # Обработка документов
│   ├── wallet_tasks.py   # Мониторинг кошельков
│   └── telegram_tasks.py # Telegram уведомления
└── aiogram_bot/          # Telegram боты
    └── main.py           # Менеджер ботов
```

---

## 🎯 Основные возможности

### 🔐 Аутентификация и авторизация
- **JWT токены** с настраиваемым временем жизни
- **bcrypt** хеширование паролей
- **Роли пользователей** (user, admin, superuser)
- **Защищенные эндпоинты** с middleware

### 🤖 AI-агенты и RAG
- **Обработка документов**: PDF, DOCX, XLSX, TXT
- **Векторный поиск** с ChromaDB
- **LangChain интеграция** для RAG
- **Ollama** локальные LLM модели
- **Семантический поиск** по документации

### 💰 Блокчейн кошельки
- **ARBITRUM кошельки**: Генерация и управление
- **Arbitrum поддержка**: Мониторинг транзакций
- **USDT балансы**: Отслеживание в реальном времени
- **Шифрование** seed-фраз с AES-256

### 📱 Telegram интеграция
- **Множественные боты**: Управление через API
- **Мониторинг чатов**: Отслеживание сообщений
- **Webhook поддержка**: Интеграция с внешними системами
- **Уведомления**: Автоматические алерты

### 💳 Подписки и платежи
- **Гибкие планы**: Настраиваемые тарифы
- **USDT платежи**: Поддержка TRC20
- **Автоматическое списание**: Периодические платежи
- **Аналитика**: Детальная статистика

### 📊 Мониторинг и метрики
- **Prometheus метрики**: Система мониторинга
- **Health checks**: Проверка состояния
- **Логирование**: Структурированные логи
- **Performance tracking**: Отслеживание производительности

---

## 🛠️ Технологический стек

### Основные технологии
- **FastAPI** - Современный Python web-фреймворк
- **PostgreSQL** - Основная база данных
- **Redis** - Кэширование и очереди
- **Celery** - Фоновые задачи
- **SQLAlchemy** - ORM с async поддержкой
- **Alembic** - Миграции БД

### AI/ML компоненты
- **LangChain** - AI/ML интеграция
- **ChromaDB** - Векторная база данных
- **Ollama** - Локальные LLM модели
- **Sentence Transformers** - Эмбеддинги
- **Hugging Face** - Pre-trained модели

### Блокчейн интеграция
- **Web3.py** - Ethereum интеграция
- **APTOS SDK** - APTOS блокчейн
- **HD Wallet** - Генерация кошельков
- **BIP39/BIP44** - Стандарты кошельков
- **Cryptography** - Шифрование

### Мониторинг и DevOps
- **Prometheus Client** - Метрики
- **Flower** - Мониторинг Celery
- **Docker** - Контейнеризация
- **Uvicorn** - ASGI сервер

---

## 🚀 Быстрый старт

### 1. Установка зависимостей
```bash
cd backend
poetry install
```

### 2. Настройка переменных окружения
```bash
# Скопируйте .env.example в .env и настройте
cp .env.example .env
```

### 3. Инициализация базы данных
```bash
# Создание миграций
poetry run alembic revision --autogenerate -m "Initial migration"

# Применение миграций
poetry run alembic upgrade head
```

### 4. Запуск сервера
```bash
# Разработка
poetry run uvicorn main:app --reload

# Продакшн
poetry run uvicorn main:app --host 0.0.0.0 --port 8000
```

### 5. Запуск Celery
```bash
# Worker
poetry run celery -A src.core.celery_app worker --loglevel=info

# Beat (планировщик)
poetry run celery -A src.core.celery_app beat --loglevel=info

# Flower (мониторинг)
poetry run celery -A src.core.celery_app flower
```

---

## 📡 API Эндпоинты

### 🔐 Аутентификация (`/api/v1/auth/`)
| Метод | Эндпоинт | Описание | Аутентификация |
|-------|----------|----------|----------------|
| POST | `/register` | Регистрация пользователя | ❌ |
| POST | `/login` | Вход в систему | ❌ |
| GET | `/health` | Проверка работоспособности | ❌ |

### 👤 Пользователи (`/api/v1/users/`)
| Метод | Эндпоинт | Описание | Аутентификация |
|-------|----------|----------|----------------|
| GET | `/me/profile` | Мой профиль | ✅ |
| PUT | `/me/profile` | Обновление профиля | ✅ |
| GET | `/balance` | Баланс пользователя | ✅ |
| GET | `/admin/all` | Все пользователи (админ) | ✅ (admin) |

### 🤖 AI-агенты (`/api/v1/agents/`)
| Метод | Эндпоинт | Описание | Аутентификация |
|-------|----------|----------|----------------|
| GET | `/` | Список агентов | ✅ |
| POST | `/` | Создание агента | ✅ |
| GET | `/{agent_id}` | Детали агента | ✅ |
| PUT | `/{agent_id}` | Обновление агента | ✅ |
| DELETE | `/{agent_id}` | Удаление агента | ✅ |

### 📄 Документы (`/api/v1/documents/`)
| Метод | Эндпоинт | Описание | Аутентификация |
|-------|----------|----------|----------------|
| GET | `/` | Список документов | ✅ |
| POST | `/upload` | Загрузка документа | ✅ |
| GET | `/{document_id}` | Детали документа | ✅ |
| POST | `/{document_id}/analyze` | Анализ документа | ✅ |
| DELETE | `/{document_id}` | Удаление документа | ✅ |

### 💰 Кошельки (`/api/v1/wallets/`)
| Метод | Эндпоинт | Описание | Аутентификация |
|-------|----------|----------|----------------|
| GET | `/my` | Мои кошельки | ✅ |
| POST | `/generate` | Генерация кошелька | ✅ |
| GET | `/my/{network}` | Кошелек по сети | ✅ |
| GET | `/my/{network}/balance` | Баланс кошелька | ✅ |

### 📱 Telegram (`/api/v1/telegram/`)
| Метод | Эндпоинт | Описание | Аутентификация |
|-------|----------|----------|----------------|
| GET | `/configs` | Конфигурации ботов | ✅ |
| POST | `/configs` | Создание конфигурации | ✅ |
| GET | `/monitoring` | Мониторинг чатов | ✅ |
| POST | `/monitoring` | Настройка мониторинга | ✅ |

---

## 🔧 Конфигурация

### Переменные окружения

```env
# База данных
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASS=password
DB_NAME=mara_ai

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# JWT
SECRET_KEY=your-super-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Ollama
OLLAMA_HOST=localhost
OLLAMA_PORT=11434

# Блокчейн
WALLET_ENCRYPTION_KEY=your-encryption-key-here

# Telegram
TELEGRAM_BOT_TOKEN=your-bot-token
```

---

## 🧪 Тестирование

### Запуск тестов
```bash
# Все тесты
poetry run pytest

# С покрытием
poetry run pytest --cov=src

# Конкретный тест
poetry run pytest tests/test_auth.py

# Асинхронные тесты
poetry run pytest tests/test_async.py
```

### Структура тестов
```
tests/
├── conftest.py              # Фикстуры
├── constants.py             # Константы для тестов
├── fixtures/                # Тестовые данные
│   ├── users.py
│   ├── agents.py
│   └── documents.py
└── api/                     # API тесты
    └── account/
        ├── test_users.py
        └── test_auth.py
```

---

## 📊 Мониторинг

### Prometheus метрики
- **HTTP запросы**: Количество, время ответа, ошибки
- **База данных**: Подключения, запросы, транзакции
- **Celery задачи**: Выполненные, неудачные, время выполнения
- **Блокчейн**: Транзакции, балансы, ошибки

### Health checks
- **Database**: Проверка подключения к PostgreSQL
- **Redis**: Проверка подключения к Redis
- **Ollama**: Проверка доступности LLM
- **Celery**: Проверка воркеров

### Логирование
- **Структурированные логи** в JSON формате
- **Уровни логирования**: DEBUG, INFO, WARNING, ERROR
- **Контекстная информация**: User ID, Request ID, Agent ID
- **Централизованное логирование** через Loki

---

## 🔒 Безопасность

### Аутентификация
- **JWT токены** с HMAC-SHA256
- **Время жизни токенов** настраивается
- **Refresh токены** для долгосрочной сессии
- **Защита от CSRF** атак

### Авторизация
- **Роли пользователей**: user, admin, superuser
- **Права доступа** на уровне эндпоинтов
- **Проверка владения** ресурсами
- **Rate limiting** для API

### Шифрование
- **Пароли**: bcrypt с солью
- **Seed фразы**: AES-256-GCM
- **API ключи**: Хеширование SHA-256
- **Транспорт**: HTTPS/TLS 1.3

### Валидация
- **Pydantic схемы** для всех входных данных
- **SQL injection** защита через SQLAlchemy
- **XSS защита** через экранирование
- **CORS** настройки для фронтенда

---

## 🚀 Производительность

### Оптимизации
- **Async/await** для всех I/O операций
- **Connection pooling** для БД
- **Redis кэширование** для частых запросов
- **Lazy loading** для связанных объектов

### Масштабирование
- **Горизонтальное масштабирование** через Docker
- **Load balancing** для множественных инстансов
- **Database sharding** для больших объемов данных
- **CDN** для статических файлов

### Мониторинг производительности
- **APM** инструменты (если необходимо)
- **Профилирование** медленных запросов
- **Метрики времени ответа** по эндпоинтам
- **Алерты** при превышении лимитов

---

## 📚 Документация

### API документация
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI схема**: http://localhost:8000/openapi.json

### Внутренняя документация
- **Docstrings** для всех функций
- **Type hints** для всех параметров
- **Примеры использования** в комментариях
- **Архитектурные решения** в README

---

## 🤝 Разработка

### Code Style
- **Black** для форматирования кода
- **isort** для сортировки импортов
- **flake8** для проверки стиля
- **mypy** для проверки типов

### Git workflow
- **Feature branches** для новых функций
- **Pull requests** для code review
- **Automated tests** в CI/CD
- **Semantic versioning** для релизов

### Добавление новых функций
1. Создайте feature branch
2. Добавьте тесты для новой функции
3. Реализуйте функцию
4. Обновите документацию
5. Создайте pull request

---

## 📞 Поддержка

- **Issues**: [GitHub Issues](https://github.com/mp4treiser/mara-ai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/mp4treiser/mara-ai/discussions)
- **Email**: mp4treiser@gmail.com