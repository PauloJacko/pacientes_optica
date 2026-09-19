#!/usr/bin/env bash

# Detener el script inmediatamente si ocurre algún error
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate

# Ejecuta tu comando personalizado
python manage.py create_initial_superuser