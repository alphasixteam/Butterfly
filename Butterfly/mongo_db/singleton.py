"""
File: singleton.py
Data creazione: 2019-03-15

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

Versione: 0.1.0
Creatore: Matteo Marchiori, matteo.marchiori@gmail.com
Autori:
    Timoty Granziero, timoty.granziero@gmail.com
"""

from pathlib import Path
import pymongo
import json
import os

_CONFIG_PATH = Path(__file__).parents[0] / 'config.json'


def _open_configs(path: Path):
    with open(path) as file:
        config = json.load(file)['mongo']
    if(os.environ['MONGO_IP']):
        config['ip'] = os.environ['MONGO_IP']
    return config


class MongoSingleton:

    class Singleton:

        def __init__(
                self,
                db: str,
                mongo_client
        ):
            self._client = mongo_client
            self._db = self._client[db]

        def create(
                self, document: dict, collection: str,
        ) -> pymongo.collection.InsertOneResult:
            """Aggiunge il documento `document` alla collezione
            `collection`, se non è già presente. Restituisce un
            `InsertOneResult`.
            """
            return self._db[collection].insert_one(document)

        def read(
                self, collection_name: str
        ) -> pymongo.collection.Collection:
            """Restituisce la collezione con il nome passato come
            argomento."""
            return self._db[collection_name]

        def delete(
                self, mongofilter: dict, collection: str
        ) -> pymongo.collection.DeleteResult:
            """Rimuove un documento che corrisponde al
            `filter`, se presente, e restituisce il risultato.
            Restituisce un `DeleteResult`.
            """
            # return self._db[collection].delete_one({'_id':ObjectId('')})
            return self._db[collection].delete_one(mongofilter)

        def drop(
                self
        ):
            """Rimuove il database specificato nelle configurazioni
            dell'oggetto.
            """
            configs = _open_configs(_CONFIG_PATH)
            self._client.drop(configs['database'])

    configs = _open_configs(_CONFIG_PATH)
    _INSTANCE = Singleton(
        configs['database'],
        pymongo.MongoClient(configs['ip'], configs['port'])
    )

    @staticmethod
    def instance():
        return MongoSingleton._INSTANCE
