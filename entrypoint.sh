#!/bin/sh

# Esperar a que la base de datos esté lista (opcional, pero recomendado)
# Se podría usar wait-for-it o similar, pero por ahora confiaremos en el restart policy o sleep simple si es necesario.

echo "Aplicando migraciones..."
python manage.py migrate

echo "Iniciando servidor..."
exec "$@"
