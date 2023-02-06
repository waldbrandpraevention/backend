# sqlite + spatialite + FastAPI
FROM python:3.10-bullseye

RUN apt update

RUN apt install -y sqlite3=3.34.1-3 libsqlite3-dev=3.34.1-3

RUN apt install -y libsqlite3-mod-spatialite=4.3.0a-5

WORKDIR /api

COPY ./requirements.txt /api/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /api/requirements.txt

COPY . .
