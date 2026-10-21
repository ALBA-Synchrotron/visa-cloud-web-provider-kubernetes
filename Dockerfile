FROM ubuntu:latest
LABEL authors="rcabezas"

ENTRYPOINT ["top", "-b"]