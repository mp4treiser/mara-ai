#!/bin/bash

# Entrypoint скрипт для Mara AI Backend
set -e

echo "🚀 Запуск Mara AI Backend..."

# Функция для ожидания готовности базы данных
wait_for_db() {
    echo "⏳ Ожидание готовности базы данных..."
    
    # Ждем, пока PostgreSQL будет готов
    until pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME; do
        echo "База данных недоступна, ждем..."
        sleep 2
    done
    
    echo "✅ База данных готова!"
}

# Функция для запуска миграций
run_migrations() {
    echo "🔄 Запуск миграций базы данных..."
    
    # Проверяем, есть ли файлы миграций
    if [ -d "alembic/versions" ] && [ "$(ls -A alembic/versions)" ]; then
        echo "Найдены файлы миграций, применяем..."
        alembic upgrade head
        echo "✅ Миграции применены!"
    else
        echo "Файлы миграций не найдены, пропускаем..."
    fi
}

# Функция для проверки переменных окружения
check_environment() {
    echo "🔍 Проверка переменных окружения..."
    
    # Проверяем обязательные переменные
    if [ -z "$DB_HOST" ]; then
        echo "❌ DB_HOST не установлен"
        exit 1
    fi
    
    if [ -z "$DB_PORT" ]; then
        echo "❌ DB_PORT не установлен"
        exit 1
    fi
    
    if [ -z "$DB_USER" ]; then
        echo "❌ DB_USER не установлен"
        exit 1
    fi
    
    if [ -z "$DB_PASS" ]; then
        echo "❌ DB_PASS не установлен"
        exit 1
    fi
    
    if [ -z "$DB_NAME" ]; then
        echo "❌ DB_NAME не установлен"
        exit 1
    fi
    
    echo "✅ Переменные окружения проверены"
}

# Функция для создания директории логов
create_logs_dir() {
    if [ ! -d "logs" ]; then
        mkdir -p logs
        echo "📁 Создана директория logs"
    fi
}

# Функция для запуска приложения
start_app() {
    echo "🌟 Запуск FastAPI приложения..."
    
    # Определяем количество воркеров
    WORKERS=${WORKERS:-1}
    
    # Определяем хост и порт
    HOST=${HOST:-"0.0.0.0"}
    PORT=${PORT:-8000}
    
    echo "📊 Количество воркеров: $WORKERS"
    echo "🌐 Хост: $HOST"
    echo "🔌 Порт: $PORT"
    
    # Запускаем uvicorn
    exec uvicorn main:app \
        --host $HOST \
        --port $PORT \
        --workers $WORKERS \
        --reload \
        --log-level info
}

# Основная логика
main() {
    echo "=================================="
    echo "    Mara AI Backend Container"
    echo "=================================="
    
    # Проверяем переменные окружения
    check_environment
    
    # Создаем директорию для логов
    create_logs_dir
    
    # Ждем готовности базы данных
    wait_for_db
    
    # Запускаем миграции
    run_migrations
    
    # Запускаем приложение
    start_app
}

# Запускаем основную функцию
main "$@"
