FROM python:3.9-alpine3.13

WORKDIR /app
ARG SCORD_VERSION=0.2.0

COPY tests/ ./tests

RUN pip install shellcord==$SCORD_VERSION


RUN shellcord -h
RUN shellcord --log-file ./tests/scord_logs/scord-log-normal.json generate
RUN cat ./scord-runbook-*

ENV LAST_SCORD_ID 12345
RUN shellcord --log-file ./tests/scord_logs/scord-log-normal.json tag previous "foo bar"

RUN pip index versions shellcord
