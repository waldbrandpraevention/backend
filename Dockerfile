# sqlite
FROM alpine:latest

RUN apk add --no-cache sqlite

# FastAPI
FROM python:3.10-alpine

WORKDIR /api

COPY ./requirements.txt /api/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /api/requirements.txt

COPY . .
