#!/bin/bash

# Скрипт деплоя NPO Arsenal
# Запускать от root в /opt/arsenal

set -e

DOMAIN="npo-arsenal.ru"
EMAIL="npo.arsenal.info@mail.ru"

echo "=== Деплой NPO Arsenal ==="

cd /opt/arsenal

# Проверка наличия .env
if [ ! -f .env ]; then
    echo "Ошибка: Файл .env не найден!"
    echo "Создайте его: cp .env.example .env && nano .env"
    exit 1
fi

# Проверка наличия SSL сертификата
if [ ! -d "certbot/conf/live/$DOMAIN" ]; then
    echo "1. SSL сертификат не найден, получаем..."
    
    # Используем временную конфигурацию nginx
    cp nginx/nginx-initial.conf nginx/nginx.conf
    
    # Запускаем контейнеры
    docker compose up -d --build
    
    # Ждём запуска
    sleep 10
    
    # Получаем сертификат
    docker compose run --rm certbot certonly \
        --webroot \
        --webroot-path=/var/www/certbot \
        --email $EMAIL \
        --agree-tos \
        --no-eff-email \
        -d $DOMAIN \
        -d www.$DOMAIN
    
    # Восстанавливаем production конфигурацию nginx
    git checkout nginx/nginx.conf
    
    # Перезапускаем nginx
    docker compose restart nginx
    
    echo "SSL сертификат получен!"
else
    echo "1. SSL сертификат уже существует"
fi

# Пересборка и запуск
echo "2. Пересборка контейнеров..."
docker compose build --no-cache

echo "3. Запуск контейнеров..."
docker compose up -d

echo "4. Применение миграций..."
docker compose exec -T web python manage.py migrate --noinput

echo "5. Очистка..."
docker system prune -f

echo ""
echo "=== Деплой завершён ==="
echo "Сайт доступен по адресу: https://$DOMAIN"
docker compose ps
