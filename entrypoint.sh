#!/bin/sh
# if any of the commands in your code fails for any reason, the entire script fails
set -o errexit
# fail exit if one of your pipe command fails
set -o pipefail
# exits if any of your variables is not set
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
python manage.py migrate
python manage.py loaddata fixtures/users.json --app user.User
python manage.py loaddata fixtures/friends.json --app friend.Friend
python manage.py loaddata fixtures/rooms.json --app chat.RoomChat
python manage.py loaddata fixtures/memberships.json --app chat.Membership
python manage.py loaddata fixtures/filechats.json --app chat.File
python manage.py loaddata fixtures/messages.json --app chat.Message
python manage.py loaddata fixtures/posts.json --app post.Post
python manage.py loaddata fixtures/postimages.json --app post.Image
python manage.py loaddata fixtures/comments.json --app post.PostComment
python manage.py loaddata fixtures/interactions.json --app post.PostInteraction
python manage.py loaddata fixtures/notifications.json --app notification.Notification
python manage.py runserver 0.0.0.0:8000
exec "$@"