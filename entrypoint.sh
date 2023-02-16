#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi
python manage.py makemigrations
python manage.py flush --no-input
python manage.py migrate
python manage.py loaddata fixtures/users.json --app user.User
python manage.py runserver 0.0.0.0:8000
exec "$@"