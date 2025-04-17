# Primero, crea el backup de la base de datos
docker-compose exec postgres pg_dump -U angel proshooter_db > db_backup.sql

# Crea un Dockerfile para Postgres con datos
cat > postgres.Dockerfile << 'EOF'
FROM postgres:14-alpine
COPY db_backup.sql /docker-entrypoint-initdb.d/
ENV POSTGRES_USER=angel
ENV POSTGRES_PASSWORD=angel
ENV POSTGRES_DB=proshooter_db
EOF

# Construye y etiqueta las imágenes
docker build -t subkey/proshooter-backend:latest -f postgres.Dockerfile .
docker-compose build api
docker tag $(docker-compose images -q api) subkey/proshooter-backend:latest

# Sube las imágenes a Docker Hub
docker login
docker push subkey/proshooter-backend:latest
docker push subkey/proshooter-backend:latest
