"""
File: db_connection.py
Data creazione: 2019-02-20
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
Versione: 0.1.1
Creatore: Timoty Granziero, timoty.granziero@gmail.com
"""

from pathlib import Path
import pymongo, json, os

_CONFIG_PATH = Path(__file__).parents[0] / 'config.json'

def _open_configs(path: Path):
    with open(path) as file:
        config = json.load(file)['mongo']
    if(os.environ['MONGO_IP']):
            config['ip'] = os.environ['MONGO_IP']
    return config

class DBConnection(object):
    """Classe con la funzionalità di connessione e sconnessione
    a un database. Dovrebbe essere usata in un costrutto with,
    in modo da automatizzare il rilascio della risorsa.
    e.g.:
    with DBConnection('nomedb'):
        # ...
    Arguments:
        db -- Nome del database a cui connettersi
        server -- server mongo a cui connettersi
        port -- porta specifica in cui gira il processo mongod
    """
    def __init__(
        self,
        db: str,
        server=_open_configs(_CONFIG_PATH)['ip'],
        port=_open_configs(_CONFIG_PATH)['port']
    ):
        configs = _open_configs(_CONFIG_PATH)
        self._client = pymongo.MongoClient(configs['ip'], configs['port'])
        self._db = self._client[db]

    # Entrata nel costrutto with
    def __enter__(self):
        return self

    # Uscita dal costrutto with
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def drop_collections(self, *collections):
        """Elimina le collezioni passate come argomenti,
        solo se presenti.
        """
        for collection in collections:
            if collection in self.db.list_collection_names():
                self.db.drop_collection(collection)

    @property
    def db(self):
        return self._db

    def close(self):
        """Chiude la connessione col client mongo.
        """
        self._client.close()
