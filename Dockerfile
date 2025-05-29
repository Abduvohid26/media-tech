# FROM python:3.12.4

# WORKDIR /home

# COPY requirements.txt .

# RUN pip install -r requirements.txt

# RUN apt-get update && apt-get install -y gettext

# RUN msgfmt /locales/uz/LC_MESSAGES/base.po -o /locales/uz/LC_MESSAGES/base.mo && \
#     msgfmt /locales/ru/LC_MESSAGES/base.po -o /locales/ru/LC_MESSAGES/base.mo && \
#     msgfmt /locales/en/LC_MESSAGES/base.po -o /locales/en/LC_MESSAGES/base.mo


FROM python:3.12.4

WORKDIR /home

ENV PYTHONUNBUFFERED=1


COPY requirements.txt .
RUN pip install -r requirements.txt

RUN apt-get update && apt-get install -y gettext
RUN apt-get update && apt-get install -y ffmpeg


COPY locales/ /home/locales/

RUN msgfmt /home/locales/uz/LC_MESSAGES/base.po -o /home/locales/uz/LC_MESSAGES/base.mo && \
    msgfmt /home/locales/ru/LC_MESSAGES/base.po -o /home/locales/ru/LC_MESSAGES/base.mo && \
    msgfmt /home/locales/en/LC_MESSAGES/base.po -o /home/locales/en/LC_MESSAGES/base.mo
