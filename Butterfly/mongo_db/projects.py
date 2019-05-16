"""
File: projects.py
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

import copy

import pymongo

from mongo_db.singleton import MongoSingleton

apps = [
    'gitlab',
    'redmine',
]


class MongoProjects:

    def __init__(self, mongo: MongoSingleton):
        self._mongo = mongo

    def projects(self, mongofilter={}):
        """Restituisce un `Cursor` che corrisponde al `filter` passato
        alla collezione `projects`.
        Per accedere agli elementi del cursore, è possibile iterare con
        un `for .. in ..`, oppure usare il subscripting `[i]`.
        """
        return self.collection.find(mongofilter)

    def exists(self, project: str) -> bool:
        """Restituisce `True` se l'`id` di un utente
        (che può essere Telegram o Email) è salvato nel DB.
        """
        count = self.collection.count_documents({
            'url': project
        })
        return count != 0

    @property
    def collection(self):
        return self._mongo.read('projects')

    def create(
        self,
        **fields,
    ) -> pymongo.results.InsertOneResult:
        """Aggiunge il documento `project` alla collezione `projects`,
        se non già presente, e restituisce il risultato, che può essere
        `None` in caso di chiave duplicata.

        Raises:
        `pymongo.errors.DuplicateKeyError`
        """

        # Valori di default dei campi
        defaultfields = {
            '_id': None,
            'url': None,
            'name': None,
            'app': None,
            'topics': [],
        }

        # Copia profonda del dict default
        new_project = copy.copy(defaultfields)

        # Aggiorna i valori di default con quelli passati al costruttore
        for key in new_project:
            if key in fields:
                new_project[key] = fields.pop(key)

        assert not fields, 'Sono stati inseriti campi non validi'
        assert new_project['url'] is not None, \
            'inserire il campo `url`'
        assert new_project['app'] is not None, \
            'inserire il campo `app`'
        assert new_project['app'] in apps, '`app` non riconosciuta'

        # L'ultimo carattere non deve essere '/'
        if new_project['url'][-1:] == '/':
            new_project['url'] = new_project['url'][:-1]

        assert not self.exists(new_project['url'])

        # Via libera all'aggiunta al DB
        if new_project['_id'] is None:  # Per non mettere _id = None sul DB
            del new_project['_id']

        return self._mongo.create(
            new_project,
            'projects'
        )

    def delete(
        self, url: str
    ) -> pymongo.results.DeleteResult:
        """Rimuove un documento che corrisponda a `url` o `_id` del progetto,
        se presente, e restituisce il risultato.
        """
        return self._mongo.delete({
            'url': url
        },
            'projects'
        )

    def read(
        self, project: str
    ) -> dict:
        """Restituisce il progetto corrispondente a `project`.

        Raises:
        `AssertionError` -- se `project` non è presente nel DB.
        """
        assert self.exists(project), f'Project {project} inesistente'

        return self.projects({
            'url': project
        }).next()

    def update_app(self, project: str, app: str) -> dict:
        """Aggiorna il campo `app` del progetto corrispondente a
        `project` con il valore `app`.
        """
        assert self.exists(project), f'Project {project} inesistente'
        assert app in apps, f'app "{app}" non riconosciuta'

        return self.collection.find_one_and_update(
            {
                'url': project
            },
            {
                '$set': {
                    'app': app,
                }
            }
        )

    def update_url(self, project: str, new_url: str) -> dict:
        """Aggiorna il campo `url` del progetto corrispondente a
        `project` con il valore `new_url`.
        """
        assert self.exists(project), f'Project {project} inesistente'
        assert not self.exists(new_url), f'Project "{new_url}" già esistente'

        return self.collection.find_one_and_update(
            {
                'url': project
            },
            {
                '$set': {
                    'url': new_url,
                }
            }
        )

    def update_name(self, project: str, new_name: str) -> dict:
        """Aggiorna il campo `name` del progetto corrispondente a
        `project` con il valore `new_name`.
        """
        assert self.exists(project), f'Project {project} inesistente'

        return self.collection.find_one_and_update(
            {
                'url': project
            },
            {
                '$set': {
                    'name': new_name,
                }
            }
        )

    # def keywords(self, project: str) -> list:
    #     """Restituisce una lista contenente le parole chiave corrispondenti
    #     all'`id`: url del progetto
    #     """
    #     cursor = self.projects(
    #         {'url': project}
    #     )
    #     return cursor[0]['keywords']

    def topics(self, project: str) -> list:
        """Restituisce una lista contenente i topics corrispondenti
        a '`project`: `url` o `_id` del progetto
        """
        assert self.exists(project), f'Project {project} inesistente'

        cursor = self.projects(
            {
                'url': project
            }
        )
        try:
            return cursor.next()['topics']
        except StopIteration:
            return []

    # def insert_keyword_by_project(self, keyword: str, project: str):
    #     """Inserisce una nuova keyword nel progetto
    #     """
    #     keywords = self.keywords(project)
    #     keywords.append(keyword)
    #     self._mongo.db['projects'].update(
    #         {'url': project},
    #         {
    #             '$set':
    #             {'keywords': keywords}
    #         }
    #     )

    def add_topics(self, project: str, *topics: str):
        """Inserisce nuovi `topics` nel progetto `project`.
        """
        assert self.exists(project), f'Project {project} inesistente'

        return self.collection.find_one_and_update(
            {'url': project},
            {
                '$addToSet': {
                    'topics': {
                        '$each': topics,
                    }
                }
            }
        )

    def remove_topics(self, project: str, *topics: str):
        """Rimuove i `topics` dal progetto `project`.
        """
        assert self.exists(project), f'Project {project} inesistente'

        return self.collection.find_one_and_update(
            {
                'url': project
            },
            {
                '$pull': {
                    'topics': {
                        '$in': topics,
                    }
                }
            }
        )
