# pull official base image
FROM python:3.9.6-alpine

# set work directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /app/backend/
RUN pip install -r ./backend/requirements.txt

# copy entrypoint.sh
COPY ./entrypoint.sh /app/backend/
RUN sed -i 's/\r$//g' /app/backend/entrypoint.sh
RUN chmod +x /app/backend/entrypoint.sh

# copy project
COPY . /app/backend/
WORKDIR /app/backend/
EXPOSE 8000
CMD ['python', 'manage.py', 'runserver', '0.0.0.0:8000']