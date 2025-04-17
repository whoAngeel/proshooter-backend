# Archivo: postgres.Dockerfile
FROM postgres:14-alpine

# Copiar el script de respaldo
COPY proshooter_db_backup.sql /docker-entrypoint-initdb.d/

# Variables de entorno (también se pueden configurar en docker-compose)
ENV POSTGRES_USER=angel
ENV POSTGRES_PASSWORD=angel
ENV POSTGRES_DB=proshooter_db
