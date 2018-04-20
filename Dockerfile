FROM ubuntu:16.04

RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y -q --allow-unauthenticated \
    build-essential \
    make \
    gcc \
    zlib1g-dev \
    git \
    python \
    python-dev \
    python-pip \
    python3-dev \
    python3-pip \
    gnupg \
    sudo \
    gunicorn \
    language-pack-en

# RUN useradd -ms /bin/bash www
# USER www
# WORKDIR /home/www
RUN mkdir /www
RUN mkdir /data
RUN mkdir /data/DB
WORKDIR /www
COPY . .

# USER root
# RUN chown -R www:www /home/www
RUN pip3 install --upgrade pip
RUN pip3 install -r ./requirements.txt
# ENV LANGUAGE en_US.UTF-8
# ENV LANG en_US.UTF-8
# ENV LC_ALL en_US.UTF-8

# RUN locale-gen en_US.UTF-8
# RUN dpkg-reconfigure locales

EXPOSE 8000

RUN /bin/bash
# CMD [ "setsid", "npm", "start", ">","frontend.log"]
# CMD [ "gunicorn", "--reload", "mlapi.app"]
