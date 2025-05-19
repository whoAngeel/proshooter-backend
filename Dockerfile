FROM python:3.12-slim

# SET ENVIRONMENT VARIABLES
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# SET WORKING DIRECTORY
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copiar solo el archivo de requisitos primero
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -v -r requirements.txt

# Ahora copiar el resto del código fuente
COPY . .

# Create a non-root user and switch to it
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Para desarrollo (cuando se usa con volumes en docker-compose)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Para producción (descomenta esta línea y comenta la anterior cuando despliegues)
# CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
