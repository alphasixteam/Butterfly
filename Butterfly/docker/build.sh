#!/bin/bash

# Costruzione delle immagini
# docker build --no-cache --tag producer_redmine -f ../Butterfly/producer/redmine/Dockerfile . ;
# docker build --no-cache --tag producer_gitlab -f ../Butterfly/producer/gitlab/Dockerfile . ;
# docker build --no-cache --tag consumer_telegram -f ../Butterfly/consumer/telegram/Dockerfile . ;
# docker build --no-cache --tag consumer_email -f ../Butterfly/consumer/email/Dockerfile . ;
# docker build --no-cache --tag gestore_personale -f ../Butterfly/gestore-personale/DockerfileConsumer/Dockerfile . ;
# docker build --no-cache --tag gestore_personale_client -f ../Butterfly/gestore-personale/DockerfileClient/Dockerfile . ;

#
# docker-compose -f ../Butterfly/docker/gitlab.yml up -d ;
# docker-compose -f ../Butterfly/docker/kafka.yml up -d ;
# docker-compose -f ../Butterfly/docker/redmine.yml up -d ;
# docker-compose -f ../Butterfly/docker/jenkins.yml up -d ;

# sleep 1m ;

cd docker ;

# 
docker-compose -f producer-gitlab.yml up -d ;
docker-compose -f producer-redmine.yml up -d ;

# 
docker-compose -f consumer-email.yml up -d ;
docker-compose -f consumer-telegram.yml up -d ;

#
docker-compose -f gestore-personale.yml up -d ;
docker-compose -f gestore-personale-client.yml up -d ;