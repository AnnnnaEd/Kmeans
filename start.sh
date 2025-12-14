#!/usr/bin/env bash

# 1. Ejecutar las migraciones (aunque no uses base de datos, es buena práctica)
python manage.py migrate

# 2. Recolectar archivos estáticos (CSS, JS, etc.)
python manage.py collectstatic --noinput

# 3. Iniciar el servidor Gunicorn (necesario para producción)
# Render necesita un servidor WSGI como Gunicorn. Necesitas instalarlo:
# pip install gunicorn
gunicorn kmeans_project.wsgi:application