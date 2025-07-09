# Documentación Docker para Pro Shooter API

Esta documentación describe el proceso para desarrollar localmente y compartir el backend Pro Shooter API utilizando Docker.

## Estructura del Proyecto

El proyecto usa Docker y Docker Compose para crear un entorno de desarrollo consistente y facilitar el despliegue. La estructura consiste en:

- **API**: Aplicación FastAPI con lógica de negocio
- **Base de Datos**: PostgreSQL para almacenamiento de datos

## Entorno de Desarrollo

El entorno de desarrollo utiliza un archivo `docker-compose.yaml` con contenedores para el backend y la base de datos.

### Archivo docker-compose.yaml (Desarrollo)

```yaml
services:
  postgres:
    image: postgres:14-alpine
    container_name: proshooter_bd
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U angel -d proshooter_db"]
      interval: 5s
      timeout: 5s
      retries: 5
    environment:
      POSTGRES_USER: angel
      POSTGRES_PASSWORD: angel
      POSTGRES_DB: proshooter_db
    networks:
      - proshooter-network

  api:
    container_name: proshooter_api
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    volumes:
      - ./:/app
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      - DATABASE_URL=postgresql://angel:angel@postgres:5432/proshooter_db
      - SECRET_KEY=fasdfjasfsdfkasjdfoiadbasdbasd
    networks:
      - proshooter-network
    env_file:
      - .env
    restart: always
    command: >
      bash -c "alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload"

networks:
  proshooter-network:
    driver: bridge

volumes:
  postgres_data:
```

### Dockerfile (API)

```dockerfile
FROM python:3.12-slim

# SET WORKING DIRECTORY
WORKDIR /app

# SET ENVIRONMENT VARIABLES
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# INSTALL DEPENDENCIES
COPY requirements.txt .
# Install basic packages first
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
# Now install the requirements with verbose output
RUN pip install --no-cache-dir -v -r requirements.txt

# Copy project
COPY . .

# Create a non-root user and switch to it
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
```

## Compartir con otros desarrolladores

Para compartir la aplicación con otros desarrolladores, se utilizan dos imágenes de Docker:

1. Una imagen para la **API** con el código actual
2. Una imagen de **PostgreSQL** con datos preconfigurados

### Proceso para actualizar imágenes

Cuando se realizan cambios en el código o en la base de datos, es necesario actualizar las imágenes y subirlas a Docker Hub.

#### postgres.Dockerfile

Este archivo se utiliza para crear una imagen de PostgreSQL con datos precargados:

```dockerfile
FROM postgres:14-alpine
COPY db_backup.sql /docker-entrypoint-initdb.d/
ENV POSTGRES_USER=angel
ENV POSTGRES_PASSWORD=angel
ENV POSTGRES_DB=proshooter_db
```

#### Script de actualización (update-images.sh)

```bash
#!/bin/bash

echo "Actualizando imágenes de Pro Shooter..."

# Asegurarse de que los contenedores estén corriendo
docker-compose up -d

# Esperar a que los servicios estén disponibles
echo "Esperando a que los servicios estén disponibles..."
sleep 10

# Crear backup de la base de datos
echo "Creando respaldo de la base de datos..."
docker-compose exec -T postgres pg_dump -U angel -d proshooter_db > db_backup.sql

# Verificar el tamaño del backup
backup_size=$(wc -c < db_backup.sql)
echo "Tamaño del backup: $backup_size bytes"

if [ $backup_size -lt 1000 ]; then
    echo "ADVERTENCIA: El archivo de backup parece muy pequeño. Verifica que contenga datos."
    exit 1
fi

# Construir y subir la imagen de PostgreSQL
echo "Construyendo imagen de PostgreSQL con datos..."
docker build -t subkey/proshooter-db:latest -f postgres.Dockerfile .
echo "Subiendo imagen de PostgreSQL a Docker Hub..."
docker push subkey/proshooter-db:latest

# Construir y subir la imagen de la API
echo "Construyendo imagen de la API..."
docker-compose build api
docker tag $(docker-compose images -q api) subkey/proshooter-api:latest
echo "Subiendo imagen de la API a Docker Hub..."
docker push subkey/proshooter-api:latest

echo "¡Imágenes actualizadas con éxito!"
```

