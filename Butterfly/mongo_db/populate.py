"""
File: populate.py
Data creazione: 2019-02-19

<descrizione>

Licenza: Apache 2.0

Copyright 2019 AlphaSix

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Versione: 0.2.0
Creatore: Timoty Granziero, timoty.granziero@gmail.com
"""

import json
import datetime
from pprint import pprint
import pymongo
from pathlib import Path
import os

from mongo_db.db_connection import DBConnection
from mongo_db.db_controller import DBController

_CONFIG_PATH = Path(__file__).parents[0] / 'config.json'

def _open_configs(path: Path):
    with open(path) as file:
        config = json.load(file)['mongo']
    if(os.environ['MONGO_IP']):
            config['ip'] = os.environ['MONGO_IP']
    return config

def populateA():
    with DBConnection(_open_configs(_CONFIG_PATH)['database']) as client:

        client.drop_collections('users', 'projects', 'topics')

        controller = DBController(client)
        db = client.db
        with open(Path(__file__).parent / 'db.json') as f:
            data = json.load(f)

        users_json = data['users']
        projects_json = data['projects']
        topics_json = data['topics']

        # Popola la collezione users da db.json
        for user in users_json:
            # NON usare questo metodo per inserire utenti! Usare
            # controller.insert_user()
            result = controller.collection('users').insert_one(user)

        # Popola la collezione projects da db.json
        for project in projects_json:
            result = controller.insert_project(project)

        # Popola la collezione topics da db.json
        for topic in topics_json:
            result = controller.insert_topic(
                # topic['_id'],
                topic['label'],
                topic['project'],
            )

def populateB():
    configs = _open_configs(_CONFIG_PATH)
    client = pymongo.MongoClient(configs['ip'], configs['port'])
    client.drop_database(configs['database'])

    db = client.butterfly

    with open(Path(__file__).parent / 'db.json') as f:
        data = json.load(f)

    projects_json = data['projects']
    users_json = data['users']

    users = db.users
    for user in users_json:
        # Converte stringa YYYY-MM-DD in formato ISO usato da MongoDB
        if 'irreperibilita' in user:
            dates = []
            for irr in user['irreperibilita']:
                irr = irr.split('-')
                dates.append(datetime.datetime(
                    int(irr[0]),
                    int(irr[1]),
                    int(irr[2]),
                ))
            user['irreperibilita'] = dates
        result = users.insert_one(user)

    projects = db.projects
    for project in projects_json:
        result = projects.insert_one(project)


populateB()
