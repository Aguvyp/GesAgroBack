#!/bin/bash
echo "--- 1. Limpiando cambios locales ---"
git reset --hard HEAD
git clean -fd

echo "--- 2. Descargando de GitHub ---"
git fetch origin main
git reset --hard origin/main

echo "--- 3. Permisos y Docker ---"
chmod +x entrypoint.sh
sudo docker compose up --build -d

echo "--- 4. Sincronizando Base de Datos ---"
sudo docker compose exec web python manage.py migrate

echo "--- ¡SISTEMA ACTUALIZADO! ---"
