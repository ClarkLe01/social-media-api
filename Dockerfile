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

COPY ./entrypoint.prod.sh .
RUN sed -i 's/\r$//g' /app/backend/entrypoint.prod.sh
RUN chmod +x /app/backend/entrypoint.prod.sh

RUN sed -i 's/\r$//g' /app/backend/beat.sh
RUN chmod +x /app/backend/beat.sh

RUN sed -i 's/\r$//g' /app/backend/worker.sh
RUN chmod +x /app/backend/worker.sh

RUN sed -i 's/\r$//g' /app/backend/flower.sh
RUN chmod +x /app/backend/flower.sh


WORKDIR /app/backend/
RUN pip install debugpy -t /tmp
