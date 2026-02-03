#!/bin/bash
# Скрипт для настройки Let's Encrypt SSL
# Запускать после настройки DNS для npo-arsenal.ru

set -e

DOMAIN="npo-arsenal.ru"
EMAIL="npo.arsenal.info@mail.ru"
ARSENAL_DIR="/opt/arsenal"

echo "=== Проверка DNS ==="
if ! nslookup $DOMAIN > /dev/null 2>&1; then
    echo "ОШИБКА: DNS для $DOMAIN не настроен!"
    echo "Настройте A-запись: $DOMAIN -> $(curl -s ifconfig.me)"
    exit 1
fi

echo "DNS настроен корректно"

echo "=== Получение Let's Encrypt сертификата ==="
docker exec arsenal-certbot certbot certonly \
    --webroot \
    -w /var/www/certbot \
    -d $DOMAIN \
    -d www.$DOMAIN \
    --email $EMAIL \
    --agree-tos \
    --non-interactive \
    --force-renewal

echo "=== Обновление nginx конфигурации ==="
cat > $ARSENAL_DIR/nginx/nginx.conf << 'NGINXCONF'
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml application/javascript;

    limit_req_zone $binary_remote_addr zone=one:10m rate=10r/s;

    upstream django {
        server web:8000;
    }

    # HTTP -> HTTPS redirect
    server {
        listen 80;
        server_name npo-arsenal.ru www.npo-arsenal.ru;

        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }

        location / {
            return 301 https://$host$request_uri;
        }
    }

    # HTTPS server с Let's Encrypt
    server {
        listen 443 ssl;
        http2 on;
        server_name npo-arsenal.ru www.npo-arsenal.ru;

        ssl_certificate /etc/letsencrypt/live/npo-arsenal.ru/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/npo-arsenal.ru/privkey.pem;
        ssl_session_timeout 1d;
        ssl_session_cache shared:SSL:50m;
        ssl_session_tickets off;

        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        add_header Strict-Transport-Security "max-age=63072000" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;

        location /static/ {
            alias /app/staticfiles/;
            expires 30d;
            add_header Cache-Control "public, immutable";
        }

        location /media/ {
            alias /app/media/;
            expires 30d;
            add_header Cache-Control "public";
        }

        location / {
            limit_req zone=one burst=20 nodelay;
            proxy_pass http://django;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto https;
            proxy_connect_timeout 30s;
            proxy_read_timeout 30s;
        }
    }
}
NGINXCONF

echo "=== Перезапуск nginx ==="
cd $ARSENAL_DIR
docker compose restart nginx

echo "=== Готово! ==="
echo "Сайт доступен по адресу: https://$DOMAIN"
