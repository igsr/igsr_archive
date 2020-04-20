FROM python:3.7-slim-buster

LABEL maintainer="ernestolowy@gmail.com"
LABEL description="Dockerfile used to build the image used in the different IGSR_archive tasks"

# Install packages
RUN apt-get update \
 && apt-get -y --no-install-recommends install build-essential \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*