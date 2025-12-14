#!/usr/bin/env bash

# 1. Ejecutar las migraciones
python manage.py migrate

# 2. Recolectar archivos estáticos
python manage.py collectstatic --noinput

# 3. Iniciar el servidor Gunicorn
# Usamos un timeout largo (300 segundos) para manejar la subida del dataset grande.
gunicorn kmeans_project.wsgi:application --bind 0.0.0.0:10000 --timeout 300