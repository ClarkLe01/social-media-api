#!/bin/bash

set -o errexit
set -o nounset

postgres_ready() {
python << END
import sys

import psycopg2

try:
    psycopg2.connect(
        dbname="${POSTGRES_DB}",
        user="${POSTGRES_USER}",
        password="${POSTGRES_PASSWORD}",
        host="${DB_HOST}",
        port="${DB_PORT}",
    )
except psycopg2.OperationalError:
    sys.exit(-1)
sys.exit(0)

END
}
until postgres_ready; do
    >&2 echo 'Waiting for PostgreSQL to become available...'
    sleep 1
done
>&2 echo 'PostgreSQL is available'
python manage.py collectstatic --no-input
python manage.py migrate
daphne -b 0.0.0.0 -p 8000 core.asgi:application
exec "$@"
