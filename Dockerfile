# Use an official Python runtime based on Debian 10 "buster" as a parent image.
FROM python:3.11-slim-buster

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# apt
RUN apt-get update -y && apt-get upgrade -y && apt-get install -y libmagic-dev gcc \
gettext --fix-missing

# Geospatial libraries
RUN apt-get install -y binutils libproj-dev gdal-bin --fix-missing

RUN apt-get clean && rm -rf /var/lib/apt/lists/* && rm -rf /var/cache/apt

ADD requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt --disable-pip-version-check --no-cache-dir

# Use /app folder as a directory where the source code is stored.
WORKDIR /app

# Copy the source code of the project into the container.
COPY . .
