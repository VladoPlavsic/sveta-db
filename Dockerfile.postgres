FROM postgres:12.4-alpine

LABEL MAINTAINER groot
ENV LANG ru_RU.utf8
ENV DBNAME pglocations
ENV USERNAME postgres

COPY data/dummy-data/*  /dummy-data/
COPY init.sql /docker-entrypoint-initdb.d/init.sql
