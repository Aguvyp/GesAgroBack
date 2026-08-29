#!/bin/sh
set -eu

cd "$(dirname "$0")"
set -a
. ./.env.server
set +a

backup_dir=/var/backups/gesagro
timestamp=$(date -u +%Y%m%dT%H%M%SZ)
temporary_file="$backup_dir/.gesagro-$timestamp.sql.gz.tmp"
final_file="$backup_dir/gesagro-$timestamp.sql.gz"

install -d -m 700 "$backup_dir"
docker compose --env-file .env.server exec -T database \
  mysqldump -ugesagro -p"$DATABASE_PASSWORD" --single-transaction gesagro \
  | gzip -9 > "$temporary_file"
mv "$temporary_file" "$final_file"
chmod 600 "$final_file"
find "$backup_dir" -type f -name 'gesagro-*.sql.gz' -mtime +7 -delete
