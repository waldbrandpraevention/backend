# sqlite + spatialite + FastAPI
FROM python:3.10-bullseye

RUN apt install -y sqlite3

RUN apt install -y libspatialite7

WORKDIR /api

COPY ./requirements.txt /api/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /api/requirements.txt

COPY . .
