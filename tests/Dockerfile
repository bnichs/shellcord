FROM python:3.9-alpine3.13

WORKDIR /app

COPY tests/ ./tests

RUN pip install shellcord


RUN shellcord -h
RUN shellcord --log-file ./tests/scord_logs/scord-log-normal.json generate
RUN cat ./scord-runbook-*

ENV LAST_SCORD_ID 12345
RUN shellcord --log-file ./tests/scord_logs/scord-log-normal.json tag previous "foo bar"

RUN pip index versions shellcord
