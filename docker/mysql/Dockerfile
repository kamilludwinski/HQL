# Build from repo root: docker build -f docker/mysql/Dockerfile .
FROM mysql:8

ENV MYSQL_ROOT_PASSWORD=humanql
ENV MYSQL_DATABASE=humanql
ENV MYSQL_USER=humanql
ENV MYSQL_PASSWORD=humanql

COPY sql/mysql.sql /docker-entrypoint-initdb.d/schema.sql
