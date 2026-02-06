FROM nginx:latest

# Создание директории для статических файлов
RUN mkdir -p /app/staticfiles

COPY ./nginx.conf /etc/nginx/nginx.conf

EXPOSE 8080
