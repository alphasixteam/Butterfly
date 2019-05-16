"""
File: db_controller.py
Data creazione: 2019-02-22
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
Versione: 0.3.0
Creatore: Timoty Granziero, timoty.granziero@gmail.com
"""

import pprint
import copy

import pymongo

from mongo_db.db_connection import DBConnection


# Non credo che controller sia il termine adatto
class DBController(object):
    """Classe handler per la gestione delle operazioni con il Database
    di Butterfly.
    """

    def __init__(self, db: DBConnection, indexes=True):
        self._dbConnection = db
        if indexes:
            self.initialize_indexes()

    def initialize_indexes(self):
        """Inizializza gli `index` del DB. In particolare, rende
        _unique_ la coppia `label`-`project` dei `topics` e `url`
        dei `projects`.
        """

        # Rende unique l'url dei progetti
        self.dbConnection.db['projects'].create_index(
            [('url', pymongo.ASCENDING)],
            unique=True,
        )
        # Rende unica la coppia label-project di topics
        self.dbConnection.db['topics'].create_index(
            [('label', pymongo.ASCENDING),
                ('project', pymongo.ASCENDING)],
            unique=True,
        )

    # ----------------------------
    # Inserimento/rimozione user |
    # ----------------------------

    def insert_user(self, **fields) -> pymongo.collection.InsertOneResult:
        """Aggiunge un documento corrispondente ai `fields` passati
        come argomento alla collezione `users` dopo esser stato
        validato. In caso qualcosa non vada bene, viene lanciata
        un'eccezione AssertionError.
        I campi `telegram` e `email` non possono essere
        entrambi `None`.
        `preferenza` non può essere impostata su un campo `None`.
        Restituisce un `InsertOneResult`.
        L'unico campo obbligatorio è uno qualsiasi tra `telegram`
        e `email`.
        Esempio:
```
        result = controller.insert_user(
            name='Esempio',
            surname='Inserimento',
            telegram='@nomeuser',
            email=esempio.email@esempio.com,
            topics=[
                4,
                5
            ],
            keywords=[
                'kw1',
                'kw2',
                'kw3',
            ],
            preferenza='telegram',
            sostituto='telegramID oppure email',
        )
```
        Arguments:
        `_id`
        `name` -- (str)
        `surname` -- (str)
        `telegram` -- (str)
        `email` -- (str)
        `topics` -- (list)
        `keywords` -- (list)
        `preferenza` -- (str)
        `sostituto` -- (str)
        Raises:
        `AssertionError`
        """

        # Collezione di interesse
        users = self.collection('users')

        # Valori di default dei campi
        FIELDS = {
            '_id': None,
            'name': None,
            'surname': None,
            'telegram': None,
            'email': None,
            'preferenza': None,
            'irreperibilità': [],
            'sostituto': None,
            'keywords': [],
            'topics': [],
        }

        new_user = copy.copy(FIELDS)  # Copia profonda del dict FIELDS

        # Aggiorna i valori di default con quelli passati al costruttore
        for key in new_user:
            if key in fields:
                new_user[key] = fields.pop(key)

        # Inutile?
        # fields.pop('_id', True)

        assert not fields, 'Sono stati inseriti campi non validi'

        # Se telegram e email sono entrambi None
        if new_user['telegram'] is None and new_user['email'] is None:
            raise AssertionError(
                'È necessario inserire almeno un valore tra email o telegram'
            )

        # Se telegram è già presente
        # assert not self.controller.user_exists(new_user['telegram']), \
        #     f'Username {new_user["telegram"]} già presente'
        if (new_user['telegram'] is not None and
                users.find_one({'telegram': new_user['telegram']})):
            raise AssertionError(
                f'Username {new_user["telegram"]} già presente'
            )

        # Se email è già presente
        if (new_user['email'] is not None and
                users.find_one({'email': new_user['email']})):
            raise AssertionError(f'Email {new_user["email"]} già presente')

        # Ottiene un id valido
        if new_user['telegram'] is None:
            id = new_user['email']
        else:
            id = new_user['telegram']

        # Via libera all'aggiunta al DB
        if new_user['_id'] is None:  # Per non mettere _id = None sul DB
            partial_result = DBController._user_dict_no_id(new_user)
            result = self._insert_document(
                partial_result,
                'users',
            )

        else:
            partial_result = DBController._user_dict_no_id(new_user)
            partial_result['_id'] = new_user['_id']
            result = self._insert_document(
                partial_result,
                'users',
            )

        # NOTE: Se i dati precedenti sono validi, a questo punto sono
        # già inseriti nel DB. I dati successivi vengono inseriti
        # mano a mano che vengono considerati validi. AssertionError
        # verrà lanciata se qualcosa lo è

        # Valida e aggiunge la preferenza
        if new_user['preferenza'] is not None:
            self.update_user_preference(
                new_user[new_user['preferenza']],
                new_user['preferenza']
            )

        # Valida e aggiunge i topic
        for topic in new_user['topics']:
            self.add_user_topic_from_id(id, topic)

        # Aggiunge le kw
        self.add_keywords(id, *new_user['keywords'])

        # Valida e aggiunge il sostituto
        self.update_user_sostituto(id, new_user['sostituto'])

        return result

    def delete_one_user(self, user: str) -> pymongo.collection.DeleteResult:
        """Rimuove un documento che corrisponde a
        `user`, se presente. `user` può riferirsi sia al contatto
        Telegram che email. Restituisce il risultato dell'operazione.
        """
        return self._delete_one_document(
            {
                '$or': [
                    {'telegram': user},
                    {'email': user},
                ]
            },
            'users',
        )

    # -----------------------------
    # Inserimento/rimozione topic |
    # -----------------------------

    def insert_topic(self, label: str, project: str):
        """Aggiunge il documento `topic`, corrispondente alla coppia
        `label`-`project`, alla collezione `topics` se
        non già presente e restituisce il risultato, che può essere
        `None` in caso di chiave (`label`-`project`) duplicata.
        Raises:
        `pymongo.errors.DuplicateKeyError`
        """
        # L'ultimo carattere dell'url di project non deve essere '/'
        if project[-1:] == '/':
            project = project[:-1]

        try:  # Tenta l'aggiunta del topic al DB
            # Ottiene l'id massimo
            max_id = (
                self.collection('topics')
                    .find()
                    .sort('_id', pymongo.DESCENDING)
                    .limit(1)[0]['_id']
            )

            result = self.dbConnection.db['topics'].insert_one({
                '_id': max_id+1,
                'label': label,
                'project': project,
            })
            return result

        except IndexError:  # Caso in cui nessun topic è presente
            result = self.dbConnection.db['topics'].insert_one({
                '_id': 0,
                'label': label,
                'project': project,
            })
            return result

    def delete_one_topic(
            self,
            label: str,
            project: str,
    ) -> pymongo.collection.DeleteResult:
        """Rimuove un documento che corrisponda alla coppia `label`-`project`,
        se presente, e restituisce il risultato.
        """
        return self._delete_one_document({
            'label': label,
            'project': project,
        },
            'topics',
        )

    # -------------------------------
    # Inserimento/rimozione project |
    # -------------------------------

    def insert_project(self, project: dict):
        """Aggiunge il documento `project` alla collezione `projects`,
        se non già presente, e restituisce il risultato, che può essere
        `None` in caso di chiave duplicata.
        Raises:
        `pymongo.errors.DuplicateKeyError`
        """
        # L'ultimo carattere non deve essere '/'
        if project['url'][-1:] == '/':
            project['url'] = project['url'][:-1]
        # Tenta l'aggiunta del progetto, raises DuplicateKeyError
        result = self.dbConnection.db['projects'].insert_one(project)
        return result

    def delete_one_project(
            self,
            url: str,
    ) -> pymongo.collection.DeleteResult:
        """Rimuove un documento che corrisponda a `url`,
        se presente, e restituisce il risultato.
        """
        return self._delete_one_document({
            'url': url,
        },
            'projects'
        )

    # --------------------------
    # Listing delle collezioni |
    # --------------------------

    def users(self, filter={}) -> pymongo.cursor.Cursor:
        """Restituisce un `Cursor` che corrisponde al `filter` passato
        alla collezione `users`.
        Per accedere agli elementi del cursore, è possibile iterare con
        un `for .. in ..`, oppure usare il subscripting `[i]`.
        """
        return self.collection('users').find(filter)

    def projects(self, filter={}) -> pymongo.cursor.Cursor:
        """Restituisce un `Cursor` che corrisponde al `filter` passato
        alla collezione `projects`.
        Per accedere agli elementi del cursore, è possibile iterare con
        un `for .. in ..`, oppure usare il subscripting `[i]`.
        """
        return self.collection('projects').find(filter)

    def topics(self, filter={}) -> pymongo.cursor.Cursor:
        """Restituisce un `Cursor` che corrisponde al `filter` passato
        alla collezione `topics`.
        Per accedere agli elementi del cursore, è possibile iterare con
        un `for .. in ..`, oppure usare il subscripting `[i]`.
        """
        return self.collection('topics').find(filter)

    # -------------------
    # | Esistenza campi |
    # -------------------

    def user_exists(self, id: str) -> bool:
        """Restituisce `True` se l'`id` di un utente
        (che può essere Telegram o Email) è salvato nel DB.
        """
        count = self.collection('users').count_documents({
            '$or': [
                # {'_id': id},
                {'telegram': id},
                {'email': id},
            ]
        })
        if count == 0:
            return False
        return True

    def project_exists(self, url: str) -> bool:
        """Restituisce `True` se l'url` corrisponde a un `url` di un
        `project` presente nel sistema.
        """
        count = self.collection('projects').count_documents({
            'url': url,
        })
        if count == 0:
            return False
        return True

    def topic_exists(self, label: str, project: str) -> bool:
        """Restituisce `True` se il `topic` corrispondente alla coppia
        `label`-`project` è salvato nel DB.
        """
        count = self.collection('topics').count_documents({
            'label': label,
            'project': project,
        })
        if count == 0:
            return False
        return True

    def topic_from_id_exists(self, id: int) -> bool:
        """Restituisce `True` se il `topic` corrispondente all'`id` è
        salvato nel DB.
        """
        count = self.collection('topics').count_documents({
            '_id': id,
        })
        if count == 0:
            return False
        return True

    # --------------------
    # | Update user data |
    # --------------------

    def update_user_preference(self, id: str, preference: str):
        """Aggiorna la preferenza (tra Telegram e Email) dell'utente
        corrispondente all'`id` (Telegram o Email).
        Raises:
        `AssertionError` -- se preference non è `telegram` o `email`
            oppure se `id` non è presente nel DB.
        """

        # Controllo validità campo preference
        assert preference.lower() in ('telegram', 'email'), \
            f'Selezione {preference} non valida: scegli tra Telegram o Email'

        # Controllo esistenza id user
        assert self.user_exists(id), f'User {id} inesistente'

        count = self.collection('users').count_documents({
            '$or': [  # Confronta id sia con telegram che con email
                {'telegram': id},
                {'email': id},
            ],
            preference: None,
        })

        # Controllo su preferenza non su un campo null
        assert count == 0, f'Il campo "{preference}" non è impostato'

        return self.collection('users').find_one_and_update(
            {'$or': [  # Confronta id sia con telegram che con email
                {'telegram': id},
                {'email': id},
            ]},
            {
                '$set': {
                    'preferenza': preference
                }
            }
        )

    def update_user_telegram(self, id: str, new_telegram: str):
        """Aggiorna lo user ID di Telegram dell'utente corrispondente a
        `id` (Telegram o Email).
        Raises:
        `AssertionError` -- se `new_telegram` corrisponde a un
            campo `telegram` già esistente,
            se `id` non è presente nel DB oppure se tenta di
            settare a `None` mentre lo è anche `Email`.
        """
        assert self.user_exists(id), f'User {id} inesistente'

        assert not self.user_exists(new_telegram), \
            f'User {new_telegram} già presente nel sistema'

        if new_telegram == '':
            new_telegram = None

        if new_telegram is None and not self.user_has_email(id):
            raise AssertionError('Operazione fallita. Impostare prima '
                                 'una Email')

        return self.collection('users').find_one_and_update(
            {'$or': [
                {'telegram': id},
                {'email': id},
            ]},
            {
                '$set': {
                    'telegram': new_telegram,
                }
            }
        )

    def update_user_email(self, id: str, new_email: str):
        """Aggiorna l'Email dell'utente corrispondente a
        `id` (Telegram o Email).
        Raises:
        `AssertionError` -- se `new_email` corrisponde a un
            campo `email` già esistente,
            se `id` non è presente nel DB oppure se tenta di
            settare a `None` mentre lo è anche il campo
            `telegram`.
        """
        assert self.user_exists(id), f'User {id} inesistente'

        assert not self.user_exists(new_email), \
            f'User {new_email} già presente nel sistema'

        if new_email == '':
            new_email = None

        if new_email is None and not self.user_has_telegram(id):
            raise AssertionError('Operazione fallita. Impostare prima '
                                 'un account Telegram')

        return self.collection('users').find_one_and_update(
            {'$or': [
                {'telegram': id},
                {'email': id},
            ]},
            {
                '$set': {
                    'email': new_email,
                }
            }
        )

    def update_user_name(self, id: str, new_name: str):
        """Aggiorna il `name` dell'utente corrispondente a
        `id` (Telegram o Email).
        Raises:
        `AssertionError` -- se `id` non è presente nel DB
        """
        assert self.user_exists(id), f'User {id} inesistente'

        return self.collection('users').find_one_and_update(
            {'$or': [
                {'telegram': id},
                {'email': id},
            ]},
            {
                '$set': {
                    'name': new_name
                }
            }
        )

    def update_user_surname(self, id: str, new_surname: str):
        """Aggiorna il `surname` dell'utente corrispondente a
        `id` (Telegram o Email).
        Raises:
        `AssertionError` -- se `id` non è presente nel DB
        """
        assert self.user_exists(id), f'User {id} inesistente'

        return self.collection('users').find_one_and_update(
            {'$or': [
                {'telegram': id},
                {'email': id},
            ]},
            {
                '$set': {
                    'surname': new_surname
                }
            }
        )

    def add_user_topic(self, id: str, label: str, project: str):
        """Aggiunge il `topic` corrispondente a `label`-`project`
        (NON ne crea uno!) alla lista dei topic dell'user
        corrispondente a `id`.
        Raises:
        `AssertionError` -- se `id`, `project` o `topic` non sono
            riconosciuti dal sistema.
        """
        assert self.user_exists(id), f'User {id} inesistente'
        assert self.project_exists(project), 'Progetto sconosciuto'
        assert self.topic_exists(label, project), 'Topic inesistente'

        topic_id = self.topics({'label': label, 'project': project})[0]['_id']
        return self.collection('users').find_one_and_update(
            {'$or': [  # Confronta id sia con telegram che con email
                {'telegram': id},
                {'email': id},
            ]},
            {
                '$addToSet': {  # Aggiunge all'array topics, senza duplicare
                    'topics': topic_id,
                }
            }
        )

    def add_user_topic_from_id(self, id: str, topic_id: int):
        """Aggiunge il `topic` corrispondente a `topic_id`
        (NON ne crea uno!) alla lista dei topic dell'user
        corrispondente a `id`.
        Raises:
        `AssertionError` -- se `id`, `project` o `topic_id` non sono
            riconosciuti dal sistema.
        """
        assert self.user_exists(id), f'User {id} inesistente'
        assert self.topic_from_id_exists(topic_id), 'Topic inesistente'
        return self.collection('users').find_one_and_update(
            {'$or': [  # Confronta id sia con telegram che con email
                {'telegram': id},
                {'email': id},
            ]},
            {
                '$addToSet': {  # Aggiunge all'array topics, senza duplicare
                    'topics': topic_id,
                }
            }
        )

    def add_keywords(self, id: str, *new_keywords):
        """Aggiunge le keywords passate come argomento all'user
        corrispondente a `id`.
        Raises:
        `AssertionError` -- se `id` non è presente nel DB.
        """
        assert self.user_exists(id), f'User {id} inesistente'
        return self.collection('users').find_one_and_update(
            {'$or': [  # Confronta id sia con telegram che con email
                {'telegram': id},
                {'email': id},
            ]},
            {
                '$addToSet': {  # Aggiunge all'array keywords, senza duplicare
                    'keywords': {
                        '$each': [*new_keywords]  # Per ogni elemento
                    }
                }
            }
        )

    # ------------------------------------
    # Listing di campi di user specifici |
    # ------------------------------------

    def user_keywords(self, id: str) -> list:
        """Restituisce una lista contenente le parole chiave corrispondenti
        all'`id`: esso può essere sia il contatto Telegram che Email.
        """
        cursor = self.users({
            '$or': [
                {'telegram': id},
                {'email': id},
            ]
        })
        return cursor[0]['keywords']

    def user_topics(self, id: str) -> list:
        """Restituisce una `Cursor` contenente i topic corrispondenti
        all'`id` del'utente: `id` può essere sia il contatto
        Telegram che Email.
        """
        assert self.user_exists(id), f'User {id} inesistente'

        cursor = self.users({
            '$or': [
                {'telegram': id},
                {'email': id},
            ]
        })
        topic_ids = cursor[0]['topics']

        # Match di tutti i topic che hanno un _id contenuto in topic_ids
        return self.topics({
            '_id': {
                '$in': topic_ids,
            }
        })

    # -------------------------------
    # Check user has telegram/email |
    # -------------------------------

    def user_has_telegram(self, id: str) -> bool:
        """Restituisce `True` se lo user corrispondente a `id`
        ha il campo `telegram` impostato.
        """
        assert self.user_exists(id), f'User {id} inesistente'

        count = self.collection('users').count_documents({
            '$or': [
                {'telegram': id},
                {'email': id},
            ],
            'telegram': None,
        })
        if count == 1:
            return False
        return True

    def user_has_email(self, id: str) -> bool:
        """Restituisce `True` se lo user corrispondente a `id`
        ha il campo `email` impostato.
        """
        assert self.user_exists(id), f'User {id} inesistente'

        count = self.collection('users').count_documents({
            '$or': [
                {'telegram': id},
                {'email': id},
            ],
            'email': None,
        })
        if count == 1:
            return False
        return True

    # -------------------
    # Proprietà/getters |
    # -------------------

    @property
    def dbConnection(self):
        """Ritorna l'oggetto `DBConnection` legato a `self`.
        """
        return self._dbConnection

    def user(self, id):
        """Restituisce un oggetto Python corrispondente all'`id`
        passato come argomento.
        Raises:
        `AssertionError` -- se `id` non è presente nel DB.
        """
        assert self.user_exists(id), f'User {id} inesistente'

        return self.users({
            '$or': [
                {'telegram': id},
                {'email': id},
            ]
        })[0]

    def collection(
            self,
            collection_name: str
    ) -> pymongo.collection.Collection:
        """Restituisce la collezione con il nome passato come
        argomento."""
        return self.dbConnection.db[collection_name]

    # -------------------------------
    # Funzioni ausiliarie/debugging |
    # -------------------------------

    def _insert_document(
            self,
            document: dict,
            collection: str,
    ) -> pymongo.collection.InsertOneResult:
        """Aggiunge il documento `document` alla collezione
        `collection`, se non è già presente. Restituisce un
        `InsertOneResult`.
        """
        result = self.dbConnection.db[collection].insert_one(document)
        return result

    def _delete_one_document(
            self,
            filter: dict,
            collection: str,
    ) -> pymongo.collection.DeleteResult:
        """Rimuove un documento che corrisponde al
        `filter`, se presente, e restituisce il risultato.
        Restituisce un `DeleteResult`.
        """
        result = self.dbConnection.db[collection].delete_one(filter)
        return result

    def _print_user(self, id):
        pprint.pprint(self.users({
            '$or': [
                {'telegram': id},
                {'email': id},
            ]
        })[0])

    @classmethod
    def _user_dict_no_id(cls, obj: dict):
        return {
            'name': obj['name'],
            'surname': obj['surname'],
            'telegram': obj['telegram'],
            'email': obj['email'],
            'preferenza': None,
            'topics': [],
            'keywords': [],
            'irreperibilità': obj['irreperibilità'],
            'sostituto': None,
        }
