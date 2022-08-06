FROM debian:stable-slim

RUN apt-get update
RUN apt-get install -y python3-pip
RUN apt-get install -y python3-gi
RUN apt-get install -y python3-gdbm

RUN pip install hid
