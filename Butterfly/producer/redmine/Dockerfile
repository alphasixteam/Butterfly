# File: Dockerfile
# Data creazione: 2019-02-19

# <descrizione>

# Licenza: Apache 2.0

# Copyright 2019 AlphaSix

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Versione: 0.2.0
# Creatore: Ciprian Voinea

# Base image
FROM python:alpine3.7

# Copying files from the correct folders
COPY /producer/redmine/__init__.py ./Butterfly/producer/redmine/
COPY /producer/redmine/producer.py ./Butterfly/producer/redmine/
COPY /producer/redmine/requirements.txt ./Butterfly/producer/redmine/
COPY /producer/redmine/run.py ./Butterfly/producer/redmine/

COPY /producer/creator.py ./Butterfly/producer/
COPY /producer/__init__.py ./Butterfly/producer/
COPY /producer/producer.py ./Butterfly/producer/
COPY /producer/server.py ./Butterfly/producer/

COPY /webhook/redmine/factory.py ./Butterfly/webhook/redmine/
COPY /webhook/redmine/__init__.py ./Butterfly/webhook/redmine/
COPY /webhook/redmine/issue_webhook.py ./Butterfly/webhook/redmine/

COPY /webhook/factory.py ./Butterfly/webhook/
COPY /webhook/__init__.py ./Butterfly/webhook/
COPY /webhook/webhook.json ./Butterfly/webhook/
COPY /webhook/webhook.py ./Butterfly/webhook/
COPY topics.json ./Butterfly/

# Change current directory
WORKDIR /Butterfly

ENV KAFKA_IP='10.42.0.142'
ENV KAFKA_PORT=9092

RUN mkdir ./config
VOLUME ./config

# Installing dependencies
RUN pip3 install --upgrade pip ; pip3 install -r producer/redmine/requirements.txt

# Run after the dependencies have been installed
CMD python3 -m producer.redmine.run
