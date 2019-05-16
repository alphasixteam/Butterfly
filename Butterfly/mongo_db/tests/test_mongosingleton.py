"""
File: test_mongosingleton.py
Data creazione: 2019-04-01

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

Versione: 0.2.1
Creatore: Timoty Granziero, timoty.granziero@gmail.com
"""

import unittest
from mongo_db.singleton import MongoSingleton


class TestMongoSingleton(unittest.TestCase):

    # Chiamato all'inizio
    @classmethod
    def setUpClass(cls):  # NOSONAR
        cls.client = MongoSingleton.Singleton('butterfly_test')

    # Chiamato alla fine
    @classmethod
    def tearDownClass(cls):  # NOSONAR
        cls.client._client.drop_database('butterfly_test')

    def test_crud(self):

        with self.subTest('Create'):
            res = self.client.create({
                '_id': 1,
                'name': 'Nome'
                },
                'users').inserted_id
            assert res == 1

            res = self.client.create({
                '_id': 2,
                'name': 'AltroNome'
                },
                'users').inserted_id
            assert res == 2

        with self.subTest('Read'):
            res = self.client.read('users').find({'_id': 1}).next()
            assert 'Nome' == res['name']
            assert 1 == res['_id']

        with self.subTest('Delete'):
            res = self.client.delete({'_id': 1}, 'users').deleted_count
            assert res == 1
            res = self.client.delete(
                {'name': 'AltroNome'},
                'users').deleted_count
            assert res == 1

            # Delete fallita
            res = self.client.delete({'_id': 1}, 'users').deleted_count
            assert res == 0
