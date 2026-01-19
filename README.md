# Платформа онлайн-обучения

Система управления онлайн-курсами для университета: регистрация, оплата, материалы, Celery-задачи, фоновые процессы.

---

## 🧩 Главные компоненты

| Компонент | Версия / Использование |
|--------|---------------------|
| Django | 5.0+ |
| Python | 3.12 |
| PostgreSQL | 16.0 |
| Redis | 7.4.7 |
| Celery | Для фоновых задач |
| django-celery-beat | Периодические задачи |
| Docker | Контейнеризация |
| docker-compose | Оркестрация сервисов |

---

## 📁 Структура проекта
.  ├── Dockerfile
   ├── docker-compose.yml
   ├── requirements.txt
   ├── .env
   ├── config/
   │   └── redis.conf
   ├── uni_school/
   │   ├── settings.py
   │   ├── urls.py
   │   └── ...
   ├── users/ # Управление пользователями
   ├── materials/ # Материалы курсов
   └── ...
---

## 🛠 Настройка окружения

### 1. Создайте файл `.env`

---
### env
База данных
NAME=uni_school_db 
USER=postgres 
PASSWORD=*******

### Django
SECRET_KEY=django-insecure-... # замените на свой 

DEBUG=True

### Email (Yandex)
EMAIL_HOST=smtp.yandex.ru 
EMAIL_PORT=465 
EMAIL_USE_TLS=False 
EMAIL_USE_SSL=True 
EMAIL_HOST_USER=*******@yandex.ru 
EMAIL_HOST_PASSWORD=***************** 
DEFAULT_FROM_EMAIL=*******@yandex.ru
### Celery
CELERY_BROKER_URL=redis://redis:6379/0 
CELERY_RESULT_BACKEND=redis://redis:6379/0


> 💡 Сохраните `.env` в корне проекта.

---

## 🐳 Запуск приложения

### 1. Сборка и запуск
- bash docker-compose down -v # Очистка предыдущих контейнеров и томов 
- docker-compose up --build # Сборка и запуск
- docker-compose up -d # Запуск в фоновом режиме
- docker-compose logs -f # Просмотр логов
- docker-compose down # Остановка
- docker-compose up --scale celery=3 # Масштабирование celery
- Приложение будет доступно по адресу: `http://localhost:8000`

---

## ⚙️ Архитектура сервисов (`docker-compose.yml`)

| Сервис | Назначение |
|-------|----------|
| `db` | PostgreSQL 16.0, хранение данных |
| `redis` | Хранилище для Celery и кэширования |
| `web` | Django-сервер (`runserver`) |
| `celery` | Воркер для фоновых задач |
| `beat` | Планировщик периодических задач |

---

### 🔗 Зависимости

- `web`, `celery`, `beat` зависят от `db` и `redis`
- `web` применяет миграции при старте
- `beat` зависит от `web` (`condition: service_started`) — чтобы миграции уже были применены

---

## 🔄 Миграции и инициализация

### Важно: Миграции выполняются в `web`
- yaml command: bash -c "python manage.py migrate --noinput && ..."
- Не запускайте миграции в `celery` или `beat` — это вызовет `duplicate key` ошибки
- `web` должен стартовать **первым** среди Django-сервисов

---

## 🧵 Celery и фоновые задачи

### Сервис `celery`

- Запускает воркер: `celery -A uni_school worker -l info`
- Обрабатывает:
  - Оповещения
  - Отправку писем
  - Обновление статуса оплат
  - Другие async-операции

### Сервис `beat`

- Планировщик: `celery -A uni_school beat`
- Использует `django-celery-beat` для хранения расписания в БД
- Задачи:
  - Ежедневная проверка оплат
  - Генерация отчётов
  - Напоминания

---

## 🔄 Healthchecks

| Сервис | Проверка |
|-------|--------|
| `db` | `pg_isready -U $$USER -d $$NAME -h localhost` |
| `redis` | `redis-cli ping` |

> ❗ `$$` в Docker Compose означает одинарный `$` — используется для подстановки переменных в `healthcheck`

---

## 📦 Dockerfile

### dockerfile 
FROM python:3.12 
LABEL authors="alexey"
WORKDIR /code COPY requirements.txt ./ 
RUN pip install --no-cache-dir -r requirements.txt 
COPY . /code/
RUN apt-get update && apt-get install -y
gcc
libpq-dev
&& apt-get clean
&& rm -rf /var/lib/apt/lists/*
EXPOSE 8000


> ⚠️ Команда запуска (`command`) задаётся в `docker-compose.yml`, не в `Dockerfile`

---

## 🧪 Тестирование

После запуска проверьте:
bash
### Логи
- docker-compose logs web 
- docker-compose logs celery 
- docker-compose logs beat

### Проверка подключения к БД
- docker-compose exec db psql -U postgres -d uni_school_db -c "\conninfo"

### Проверка Redis
- docker-compose exec redis redis-cli ping

---

## 🔒 Рекомендации

### 1. Безопасность
- Не используйте `DEBUG=True` на продакшене
- Замените `SECRET_KEY`
- Используйте в корне проекта файл `.env.sample`. Необходимо сделать копию с именем `.env` и заполнить.

### 2. Масштабирование
- `celery` можно масштабировать: `docker-compose up --scale celery=3`
- Используйте `supervisord` или `process manager` в продакшене

---

## 🆘 Возможные ошибки и решения

| Ошибка | Решение |
|------|--------|
| `FATAL: password authentication failed` | Убедитесь, что `POSTGRES_USER` и `POSTGRES_PASSWORD` переданы в `db` |
| `migrate: duplicate key` | Запускайте `migrate` только в одном сервисе |
| `KeyError: 'id'` | Вторичная ошибка Docker Compose — можно игнорировать, если сервисы работают |

---

## 📞 Поддержка

Разработчик: Алексей  
Email: alex0236889@yandex.ru  
Проект: uni_school - онлайн образовательная платформа.