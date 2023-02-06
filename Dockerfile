# sqlite + spatialite + FastAPI
FROM python:3.10-bullseye

RUN apk add --no-cache sqlite

RUN apk add --no-cache libspatialite=5.0.1-r5

WORKDIR /api

COPY ./requirements.txt /api/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /api/requirements.txt

COPY . .
