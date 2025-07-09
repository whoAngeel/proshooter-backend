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
