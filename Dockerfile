# sqlite + spatialite + FastAPI
FROM python:3.10-alpine

RUN apk add --no-cache sqlite

RUN apk add --no-cache libspatialite

WORKDIR /api

COPY ./requirements.txt /api/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /api/requirements.txt

COPY . .
