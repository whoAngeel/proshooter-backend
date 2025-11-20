FROM python:3.11-slim

WORKDIR /app

# Fix: Usar mirrors alternativos y verificar conectividad
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libgl1-mesa-glx \
    libglib2.0-0 \
    python3-dev \
    build-essential \
    libfreetype6-dev \
    pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip wheel setuptools && \
    pip install --no-cache-dir numpy && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir alembic

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8000"]
