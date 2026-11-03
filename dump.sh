#!/bin/bash
# chmod +x dump.sh
set -a
source .env
set +a

DATE=$(date +"%Y-%m-%d_%H-%M-%S")
DUMP_FILE="dump_$DATE.sql"

echo "Данные бд"
echo "DB_HOST=[$DB_HOST]"
echo "DB_PORT=[$DB_PORT]"
echo "DB_USER=[$DB_USER]"
echo "DB_NAME=[$DB_NAME]"

echo "🚀 Creating dump..."

mysqldump \
  -h "$DB_HOST" \
  -P "$DB_PORT" \
  -u "$DB_USER" \
  -p"$DB_PASSWORD" \
  --default-character-set=utf8mb4 \
  --single-transaction \
  "$DB_NAME" > "$DUMP_FILE"

echo "✅ Dump created: $DUMP_FILE"