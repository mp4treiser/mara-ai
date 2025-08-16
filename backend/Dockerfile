# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    postgresql-client \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY pyproject.toml poetry.lock ./

# Устанавливаем Poetry
RUN pip install poetry

# Настраиваем Poetry для работы в контейнере
RUN poetry config virtualenvs.create false

# Устанавливаем зависимости
RUN poetry install --no-root

# Копируем исходный код
COPY . .

# Делаем entrypoint скрипт исполняемым
RUN chmod +x entrypoint.sh

# Создаем пользователя для безопасности
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Открываем порт
EXPOSE 8000
EXPOSE 80
EXPOSE 3001

# Используем entrypoint скрипт
ENTRYPOINT ["./entrypoint.sh"]
