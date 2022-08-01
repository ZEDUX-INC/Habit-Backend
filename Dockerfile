FROM python:3.10.4

ENV PYTHONUNBUFFERED 1
RUN mkdir /backend
COPY . /backend/
COPY ./requirements.txt /requirements.txt

RUN pip install --upgrade pip
RUN pip install -r /requirements.txt

WORKDIR /backend
