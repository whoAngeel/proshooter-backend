#!/bin/bash
# update-images.sh

# Colores para salida
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Actualizando imágenes de Pro Shooter API...${NC}"

# Parámetros
DOCKER_USERNAME="tuusuario"  # Reemplaza con tu nombre de usuario
VERSION=$(date +"%Y%m%d.%H%M")  # Versión basada en fecha y hora
UPDATE_DB=false

# Procesar argumentos
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --with-db) UPDATE_DB=true ;;
        --username) DOCKER_USERNAME="$2"; shift ;;
        *) echo "Argumento desconocido: $1"; exit 1 ;;
    esac
    shift
done

# Verificar si los contenedores están en ejecución
if ! docker-compose ps | grep -q "api"; then
    echo "Los contenedores no están en ejecución. Iniciando..."
    docker-compose up -d
    sleep 5
fi

# Actualización de la base de datos si se especifica
if $UPDATE_DB; then
    echo -e "${YELLOW}Actualizando la base de datos...${NC}"

    # Aplicar migraciones si existen
    docker-compose exec -T api alembic upgrade head

    echo -e "${YELLOW}Creando backup de la base de datos...${NC}"
    docker-compose exec -T postgres pg_dump -U angel proshooter_db > db_backup.sql

    echo -e "${YELLOW}Construyendo imagen de PostgreSQL...${NC}"
    docker build -t ${DOCKER_USERNAME}/proshooter-postgres:latest -f postgres.Dockerfile .
    docker tag ${DOCKER_USERNAME}/proshooter-postgres:latest ${DOCKER_USERNAME}/proshooter-postgres:${VERSION}
fi

# Construir imagen de la API
echo -e "${YELLOW}Construyendo imagen de la API...${NC}"
docker-compose build api
docker tag $(docker-compose images -q api) ${DOCKER_USERNAME}/proshooter-api:latest
docker tag $(docker-compose images -q api) ${DOCKER_USERNAME}/proshooter-api:${VERSION}

# Subir imágenes
echo -e "${YELLOW}Subiendo imágenes a Docker Hub...${NC}"
docker login

if $UPDATE_DB; then
    docker push ${DOCKER_USERNAME}/proshooter-postgres:latest
    docker push ${DOCKER_USERNAME}/proshooter-postgres:${VERSION}
fi

docker push ${DOCKER_USERNAME}/proshooter-api:latest
docker push ${DOCKER_USERNAME}/proshooter-api:${VERSION}

echo -e "${GREEN}¡Imágenes actualizadas con éxito!${NC}"
echo -e "API: ${DOCKER_USERNAME}/proshooter-api:latest (${VERSION})"
if $UPDATE_DB; then
    echo -e "DB: ${DOCKER_USERNAME}/proshooter-postgres:latest (${VERSION})"
fi
