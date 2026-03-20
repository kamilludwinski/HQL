#!/usr/bin/env bash
# Build and start the MySQL Docker container (humanql database with sample data).
set -e
cd "$(dirname "$0")/.."

IMAGE_NAME="${IMAGE_NAME:-humanql-mysql}"
CONTAINER_NAME="${CONTAINER_NAME:-humanql-mysql}"
PORT="${PORT:-3306}"

docker build -f docker/mysql/Dockerfile -t "$IMAGE_NAME" .

if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
  docker rm -f "$CONTAINER_NAME" 2>/dev/null || true
fi

docker run -d -p "${PORT}:3306" --name "$CONTAINER_NAME" "$IMAGE_NAME"

echo "MySQL container '$CONTAINER_NAME' started on port $PORT."
echo "Connect with: mysql://humanql:humanql@127.0.0.1:${PORT}/humanql"
echo "Example: ./run.sh --db mysql://humanql:humanql@127.0.0.1:${PORT}/humanql list all tables"
