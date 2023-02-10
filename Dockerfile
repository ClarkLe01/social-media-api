# pull official base image
FROM python:3.9.6-alpine

# set work directory
WORKDIR /backend

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt backend/
RUN pip install -r ./requirements.txt

# copy entrypoint.sh
COPY ./entrypoint.sh /backend/
RUN sed -i 's/\r$//g' /backend/entrypoint.sh
RUN chmod +x /backend/entrypoint.sh

# copy project
COPY . /backend/
WORKDIR /backend/