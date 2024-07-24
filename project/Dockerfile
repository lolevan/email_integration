# Используем официальный образ Python
FROM python:3.12

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем requirements.txt и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Открываем порты для Daphne и Django
EXPOSE 8000 8001

# Запускаем миграции и сервера
CMD ["sh", "-c", "sleep 10 && python manage.py migrate && daphne -b 0.0.0.0 -p 8001 project.asgi:application"]
