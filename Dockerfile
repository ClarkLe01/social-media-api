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

# copy entrypoint.sh
COPY . /app/backend/
#COPY ./entrypoint.sh /app/backend/
RUN sed -i 's/\r$//g' /app/backend/entrypoint.sh
RUN chmod +x /app/backend/entrypoint.sh

#COPY ./celery/beat/start.sh /app/backend/celery/beat/
RUN sed -i 's/\r$//g' /app/backend/celery/beat/start.sh
RUN chmod +x /app/backend/celery/beat/start.sh

#COPY ./celery/worker/start.sh /app/backend/celery/worker/
RUN sed -i 's/\r$//g' /app/backend/celery/worker/start.sh
RUN chmod +x /app/backend/celery/worker/start.sh

#COPY ./celery/flower/start.sh /app/backend/celery/flower/
RUN sed -i 's/\r$//g' /app/backend/celery/flower/start.sh
RUN chmod +x /app/backend/celery/flower/start.sh

WORKDIR /app/backend/
