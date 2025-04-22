#!/bin/bash
set -e

# Esperar a que PostgreSQL esté completamente iniciado
until pg_isready -U "$POSTGRES_USER" -h localhost; do
  echo "Esperando a que PostgreSQL esté disponible..."
  sleep 1
done

# Restaurar la base de datos
pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v /tmp/proshooter_backup.dump

echo "Base de datos restaurada correctamente"
