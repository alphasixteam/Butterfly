"""
File: users.py
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
import datetime

import bson

from mongo_db.singleton import MongoSingleton


class MongoUsers:

    def __init__(self, mongo: MongoSingleton):
        self._mongo = mongo

    @staticmethod
    def _user_dict_no_id(obj: dict):
        return {
            'name': obj['name'],
            'surname': obj['surname'],
            'telegram': obj['telegram'],
            'email': obj['email']
        }

    def users(self, mongofilter={}):
        """Restituisce un `Cursor` che corrisponde al `filter` passato
        alla collezione `users`.
        Per accedere agli elementi del cursore, è possibile iterare con
        un `for .. in ..`, oppure usare il subscripting `[i]`.
        """
        return self._mongo.read('users').find(mongofilter)

    def exists(self, user: str) -> bool:
        """Restituisce `True` se l'`id` di un utente
        (che può essere Telegram, Email o _id) è salvato nel DB.
        """
        if bson.objectid.ObjectId.is_valid(user):
            count = self._mongo.read('users').count_documents(
                {'_id': bson.objectid.ObjectId(user)}
            )
        else:
            count = self._mongo.read('users').count_documents({
                '$or': [
                    {'telegram': user},
                    {'email': user}
                ]
            })
        return count != 0 and user != ''

    def create(self, **fields):
        # Collezione di interesse
        users = self._mongo.read('users')

        # Valori di default dei campi
        defaultfields = {
            '_id': None,
            'name': None,
            'surname': None,
            'telegram': None,
            'email': None,
            # 'irreperibilita': [],
            # 'projects': [],
        }

        new_user = copy.copy(defaultfields)  # Copia profonda del dict default

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
        # assert not self.controller.exists(new_user['telegram']), \
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

        # Via libera all'aggiunta al DB
        if new_user['_id'] is None:  # Per non mettere _id = None sul DB
            del new_user['_id']

        return self._mongo.create(
            new_user,
            'users'
        )

    def read(self, user: str):
        """Restituisce un oggetto Python corrispondente all'`user`
        passato come argomento.

        Raises:
        `AssertionError` -- se `user` non è presente nel DB.
        """
        assert self.exists(user), f'User {user} inesistente'
        if bson.objectid.ObjectId.is_valid(user):
            return self.users({
                '_id': bson.objectid.ObjectId(user)
            }).next()
        else:
            return self.users({
                '$or': [
                    {'telegram': user},
                    {'email': user},
                ]
            }).next()

    def read_by_project(self, project: str):
        """Restituisce una lista corrispondente al `project`
        passato come argomento.
        """
        return self.users({
            'projects.url': project
        })

    def delete_from_id(self, user: str):
        """Rimuove un documento che corrisponde a
        `user`, se presente. `user` è l'identificativo nel db
        """
        return self._mongo.delete(
            {'_id': bson.objectid.ObjectId(user)}, 'users'
        )

    def delete(self, user: str):
        """Rimuove un documento che corrisponde a
        `user`, che può essere `telegram` o `email`.
        """
        return self._mongo.delete({
            '$or': [
                {'telegram': user},
                {'email': user},
            ]
        }, 'users')

    def update_name(self, user: str, name: str):
        """Aggiorna il `name` dell'utente corrispondente a
        `user` (Telegram o Email).

        Raises:
        `AssertionError` -- se `user` non è presente nel DB
        """
        assert self.exists(user), f'User {user} inesistente'

        return self._mongo.read('users').find_one_and_update(
            {'$or': [
                {'telegram': user},
                {'email': user},
            ]},
            {
                '$set': {
                    'name': name
                }
            }
        )

    def update_surname(self, user: str, surname: str):
        """Aggiorna il `surname` dell'utente corrispondente a
        `user` (Telegram o Email).

        Raises:
        `AssertionError` -- se `user` non è presente nel DB
        """
        assert self.exists(user), f'User {user} inesistente'

        return self._mongo.read('users').find_one_and_update(
            {'$or': [
                {'telegram': user},
                {'email': user},
            ]},
            {
                '$set': {
                    'surname': surname
                }
            }
        )

    def _user_has_telegram(self, user: str) -> bool:
        """Restituisce `True` se lo user corrispondente a `user`
        ha il campo `telegram` impostato.
        """
        assert self.exists(user), f'User {user} inesistente'
        if bson.objectid.ObjectId.is_valid(user):
            count = self._mongo.read('users').count_documents({
                '_id': bson.objectid.ObjectId(user)
            })
        else:
            count = self._mongo.read('users').count_documents({
                '$or': [
                    {'telegram': user},
                    {'email': user},
                ],
                'telegram': None,
            })
        return count != 1

    def _user_has_email(self, user: str) -> bool:
        """Restituisce `True` se lo user corrispondente a `user`
        ha il campo `email` impostato.
        """
        assert self.exists(user), f'User {user} inesistente'
        if bson.objectid.ObjectId.is_valid(user):
            count = self._mongo.read('users').count_documents({
                '_id': bson.objectid.ObjectId(user)
            })
        else:
            count = self._mongo.read('users').count_documents({
                '$or': [
                    {'telegram': user},
                    {'email': user},
                ],
                'email': None,
            })
        return count != 1

    def _user_has_project(self, user: str, project: str) -> bool:
        """Restituisce True se `user` ha il progetto con valore
        `url == project`.
        """
        assert self.exists(user), f'User {user} inesistente'
        if bson.objectid.ObjectId.is_valid(user):
            count = self._mongo.read('users').count_documents({
                '_id': bson.objectid.ObjectId(user),
                'projects.url': project
            })
        else:
            count = self._mongo.read('users').count_documents({
                '$or': [
                    {'telegram': user},
                    {'email': user},
                ],
                'projects.url': project,
            })
        return count != 0

    def update_telegram(self, user: str, telegram: str):
        """Aggiorna lo user ID di Telegram dell'utente corrispondente a
        `user` (Telegram o Email).

        Raises:
        `AssertionError` -- se `new_telegram` corrisponde a un
            campo `telegram` già esistente,
            se `user` non è presente nel DB oppure se tenta di
            settare a `None` mentre lo è anche `Email`.
        """
        assert self.exists(user), f'User {user} inesistente'

        assert not self.exists(telegram), \
            f'User {telegram} già presente nel sistema'

        new_telegram = telegram

        if telegram == '':
            new_telegram = None

        if new_telegram is None and not self._user_has_email(user):
            raise AssertionError('Operazione fallita. Impostare prima '
                                 'una Email')

        return self._mongo.read('users').find_one_and_update(
            {'$or': [
                {'telegram': user},
                {'email': user},
            ]},
            {
                '$set': {
                    'telegram': new_telegram,
                }
            }
        )

    def update_email(self, user: str, email: str):
        """Aggiorna l'Email dell'utente corrispondente a
        `user` (Telegram o Email).

        Raises:
        `AssertionError` -- se `new_email` corrisponde a un
            campo `email` già esistente,
            se `user` non è presente nel DB oppure se tenta di
            settare a `None` mentre lo è anche il campo
            `telegram`.
        """
        assert self.exists(user), f'User {user} inesistente'

        assert not self.exists(email), \
            f'User {email} già presente nel sistema'

        new_email = email

        if email == '':
            new_email = None

        if new_email is None and not self._user_has_telegram(user):
            raise AssertionError('Operazione fallita. Impostare prima '
                                 'un account Telegram')

        return self._mongo.read('users').find_one_and_update(
            {'$or': [
                {'telegram': user},
                {'email': user},
            ]},
            {
                '$set': {
                    'email': new_email,
                }
            }
        )

    def update_user_preference(self, user: str, preference: str):
        """Aggiorna la preferenza (tra Telegram e Email) dell'utente
        corrispondente all'`user` (Telegram o Email).

        Raises:
        `AssertionError` -- se preference non è `telegram` o `email`
            oppure se `user` non è presente nel DB.
        """

        # Controllo validità campo preference
        assert preference.lower() in ('telegram', 'email'), \
            f'Selezione {preference} non valida: scegli tra Telegram o Email'

        # Controllo esistenza user user
        assert self.exists(user), f'User {user} inesistente'

        count = self._mongo.read('users').count_documents({
            '$or': [  # Confronta user sia con telegram che con email
                {'telegram': user},
                {'email': user},
            ],
            preference: None,
        })

        # Controllo su preferenza non su un campo null
        assert count == 0, f'Il campo "{preference}" non è impostato'

        return self._mongo.read('users').find_one_and_update(
            {'$or': [  # Confronta user sia con telegram che con email
                {'telegram': user},
                {'email': user},
            ]},
            {
                '$set': {
                    'preference': preference
                }
            }
        )

    def add_project(
        self,
        user: str,
        project: str,
        priority: int = 3,
        topics: list = [],
        keywords: list = [],
    ):
        """Aggiunge un progetto all'utente `user` il progetto con i campi
        passati come parametro.
        """
        assert self.exists(user), f'User {user} inesistente'
        assert not self._user_has_project(user, project), \
            f'{user} ha già il progetto {project}'

        return self._mongo.read('users').find_one_and_update(
            {'$or': [  # Confronta user sia con telegram che con email
                {'telegram': user},
                {'email': user},
            ]},
            {
                '$addToSet': {  # Aggiunge all'array projects, senza duplicare
                    'projects': {
                        'url': project,
                        'priority': priority,
                        'topics': topics,
                        'keywords': keywords,
                    }
                }
            }
        )

    def remove_project(self, user: str, project: str):
        """Rimuove un progetto all'utente `user`"""
        assert self.exists(user), f'User {user} inesistente'
        assert self._user_has_project(user, project), \
            f'{user} non ha già il progetto {project}'

        return self._mongo.read('users').find_one_and_update(
            {'$or': [  # Confronta user sia con telegram che con email o _id
                {'telegram': user},
                {'email': user},
            ]},
            {
                # Rimuove dall'array il progetto
                '$pull': {
                    'projects': {
                        'url': project
                    }
                }
            }
        )

    def add_keywords(self, user: str, project: str, *new_keywords):
        """Aggiunge le keywords passate come argomento all'user
        corrispondente a `user`.

        Raises:
        `AssertionError` -- se `user` non è presente nel DB.
        """

        assert self._user_has_project(user, project), \
            f'{user} non ha in lista il progetto {project}'

        return self._mongo.read('users').update_one({
            '$or': [
                {'telegram': user},
                {'email': user},
            ],
            "projects.url": project,
        },
            {
            '$addToSet': {  # Aggiunge all'array keywords, senza duplicare
                f'projects.$.keywords': {
                    '$each': [*new_keywords]  # Per ogni elemento
                }
            }
        })

    def remove_keywords(self, user: str, project: str, *kw_to_remove):

        assert self._user_has_project(user, project), \
            f'{user} non ha in lista il progetto {project}'

        self._mongo.read('users').update_one({
            '$or': [
                {'telegram': user},
                {'email': user},
            ],
            "projects.url": project,
        },
            {
            '$pull': {  # Rimuove dall'array gli elementi in kw_to_remove
                f'projects.$.keywords': {
                    '$in': [*kw_to_remove]  # Per ogni elemento
                }
            }
        })

    def reset_keywords(self, user: str, project: str):

        assert self._user_has_project(user, project), \
            f'{user} non ha in lista il progetto {project}'

        self._mongo.read('users').update_one(
            {
                '$and': [
                    {'$or': [
                        {'telegram': user},
                        {'email': user},
                    ]},
                    {'projects.url': project}
                ]
            },
            {
                '$set': {
                    "projects.$.keywords": []
                }
            }
        )

    def user_keywords(self, user: str, project: str) -> list:
        """Restituisce una lista contenente le parole chiave corrispondenti
        a `project` di `user`: esso può essere sia il contatto Telegram
        che Email.
        """
        assert self._user_has_project(user, project), \
            f'{user} non ha in lista il progetto {project}'
        if bson.objectid.ObjectId.is_valid(user):
            cursor = self._mongo.read('users').find({
                '_id': bson.objectid.ObjectId(user),
                'projects.url': project
            },
                {
                    '_id': 0,
                    'projects.$.keywords': 1,
            })
        else:
            cursor = self._mongo.read('users').find({
                '$or': [
                    {'telegram': user},
                    {'email': user},
                ],
                'projects.url': project,
            },
                {
                    '_id': 0,
                    'projects.$.keywords': 1,
            })

        try:
            return cursor.next()['projects'][0]['keywords']
        except StopIteration:
            return []

    def add_labels(self, user: str, project: str, *new_labels):
        """Aggiunge le labels passate come argomento all'user
        corrispondente a `user` nel progetto `project`.

        Raises:
        `AssertionError` -- se `user` non è presente nel DB.
        """

        assert self._user_has_project(user, project), \
            f'{user} non ha in lista il progetto {project}'

        return self._mongo.read('users').update_one({
            '$or': [
                {'telegram': user},
                {'email': user},
            ],
            "projects.url": project,
        },
            {
            '$addToSet': {  # Aggiunge all'array keywords, senza duplicare
                f'projects.$.topics': {
                    '$each': [*new_labels]  # Per ogni elemento
                }
            }
        })

    def remove_labels(self, user: str, project: str, *labels_to_remove):
        assert self._user_has_project(user, project), \
            f'{user} non ha in lista il progetto {project}'

        return self._mongo.read('users').update_one({
            '$or': [
                {'telegram': user},
                {'email': user},
            ],
            "projects.url": project,
        },
            {
            '$pull': {  # Rimuove dall'array labels_to_remove
                f'projects.$.topics': {
                    '$in': [*labels_to_remove]  # Per ogni elemento
                }
            }
        })

    def reset_labels(self, user: str, project: str):

        assert self._user_has_project(user, project), \
            f'{user} non ha in lista il progetto {project}'

        self._mongo.read('users').update(
            {
                '$and': [
                    {'$or': [
                        {'telegram': user},
                        {'email': user},
                    ]},
                    {'projects.url': project}
                ]
            },
            {
                '$set': {
                    "projects.$.topics": []
                }
            }
        )

    def user_labels(self, user: str, project: str) -> list:
        """Restituisce una lista contenente le label corrispondenti
        a `project` di `user`: esso può essere sia il contatto Telegram
        che Email.
        """

        assert self._user_has_project(user, project), \
            f'{user} non ha in lista il progetto {project}'
        if bson.objectid.ObjectId.is_valid(user):
            cursor = self._mongo.read('users').find({
                '_id': bson.objectid.ObjectId(user),
                'projects.url': project
            },
                {
                    '_id': 0,
                    'projects.$.topics': 1,
            })
        else:
            cursor = self._mongo.read('users').find({
                '$or': [
                    {'telegram': user},
                    {'email': user},
                ],
                'projects.url': project,
            },
                {
                    '_id': 0,
                    'projects.$.topics': 1,
            })

        try:
            return cursor.next()['projects'][0]['topics']
        except StopIteration:
            return []

    def _get_users_by_priority(self, project: str, priority: int):
        """Restituisce gli utenti con priorità specificata iscritti
        a `project` disponibili in data odierna.
        """
        date = datetime.datetime.today()  # today, compreso time

        # today, esclusi i valori time
        date = datetime.datetime(date.year, date.month, date.day)

        cursor = self._mongo.read('users').find({
            'projects': {
                '$elemMatch': {
                    'url': project,
                    'priority': priority
                },
            },
            'irreperibilita': {
                '$nin': [date]
            }
        }, {
            '_id': 1,
        })

        user_list = []
        for identifier in cursor:
            user_list.append(identifier['_id'])
        return user_list

    def set_priority(self, user: str, project: str, priority: int):
        """Modifica la priorità di un progetto per l'utente specificato.
        """
        assert self.exists(user), f'User {user} inesistente'
        return self._mongo.read('users').find_one_and_update(
            {
                '$and': [
                    {'$or': [
                        {'telegram': user},
                        {'email': user},
                    ]},
                    {'projects.url': project}
                ]
            },
            {
                '$set': {
                    "projects.$.priority": bson.Int64(priority)
                }
            }
        )

    def get_users_available(self, project: str) -> list:
        """Dato un progetto, cerco tutti
        Gli utenti disponibili oggi
        (la lista di ritorno contiene gli ID del DB)
        """
        users = []
        for priority in range(1, 4):  # Cicla da 1 a 3
            users += self._get_users_by_priority(project, priority)
        return users

    def get_users_max_priority(self, project: str) -> list:
        """Dato un progetto, ritorno la lista di
        utenti disponibili oggi di priorità maggiore
        (la lista di ritorno contiene gli ID del DB)
        """
        for priority in range(1, 4):
            max_priority = self._get_users_by_priority(project, priority)
            if max_priority:
                return max_priority
        return []

    def filter_max_priority(self, user_list: list, project: str) -> list:
        """Data una lista di utenti, ritorno la sottolista di
        utenti con priorità maggiore per il progetto specificato
        """
        users = []
        for priority in range(1, 4):
            max_priority = self._get_users_by_priority(project, priority)
            for user in user_list:
                if user in max_priority:
                    users.append(user)
            if users:
                return users
        return []

    def get_user_telegram_from_id(self, user: str):
        try:
            return self.users({
                '_id': bson.objectid.ObjectId(user)
            }).next()['telegram']
        except StopIteration:
            return None

    def get_user_email_from_id(self, user: str):
        try:
            return self.users({
                '_id': bson.objectid.ObjectId(user)
            }).next()['email']
        except StopIteration:
            return None

    def get_user_telegram(self, user: str):
        try:
            return self.users({
                '$and': [
                    {'_id': bson.objectid.ObjectId(user)},
                    {'$or': [
                        {'preference': 'telegram'},
                        {'email': None},
                    ]},
                ]
            }).next()['telegram']
        except StopIteration:
            return None

    def get_user_telegram_web(self, user: str):
        try:
            return self.users({
                '$or': [
                    {'telegram': user},
                    {'email': user},
                ]
            }).next()['telegram']
        except StopIteration:
            return None

    def get_user_email(self, user: str):
        try:
            return self.users({
                '$and': [
                    {'_id': bson.objectid.ObjectId(user)},
                    {'$or': [
                        {'preference': 'email'},
                        {'telegram': None},
                    ]},
                ]
            }).next()['email']
        except StopIteration:
            return None

    def get_user_email_web(self, user: str):
        try:
            return self.users({
                '$or': [
                    {'telegram': user},
                    {'email': user},
                ]
            }).next()['email']
        except StopIteration:
            return None

    def get_match_keywords(
        self,
        users: list,
        project: str,
        commit: str,
    ) -> list:
        keyword_user = []
        for user in users:
            if self.match_keyword_commit(
                self.user_keywords(user, project),
                commit
            ):
                keyword_user.append(user)
        return keyword_user

    @staticmethod
    def match_keyword_commit(
        keywords: list,
        commit_msg: str,
        case=True
    ) -> bool:
        """Restituisce `True` se `commit_msg` contiene una
        o più keyword contenute in `keywords`.
        `case` è `True` se la ricerca è case sensitive, `False`
        altrimenti.
        """
        if case is True:
            for keyword in keywords:
                if keyword in commit_msg:
                    return True
            return False

        # Case insensitive
        for keyword in keywords:
            if keyword.lower() in commit_msg.lower():
                return True
        return False

    def get_match_labels(
        self,
        users: list,
        project: str,
        labels: list,
    ) -> list:
        """Guarda se almeno una label di un user (chiamando get_user_labels) è
        presente nelle label della issue
        Per redmine c'è una sola label, per gitlab una lista
        Ritorna true se è presente almeno una label dell'utente
        nelle label della issue
        """
        label_user = []
        for user in users:
            if self.match_labels_issue(
                self.user_labels(user, project),
                labels,
            ):
                label_user.append(user)
        return label_user

    @staticmethod
    def match_labels_issue(user_labels: list, labels: list) -> bool:
        for label in user_labels:
            if label in labels:
                return True
        return False

    def get_projects(self, user: str) -> list:
        """Restituisce una mappa contenente i progetti a cui è iscritto un
        utente e i relativi dati.

        Raises:
        `AssertionError` -- se `user` non è presente nel DB.
        """
        assert self.exists(user), f'User {user} inesistente'

        if bson.objectid.ObjectId.is_valid(user):
            user = self._mongo.read('users').find({
                '_id': bson.objectid.ObjectId(user)
            }, {
                'projects': 1,
            }).next()
        else:
            user = self._mongo.read('users').find({
                '$or': [
                    {'telegram': user},
                    {'email': user},
                ]
            }, {
                'projects': 1,
            }).next()
        if 'projects' in user:
            return user['projects']
        return []

    def add_giorno_irreperibilita(
        self,
        user: str,
        year: int, month: int, day: int,
    ):
        """Aggiunge il giorno di irreperibilità specificato all'utente `user`.
        `user` può corrispondere ai campi `_id`, `telegram` o `email`.
        """
        assert self.exists(user), f'User {user} inesistente'
        date = datetime.datetime(year, month, day, 0, 0)
        return self._mongo.read('users').find_one_and_update(
            {'$or': [  # Confronta user sia con telegram che con email o _id
                {'telegram': user},
                {'email': user},
            ]},
            {
                # Aggiunge all'array irreperibilita, senza duplicare
                '$addToSet': {
                    'irreperibilita': date,
                }
            }
        )

    def remove_giorno_irreperibilita(
        self,
        user: str,
        year: int, month: int, day: int,
    ):
        """Rimuove il giorno di irreperibilità specificato all'utente `user`,
        se presente.
        `user` può corrispondere ai campi `_id`, `telegram` o `email`.
        """
        assert self.exists(user), f'User {user} inesistente'
        date = datetime.datetime(year, month, day, 0, 0)
        return self._mongo.read('users').find_one_and_update(
            {'$or': [  # Confronta user sia con telegram che con email o _id
                {'telegram': user},
                {'email': user},
            ]},
            {
                # Rimuove dall'array irreperibilita
                '$pull': {
                    'irreperibilita': date,
                }
            }
        )
