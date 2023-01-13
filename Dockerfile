# sqlite + spatialite + FastAPI
FROM debian:bullseye AS spatialite_builder

RUN apt update && apt install -y libsqlite3-mod-spatialite && apt clean

FROM python:3.10-alpine

WORKDIR /api

COPY --from=spatialite_builder /usr/lib/x86_64-linux-gnu/mod_spatialite.so.7.1.0 /api/mod_spatialite.so

COPY ./requirements.txt /api/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /api/requirements.txt

COPY . .
