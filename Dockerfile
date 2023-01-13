# sqlite + spatialite + FastAPI
FROM python:3.10-alpine

RUN apk add --no-cache sqlite

RUN apk add --no-cache libspatialite

WORKDIR /api

COPY --from=spatialite_builder /usr/lib/x86_64-linux-gnu/mod_spatialite.so.7.1.0 /api/mod_spatialite.so

COPY ./requirements.txt /api/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /api/requirements.txt

COPY . .
