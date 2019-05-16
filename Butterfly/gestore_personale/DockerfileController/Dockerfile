# File: Dockerfile
# Data creazione: 2019-05-03

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

# Versione: 0.1.0
# Creatore: Laura Cameran

# Base image
FROM python:alpine3.7

# Port exposure
EXPOSE 5000

# Copying files from the correct folders
COPY /gestore_personale/static/html/access.html ./Butterfly/gestore_personale/static/html/
COPY /gestore_personale/static/html/adduser.html ./Butterfly/gestore_personale/static/html/
COPY /gestore_personale/static/html/adminpanel.html ./Butterfly/gestore_personale/static/html/
COPY /gestore_personale/static/html/modifyuser.html ./Butterfly/gestore_personale/static/html/
COPY /gestore_personale/static/html/panel.html ./Butterfly/gestore_personale/static/html/
COPY /gestore_personale/static/html/preference.html ./Butterfly/gestore_personale/static/html/
COPY /gestore_personale/static/html/removeuser.html ./Butterfly/gestore_personale/static/html/
COPY /gestore_personale/static/html/showuser.html ./Butterfly/gestore_personale/static/html/
COPY /gestore_personale/static/html/showproject.html ./Butterfly/gestore_personale/static/html/
COPY /gestore_personale/static/html/removeproject.html ./Butterfly/gestore_personale/static/html/

COPY /gestore_personale/static/image/a6.png ./Butterfly/gestore_personale/static/image/
COPY /gestore_personale/static/image/b.png ./Butterfly/gestore_personale/static/image/
COPY /gestore_personale/static/image/favicon.ico ./Butterfly/gestore_personale/static/image/

COPY /gestore_personale/static/script/script.js  ./Butterfly/gestore_personale/static/script/

COPY /gestore_personale/static/style/style.css ./Butterfly/gestore_personale/static/style/

COPY /gestore_personale/observer.py ./Butterfly/gestore_personale/
COPY /gestore_personale/api.py ./Butterfly/gestore_personale/
COPY /gestore_personale/web.py ./Butterfly/gestore_personale/
COPY /gestore_personale/controller.py ./Butterfly/gestore_personale/

COPY /gestore_personale/requirements.txt ./Butterfly/gestore_personale/

COPY /mongo_db/facade.py ./Butterfly/mongo_db/
COPY /mongo_db/users.py ./Butterfly/mongo_db/
COPY /mongo_db/projects.py ./Butterfly/mongo_db/
COPY /mongo_db/singleton.py ./Butterfly/mongo_db/
COPY /mongo_db/db.json ./Butterfly/mongo_db/
COPY /mongo_db/config.json ./Butterfly/mongo_db/
COPY /mongo_db/populate.py ./Butterfly/mongo_db/
COPY /mongo_db/__init__.py ./Butterfly/mongo_db/
COPY /mongo_db/db_connection.py ./Butterfly/mongo_db/
COPY /mongo_db/db_controller.py ./Butterfly/mongo_db/

COPY topics.json ./Butterfly/

# Change current directory
WORKDIR /Butterfly

ENV MONGO_IP='10.42.0.194'

RUN mkdir ./config
VOLUME ./config

# Installing dependencies
RUN pip3 install --upgrade pip ; pip3 install -r gestore_personale/requirements.txt

# Run after the dependencies have been installed
CMD python3 -m gestore_personale.controller
