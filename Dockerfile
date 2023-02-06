# sqlite + spatialite + FastAPI
FROM python:3.10-bullseye

RUN apt update

RUN apt install -y sqlite3=3.34.1-3 libsqlite3-dev=3.34.1-3

RUN apt install -y libspatialite7=5.0.1-2

WORKDIR /api

COPY ./requirements.txt /api/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /api/requirements.txt

COPY . .
