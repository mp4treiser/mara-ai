# Система аутентификации

## Архитектура

Ваша структура проекта правильно организована:

```
backend/src/
├── account/          # Управление пользователями (CRUD)
│   ├── models/       # Модели данных
│   ├── repositories/ # Работа с БД
│   ├── services/     # Бизнес-логика
│   ├── schemas/      # Pydantic схемы
│   └── routers/      # API эндпоинты
└── auth/             # Аутентификация и авторизация
    ├── dependencies.py # Зависимости для защиты эндпоинтов
    ├── routers/      # Login/Register эндпоинты
    ├── schemas/      # Схемы аутентификации
    └── services/     # Логика аутентификации
```

## Разделение ответственности

### `src/account` - Управление пользователями
- **CRUD операции** с профилем пользователя
- **Бизнес-логика** управления данными
- **Публичные эндпоинты** для администраторов

### `src/auth` - Аутентификация
- **Login/Register** процессы
- **JWT токены** и их валидация
- **Защита эндпоинтов** через зависимости

## Эндпоинты

### Аутентификация (`/api/v1/auth/`)

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| POST | `/register` | Регистрация нового пользователя |
| POST | `/login` | Вход в систему |
| GET | `/health` | Проверка работоспособности |

### Пользователи (`/api/v1/users/`)

| Метод | Эндпоинт | Описание | Аутентификация |
|-------|----------|----------|----------------|
| GET | `/` | Все пользователи | Нет |
| GET | `/{user_id}` | Пользователь по ID | Нет |
| POST | `/` | Создание пользователя | Нет |
| PUT | `/{user_id}` | Обновление пользователя | Нет |
| DELETE | `/{user_id}` | Удаление пользователя | Нет |
| GET | `/me/profile` | Мой профиль | Да |
| PUT | `/me/profile` | Обновление моего профиля | Да |
| GET | `/admin/all` | Все пользователи (админ) | Да (суперпользователь) |

## Настройка

### 1. Переменные окружения

Добавьте в `.env`:

```env
# JWT настройки
SECRET_KEY=your-super-secret-key-here-make-it-long-and-random
ACCESS_TOKEN_EXPIRE_MINUTES=30

# База данных
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASS=password
DB_NAME=mara_ai
```

### 2. Установка зависимостей

```bash
cd backend
poetry install
```

### 3. Запуск

```bash
uvicorn main:app --reload
```

## Примеры использования

### Регистрация

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "confirm_password": "password123",
    "company": "Example Corp",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

**Ответ:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "company": "Example Corp",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": true
}
```

### Вход в систему

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

**Ответ:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Защищенные эндпоинты

```bash
# Получение профиля
curl -X GET "http://localhost:8000/api/v1/users/me/profile" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Обновление профиля
curl -X PUT "http://localhost:8000/api/v1/users/me/profile" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Jane",
    "company": "New Company"
  }'
```

## Зависимости для защиты эндпоинтов

```python
from src.auth.dependencies import get_current_user, get_current_active_user, get_current_superuser

# Любой аутентифицированный пользователь
@router.get("/protected")
async def protected_endpoint(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello {current_user.email}"}

# Только активные пользователи
@router.get("/active-only")
async def active_only_endpoint(current_user: User = Depends(get_current_active_user)):
    return {"message": "You are active!"}

# Только суперпользователи
@router.get("/admin-only")
async def admin_endpoint(current_user: User = Depends(get_current_superuser)):
    return {"message": "Admin access granted"}
```

## Безопасность

### Пароли
- Хешируются с помощью bcrypt
- Минимальная длина: 6 символов
- Проверка совпадения при регистрации

### JWT токены
- Алгоритм: HS256
- Время жизни: настраивается через переменную окружения
- Содержит ID пользователя в поле `sub`

### Валидация
- Email проверяется на уникальность
- Пароли проверяются на совпадение
- Проверка активности пользователя при входе

## Преимущества вашей архитектуры

1. **Разделение ответственности** - аутентификация отделена от управления пользователями
2. **Переиспользование** - модель User используется в обоих модулях
3. **Масштабируемость** - легко добавлять новые функции аутентификации
4. **Безопасность** - правильная обработка паролей и токенов
5. **Гибкость** - разные уровни доступа для разных эндпоинтов