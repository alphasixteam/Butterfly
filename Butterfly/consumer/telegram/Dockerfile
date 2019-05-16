# File: Dockerfile
# Data creazione: 2019-02-15

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

# Port exposure
EXPOSE 5000

# Copying files from the correct folders
COPY /consumer/telegram/config.json ./Butterfly/consumer/telegram/
COPY /consumer/telegram/consumer.py ./Butterfly/consumer/telegram/
COPY /consumer/telegram/requirements.txt ./Butterfly/consumer/telegram/
COPY /consumer/telegram/__init__.py ./Butterfly/consumer/telegram/
COPY /consumer/telegram/run.py ./Butterfly/consumer/telegram/
COPY /consumer/consumer.py ./Butterfly/consumer/
COPY /consumer/creator.py ./Butterfly/consumer/
COPY /consumer/__init__.py ./Butterfly/consumer/
COPY topics.json ./Butterfly/
 
# Change current directory
WORKDIR /Butterfly

ENV KAFKA_IP='10.42.0.142'
ENV KAFKA_PORT=9092

RUN mkdir ./config
VOLUME ./config

# Installing dependencies
RUN pip3 install --upgrade pip ; pip3 install -r consumer/telegram/requirements.txt

# Run after the dependencies have been installed
CMD python3 -m consumer.telegram.run
