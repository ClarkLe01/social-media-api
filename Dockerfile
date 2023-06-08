# pull official base image
FROM python:3.9.6-alpine

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . /app/backend/
RUN sed -i 's/\r$//g' /app/backend/entrypoint.sh
RUN chmod +x /app/backend/entrypoint.sh

RUN sed -i 's/\r$//g' /app/backend/celery/beat/start-beat.sh
RUN chmod +x /app/backend/celery/beat/start-beat.sh

RUN sed -i 's/\r$//g' /app/backend/celery/worker/start-worker.sh
RUN chmod +x /app/backend/celery/worker/start-worker.sh

RUN sed -i 's/\r$//g' /app/backend/celery/flower/start-flower.sh
RUN chmod +x /app/backend/celery/flower/start-flower.sh

WORKDIR /app/backend/
