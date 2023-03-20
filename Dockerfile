# sqlite + spatialite + FastAPI
FROM python:3.10-bullseye

RUN apt update

# sqlite
RUN apt install -y sqlite3=3.34.1-3 libsqlite3-dev=3.34.1-3

# spatialite
RUN apt install -y libsqlite3-mod-spatialite=5.0.1-2

# protobuffer
RUN apt install -y protobuf-compiler=3.12.4-1

# object detection api for tensorflow
RUN git clone --depth 1 https://github.com/tensorflow/models.git

WORKDIR /models/research

RUN protoc object_detection/protos/*.proto --python_out=. 

RUN cp object_detection/packages/tf2/setup.py . 

RUN python -m pip install --no-cache-dir --upgrade pip 

# Mac problems https://github.com/tensorflow/models/issues/10499
RUN python -m pip install --no-cache-dir --upgrade  --no-deps .

RUN rm -rf /models

# fastapi
WORKDIR /api

COPY ./requirements.txt /api/requirements.txt

# maybe fix https://github.com/waldbrandpraevention/backend/actions/runs/4471759683/jobs/7857051725 ?
RUN python3 -m pip install --upgrade pip setuptools wheel

RUN pip install --no-cache-dir --upgrade -r /api/requirements.txt

COPY . .
