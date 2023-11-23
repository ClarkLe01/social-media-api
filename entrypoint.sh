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