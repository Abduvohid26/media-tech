FROM python:3.12.4

WORKDIR /home

COPY requirements.txt .

RUN pip install -r requirements.txt