### Archivo docker-compose.yaml para otros desarrolladores

Los otros desarrolladores solo necesitan este archivo:

```yaml
services:
  postgres:
    image: subkey/proshooter-db:latest
    container_name: proshooter_bd_dev
    ports:
      - "5432:5432"
    volumes:
      - proshooter_db_data:/var/lib/postgresql/data
    environment:
      POSTGRES_USER: angel
      POSTGRES_PASSWORD: angel
      POSTGRES_DB: proshooter_db
    networks:
      - proshooter-network-dev
    restart: always
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U angel -d proshooter_db"]
      interval: 5s
      timeout: 5s
      retries: 5

  api:
    image: subkey/proshooter-api:latest
    container_name: proshooter-api_dev
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      - DATABASE_URL=postgresql://angel:angel@postgres:5432/proshooter_db
      - SECRET_KEY=fasdfjasfsdfkasjdfoiadbasdbasd
    networks:
      - proshooter-network-dev
    restart: always
    command: uvicorn src.main:app --host 0.0.0.0 --port 8000

networks:
  proshooter-network-dev:
    driver: bridge

volumes:
  proshooter_db_data:
```

## Guías Prácticas

### Iniciar el entorno de desarrollo

```bash
# Clonar el repositorio
git clone [URL_DEL_REPOSITORIO]
cd proshooter-api

# Iniciar los contenedores
docker-compose up -d

# Ver logs de la aplicación
docker-compose logs -f api
```

### Actualizar imágenes para compartir

```bash
# Asegúrate de estar logueado en Docker Hub
docker login

# Ejecutar el script de actualización
./update-images.sh
```

### Instrucciones para otros desarrolladores

1. Crear una carpeta para el proyecto
2. Guardar el archivo `docker-compose.yaml` proporcionado
3. Ejecutar:
   ```bash
   docker-compose up -d
   ```
4. La API estará disponible en http://localhost:8000
5. La documentación de la API estará en http://localhost:8000/docs

### Actualizar a la última versión (para otros desarrolladores)

```bash
# Descargar las últimas imágenes
docker-compose pull

# Reiniciar los contenedores
docker-compose up -d
```

### Reiniciar con datos frescos (para otros desarrolladores)

Si quieren asegurarse de tener los datos más recientes de la imagen:

```bash
# Detener contenedores y eliminar volúmenes
docker-compose down -v

# Iniciar con datos frescos de la imagen
docker-compose up -d
```

## Solución de problemas comunes

### La API no se inicia

Verifica los logs:
```bash
docker-compose logs api
```

Posibles soluciones:
- Asegúrate de que la base de datos esté funcionando
- Verifica que el comando de inicio de la API sea el correcto

### Base de datos sin datos

Si la base de datos no contiene los datos esperados:
```bash
# Verificar si hay tablas en la base de datos
docker-compose exec postgres psql -U angel -d proshooter_db -c "\dt"
```

Posibles soluciones:
- Elimina el volumen y reinicia: `docker-compose down -v && docker-compose up -d`
- Verifica que la imagen de PostgreSQL se creó correctamente con los datos

### Errores al construir imágenes

Si hay errores al construir las imágenes, verifica:
- Que el archivo `requirements.txt` exista y sea accesible
- Que tengas permisos para escribir en el directorio actual
- Que estés ejecutando los comandos desde el directorio raíz del proyecto

### La API no puede conectarse a la base de datos

Verifica:
- Que los nombres de los servicios coincidan con los utilizados en la URL de conexión
- Que las credenciales sean correctas
- Que el servicio de base de datos esté en el mismo network que la API
