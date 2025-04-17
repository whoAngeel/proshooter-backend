FROM postgres:14-alpine
COPY db_backup.sql /docker-entrypoint-initdb.d/
ENV POSTGRES_USER=angel
ENV POSTGRES_PASSWORD=angel
ENV POSTGRES_DB=proshooter_db
