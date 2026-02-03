#!/bin/bash

# Скрипт первоначальной настройки сервера для NPO Arsenal
# Запускать от root на сервере

set -e

echo "=== Настройка сервера для NPO Arsenal ==="

# Обновление системы
echo "1. Обновление системы..."
apt update && apt upgrade -y

# Установка необходимых пакетов
echo "2. Установка необходимых пакетов..."
apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    git \
    ufw

# Установка Docker
echo "3. Установка Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    systemctl enable docker
    systemctl start docker
fi

# Установка Docker Compose (уже включен в новые версии Docker)
echo "4. Проверка Docker Compose..."
docker compose version

# Настройка firewall
echo "5. Настройка firewall..."
ufw allow ssh
ufw allow http
ufw allow https
ufw --force enable

# Создание директории проекта
echo "6. Создание директории проекта..."
mkdir -p /opt/arsenal
cd /opt/arsenal

# Клонирование репозитория (замените на ваш URL)
echo "7. Репозиторий будет склонирован после настройки GitHub..."

# Создание директорий для SSL
echo "8. Создание директорий для SSL..."
mkdir -p nginx/ssl certbot/www certbot/conf

echo ""
echo "=== Первоначальная настройка завершена ==="
echo ""
echo "Следующие шаги:"
echo "1. Склонируйте репозиторий: git clone <your-repo-url> /opt/arsenal"
echo "2. Создайте файл .env: cp .env.example .env && nano .env"
echo "3. Убедитесь что домен npo-arsenal.ru указывает на IP сервера"
echo "4. Запустите первичный деплой: ./scripts/deploy.sh"
