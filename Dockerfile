# sqlite
FROM alpine:latest

RUN apk add --no-cache -y sqlite3

# FastAPI
FROM python:3.9

WORKDIR /api

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . .
