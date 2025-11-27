FROM python:3.10.8-slim
LABEL maintainer="lyubinska"

ENV PYTHONUNBUFFERED 1

WORKDIR train/

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt
COPY . .

RUN adduser \
        --disabled-password \
        --no-create-home \
        django-user