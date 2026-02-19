FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /code

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Установка gunicorn (если нет в requirements.txt)
RUN pip install --no-cache-dir gunicorn

CMD ["gunicorn", "uni_school.wsgi:application", "--bind", "0.0.0.0:8000"]
