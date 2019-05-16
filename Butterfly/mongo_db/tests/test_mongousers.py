"""
File: test_mongousers.py
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
import datetime

import pytest

from mongo_db.singleton import MongoSingleton
from mongo_db.users import MongoUsers


class TestMongoUsers(unittest.TestCase):

    # Chiamato all'inizio
    @classmethod
    def setUpClass(cls):  # NOSONAR
        cls.client = MongoUsers(MongoSingleton.Singleton('butterfly_test'))

    # Chiamato alla fine
    @classmethod
    def tearDownClass(cls):  # NOSONAR
        cls.client._mongo._client.drop_database('butterfly_test')

    def test_crud(self):
        with self.subTest('Raises'):
            self.assertRaises(
                AssertionError,  # Ne telegram ne email inseriti
                self.client.create,
                name='Timoty',
                surname='Granziero',
            )

        with self.subTest('Create'):
            res = self.client.create(
                _id=123,
                name='Timoty',
                surname='Granziero',
                telegram='12332').inserted_id
            assert res == 123

            res = self.client.create(
                _id=124,
                name='Simone',
                surname='Granziero',
                telegram='12343',
                email='aa@a.it').inserted_id
            assert res == 124

            self.assertRaises(
                AssertionError,
                self.client.create,
                telegram='12343',
            )

            self.assertRaises(
                AssertionError,
                self.client.create,
                email='aa@a.it',
            )

        with self.subTest('Read'):
            self.assertRaises(
                AssertionError,  # Nessun contatto TG o email corrispondente
                self.client.read,
                'aaa'
            )
            user = self.client.read('12332')
            assert user['name'] == 'Timoty'
            assert user['surname'] == 'Granziero'
            assert user['email'] is None

            user = self.client.read('aa@a.it')
            assert user['name'] == 'Simone'
            assert user['surname'] == 'Granziero'
            assert user['telegram'] == '12343'
            assert user['email'] is not None

        with self.subTest('Update name'):
            self.assertRaises(
                AssertionError,  # Nessun contatto TG o email corrispondente
                self.client.update_name,
                'aaa',
                'New name',
            )

            user = self.client.read('12343')
            assert user['name'] != 'Andrew'

            res = self.client.update_name('12343', 'Andrew')
            assert res['name'] == 'Simone'  # ex name

            user = self.client.read('12343')
            assert user['name'] == 'Andrew'

        with self.subTest('Update surname'):
            self.assertRaises(
                AssertionError,  # Nessun contatto TG o email corrispondente
                self.client.update_surname,
                'aaa',
                'New surname',
            )

            user = self.client.read('12343')
            assert user['surname'] != 'Tanenbaum'

            res = self.client.update_surname('12343', 'Tanenbaum')
            assert res['surname'] == 'Granziero'  # ex name

            user = self.client.read('12343')
            assert user['surname'] == 'Tanenbaum'

        with self.subTest('Update Telegram'):
            self.assertRaises(
                AssertionError,  # Nessun contatto TG o email corrispondente
                self.client.update_telegram,
                'aaa',
                'New telegram',
            )

            self.assertRaises(
                AssertionError,  # Contatto TG già presente
                self.client.update_telegram,
                '12343',
                '12332',
            )

            user = self.client.read('12343')
            assert user['telegram'] == '12343'
            assert user['name'] == 'Andrew'

            res = self.client.update_telegram('12343', '12345')
            assert res['telegram'] == '12343'

            user = self.client.read('12345')
            assert user['telegram'] == '12345'
            assert user['name'] == 'Andrew'
            assert user['surname'] == 'Tanenbaum'

        with self.subTest('Update email'):
            self.assertRaises(
                AssertionError,  # Nessun contatto TG o email corrispondente
                self.client.update_email,
                'aaa',
                'eee@email.it',
            )

            self.assertRaises(
                AssertionError,  # Contatto email già presente
                self.client.update_email,
                '12345',
                'aa@a.it',
            )

            user = self.client.read('12345')
            assert user['email'] == 'aa@a.it'
            assert user['name'] == 'Andrew'

            res = self.client.update_email('12345', 'aa@email.it')
            assert res['email'] == 'aa@a.it'

            user = self.client.read('12345')
            assert user['telegram'] == '12345'
            assert user['name'] == 'Andrew'
            assert user['surname'] == 'Tanenbaum'
            assert user['email'] == 'aa@email.it'

        with self.subTest('Delete'):
            res = self.client.delete_from_id(123).deleted_count
            assert res == 1

            # Failed delete
            res = self.client.delete('aaa@a.it').deleted_count
            assert res == 0

            res = self.client.delete('aa@email.it').deleted_count
            assert res == 1

    def test_add_project(self):
        res = self.client.create(
            _id=900,
            name='Timoty',
            surname='Granziero',
            telegram='900').inserted_id
        assert res == 900

        res = self.client.add_project(
            '900',  # id telegram/email
            'http://..',  # url
            1,  # priority
            ['topic1', 'topic2'],  # topics
            ['kw1', 'kw2'],  # keywords
        )
        assert res['email'] is None
        user = self.client.read('900')

        res = self.client.add_project(
            '900',  # id telegram/email
            'http://lol',  # url
            3,  # priority
            ['topic1'],  # topics
            ['kw1'],  # keywords
        )
        assert res['name'] == 'Timoty'

        for project in user['projects']:
            # Cerca il progetto inserito e lo testa
            if project['url'] == 'http://..':
                assert project['priority'] == 1
                assert project['topics'][0] == 'topic1'
                assert 'topic2' in project['topics']
                assert project['keywords'][0] == 'kw1'
                assert 'kw2' in project['keywords']
                assert 'kw2' not in project['topics']
            if project['url'] == 'http://lol':
                assert project['priority'] == 3

    def test_match_labels_issue(self):
        assert self.client.match_labels_issue(
            [1, 2, 4],
            [4, 5, 6],
        ) is True
        assert self.client.match_labels_issue(
            [4],
            ['str', 'aaa', 'b', 4],
        ) is True
        assert self.client.match_labels_issue(
            [1, 2, 3, 16],
            [4, 5, 6],
        ) is False
        assert self.client.match_labels_issue(
            [1, 2, 3, 16],
            [],
        ) is False
        assert self.client.match_labels_issue(
            [],
            [1, 2, 3, 16],
        ) is False

    def test_match_keyword_commit(self):
        assert self.client.match_keyword_commit(
            ['CI', 'java'],
            'Stringa contenente CI.',
        ) is True
        assert self.client.match_keyword_commit(
            ['CI', 'java'],
            'Stringa non contenente keywords. JAVA case sensitive',
        ) is False
        assert self.client.match_keyword_commit(
            ['CI', 'java'],
            'Stringa non contenente keywords. JAVA case insensitive',
            case=False,
        ) is True

    # @pytest.mark.skip()
    def test_add_labels(self):
        self.assertRaises(
            AssertionError,
            self.client.add_project,
            '11111111111', '', '', [], [])

        with self.subTest('add_labels'):
            res = self.client.create(
                _id=1000,
                name='Timoty',
                surname='Granziero',
                telegram='111').inserted_id
            assert res == 1000

            self.client.add_project(
                '111',
                'PROJECT',  # url
                3,  # priority
                ['topic1'],  # topics
                ['kw1'],  # keywords
            )

            self.client.add_labels('111', 'PROJECT', 'label1', 'label2')
            user = self.client.read('111')

            for project in user['projects']:
                if project['url'] == 'PROJECT':
                    assert 'topic1' in project['topics']
                    assert 'label1' in project['topics']
                    assert 'label2' in project['topics']

        with self.subTest('remove_labels'):
            self.client.remove_labels('111', 'PROJECT', 'label1')
            user = self.client.read('111')

            for project in user['projects']:
                if project['url'] == 'PROJECT':
                    assert 'topic1' in project['topics']
                    assert 'label1' not in project['topics']
                    assert 'label2' in project['topics']

        with self.subTest('user_labels'):
            # user = self.client.read('111')
            topics_lst = self.client.user_labels('111', 'PROJECT')
            assert 'label2' in topics_lst
            assert 'topic1' in topics_lst
            assert 'label1' not in topics_lst

            self.assertRaises(
                AssertionError,
                self.client.user_labels,
                '111',
                'AAAAAa',
            )
            self.assertRaises(
                AssertionError,
                self.client.user_labels,
                'AAAAAa',
                'PROJECT',
            )

    def test_add_keywords(self):
        self.assertRaises(
            AssertionError,
            self.client.add_project,
            '11111111111', '', '', [], [])

        with self.subTest('add_keywords'):
            res = self.client.create(
                _id=1100,
                name='Timoty',
                surname='Granziero',
                telegram='222').inserted_id
            assert res == 1100

            self.client.add_project(
                '222',
                'PROJECT',  # url
                3,  # priority
                ['topic1'],  # topics
                ['kw1'],  # keywords
            )

            self.client.add_keywords('222', 'PROJECT', 'kw3', 'kw2')
            user = self.client.read('222')

            self.assertRaises(
                AssertionError,
                self.client.add_keywords,
                '2222',
                'PROJECT',
            )
            self.assertRaises(
                AssertionError,
                self.client.user_keywords,
                '222',
                'AAAAAa',
            )

            for project in user['projects']:
                if project['url'] == 'PROJECT':
                    assert 'kw1' in project['keywords']
                    assert 'kw2' in project['keywords']
                    assert 'kw3' in project['keywords']

        with self.subTest('remove_keywords'):
            self.client.remove_keywords('222', 'PROJECT', 'kw2')
            user = self.client.read('222')

            self.assertRaises(
                AssertionError,
                self.client.remove_keywords,
                '2222',
                'PROJECT',
            )
            self.assertRaises(
                AssertionError,
                self.client.remove_keywords,
                '222',
                'AAAAAa',
            )

            for project in user['projects']:
                if project['url'] == 'PROJECT':
                    assert 'kw1' in project['keywords']
                    assert 'kw2' not in project['keywords']
                    assert 'kw3' in project['keywords']

        with self.subTest('user_keywords'):
            kw_lst = self.client.user_keywords('222', 'PROJECT')
            assert 'kw1' in kw_lst
            assert 'kw3' in kw_lst
            assert 'kw2' not in kw_lst

            self.assertRaises(
                AssertionError,
                self.client.user_keywords,
                '222',
                'AAAAAa',
            )
            self.assertRaises(
                AssertionError,
                self.client.user_keywords,
                'AAAAAa',
                'PROJECT',
            )

    def test_get_projects(self):
        res = self.client.create(
            _id=901,
            name='Matteo',
            surname='Marchiori',
            telegram='42').inserted_id
        assert res == 901

        res = self.client.add_project(
            '42',  # id telegram/email
            'http://..',  # url
            1,  # priority
            ['topic1', 'topic2'],  # topics
            ['kw1', 'kw2'],  # keywords
        )
        assert res['email'] is None

        self.assertRaises(  # Test project già presente
            AssertionError,
            self.client.add_project,
            '42',  # id telegram/email
            'http://..',  # url
            1,  # priority
            ['topic1', 'topic2'],  # topics
            ['kw1', 'kw2'],  # keywords
        )

        res = self.client.add_project(
            '42',  # id telegram/email
            'http://lol',  # url
            3,  # priority
            ['topic1'],  # topics
            ['kw1'],  # keywords
        )
        assert res['name'] == 'Matteo'

        res = self.client.get_projects('42')
        assert res[0]['url'] == "http://.."
        for project in res:
            # Testa i progetti
            if project['url'] == 'http://..':
                assert project['priority'] == 1
                assert project['topics'][0] == 'topic1'
                assert 'topic2' in project['topics']
                assert project['keywords'][0] == 'kw1'
                assert 'kw2' in project['keywords']
                assert 'kw2' not in project['topics']
            if project['url'] == 'http://lol':
                assert project['priority'] == 3

    def test_get_user_telegram_email(self):
        res = self.client.create(
            _id=1200,
            name='Timoty',
            surname='Granziero',
            telegram='2223',
            email='aaa@aaa.aaa').inserted_id
        assert res == 1200

        with self.subTest('telegram'):
            res = self.client.get_user_telegram('2223')
            assert res == '2223'
            res = self.client.get_user_telegram('aaa@aaa.aaa')
            assert res == '2223'
            res = self.client.get_user_telegram('22222222222')
            assert res is None

        with self.subTest('email'):
            res = self.client.get_user_email('2223')
            assert res == 'aaa@aaa.aaa'
            res = self.client.get_user_email('aaa@aaa.aaa')
            assert res == 'aaa@aaa.aaa'
            res = self.client.get_user_email('22222222222')
            assert res is None

    def test_match_keywords(self):
        res = self.client.create(
            _id=1300,
            name='Timoty',
            surname='Granziero',
            telegram='2332').inserted_id
        assert res == 1300

        res = self.client.add_project(
            '2332',  # id telegram/email
            'http://..',  # url
            1,  # priority
            ['topic1', 'topic2'],  # topics
            ['kw1', 'kw2', 'kw3'],  # keywords
        )
        assert res['telegram'] == '2332'

        res = self.client.create(
            _id=1301,
            name='Timotyy',
            surname='Granziero',
            telegram='2333').inserted_id
        assert res == 1301

        res = self.client.add_project(
            '2333',  # id telegram/email
            'http://..',  # url
            1,  # priority
            ['topic3', 'topic4'],  # topics
            ['kw8', 'kw9', 'kw7'],  # keywords
        )
        assert res['telegram'] == '2333'

        res = self.client.create(
            _id=1302,
            name='Timoty',
            surname='Granziero',
            telegram='2334').inserted_id
        assert res == 1302

        res = self.client.create(
            _id=1303,
            name='Timoty',
            surname='Granziero',
            email='b@b.b').inserted_id
        assert res == 1303

        res = self.client.add_project(
            'b@b.b',  # id telegram/email
            'http://..',  # url
            1,  # priority
            ['topic5', 'topic6'],  # topics
            ['kw1', 'kw6', 'kw3'],  # keywords
        )
        assert res['email'] == 'b@b.b'

        with self.subTest('match_kws'):
            user_list = self.client.get_match_keywords(
                ['2332', '2333', 'b@b.b'],
                'http://..',
                'kw1, aaa, kw2'
            )
            assert '2332' in user_list
            assert '2333' not in user_list
            assert 'b@b.b' in user_list
            assert '2334' not in user_list

        with self.subTest('match_labels'):
            user_list = self.client.get_match_labels(
                ['2332', '2333', 'b@b.b'],
                'http://..',
                ['topic5', 'topic3', 'topic4']
            )
            assert '2332' not in user_list
            assert '2333' in user_list
            assert 'b@b.b' in user_list
            assert '2334' not in user_list

    def test_add_giorno_irreperibilita(self):
        res = self.client.create(
            _id=1310,
            name='Timoty',
            surname='Granziero',
            email='b@b.bbb').inserted_id
        assert res == 1310
        res = self.client.add_giorno_irreperibilita(
            1310,
            2019, 4, 16,
        )
        res = self.client.add_giorno_irreperibilita(
            1310,
            2019, 4, 17,
        )

        user = self.client.users({'email': 'b@b.bbb'}).next()
        assert 2019 == user['irreperibilita'][0].year
        assert 4 == user['irreperibilita'][0].month
        assert 16 == user['irreperibilita'][0].day
        assert datetime.datetime(2019, 4, 16) in user['irreperibilita']

        res = self.client.add_giorno_irreperibilita(
            1310,
            2019, 4, 16,
        )
        res = self.client.add_giorno_irreperibilita(
            1310,
            2019, 4, 18,
        )
        user = self.client.users({'email': 'b@b.bbb'}).next()
        assert datetime.datetime(2019, 4, 17) in user['irreperibilita']
        assert datetime.datetime(2019, 4, 18) in user['irreperibilita']
        assert datetime.datetime(2019, 4, 10) not in user['irreperibilita']

    def test_update_user_preference(self):
        res = self.client.create(
            _id=1315,
            name='Timoty',
            surname='Granziero',
            telegram='12').inserted_id
        assert res == 1315

        self.assertRaises(
            AssertionError,
            self.client.update_user_preference,
            '999',  # User inesistente
            'telegram',
        )
        self.assertRaises(
            AssertionError,
            self.client.update_user_preference,
            '12',
            'eemail',  # no email o telegram
        )
        self.assertRaises(
            AssertionError,
            self.client.update_user_preference,
            '12',
            'email',  # campo non impostato
        )

        self.client.update_user_preference('12', 'telegram')
        user = self.client.read('12')
        assert user['preference'] == 'telegram'
        self.client.update_email('12', 'cret@cret.a')
        self.client.update_user_preference('12', 'email')
        user = self.client.read('12')
        assert user['preference'] == 'email'

    # @pytest.mark.skip()
    def test_get_users_by_priority_available_priority(self):
        res = self.client.create(
            _id=1901,
            name='Matteo',
            surname='Marchioni',
            telegram='420').inserted_id
        assert res == 1901

        res = self.client.add_project(
            '420',  # id telegram/email
            'http://project',  # url
            1,  # priority
            ['topic1', 'topic2'],  # topics
            ['kw1', 'kw2'],  # keywords
        )
        assert res['email'] is None

        self.assertRaises(  # Test project già presente
            AssertionError,
            self.client.add_project,
            '420',  # id telegram/email
            'http://project',  # url
            1,  # priority
            ['topic1', 'topic2'],  # topics
            ['kw1', 'kw2'],  # keywords
        )

        res = self.client.create(
            _id=1902,
            name='Matteo',
            surname='Marchionni',
            telegram='421').inserted_id
        assert res == 1902
        res = self.client.add_project(
            '421',  # id telegram/email
            'http://project',  # url
            2,  # priority
            ['topic1', 'topic2'],  # topics
            ['kw1', 'kw2'],  # keywords
        )

        res = self.client.create(
            _id=1903,
            name='Mattia',
            surname='Marchionni',
            telegram='422').inserted_id
        assert res == 1903
        res = self.client.add_project(
            '422',  # id telegram/email
            'http://project',  # url
            2,  # priority
            ['topic1', 'topic2'],  # topics
            ['kw1', 'kw2'],  # keywords
        )
        res = self.client.create(
            _id=1904,
            name='Mattia',
            surname='Marchionni',
            telegram='423').inserted_id
        assert res == 1904
        res = self.client.add_project(
            '423',  # id telegram/email
            'http://project',  # url
            3,  # priority
            ['topic1', 'topic2'],  # topics
            ['kw1', 'kw2'],  # keywords
        )
        res['name'] = 'Mattia'

        with self.subTest('_get_users_by_priority'):

            users = self.client._get_users_by_priority('http://project', 2)

            assert 1901 not in users
            assert 1902 in users
            assert 1903 in users
            assert 1904 not in users

            # Test con giorno di irreperibilità

            date = datetime.datetime.today()  # today, compreso time
            self.client.add_giorno_irreperibilita(
                1902,
                date.year, date.month, date.day,
            )

            users = self.client._get_users_by_priority('http://project', 2)

            assert 1901 not in users
            assert 1902 not in users
            assert 1903 in users
            assert 1904 not in users

        with self.subTest('get_users_available'):
            users = self.client.get_users_available('http://project')

            assert 1901 in users
            assert 1902 not in users
            assert 1903 in users
            assert 1904 in users

            date = datetime.datetime.today()  # today, compreso time
            self.client.add_giorno_irreperibilita(
                1904,
                date.year, date.month, date.day,
            )

            users = self.client.get_users_available('http://project')
            assert 1901 in users
            assert 1902 not in users
            assert 1903 in users
            assert 1904 not in users
            assert len(users) == 2

        with self.subTest('get_users_max_priority'):
            res = self.client.create(
                _id=1905,
                name='Mattia',
                surname='Marchionni',
                telegram='430').inserted_id
            assert res == 1905
            res = self.client.add_project(
                '430',  # id telegram/email
                'http://project',  # url
                2,  # priority
                ['topic1', 'topic2'],  # topics
                ['kw1', 'kw2'],  # keywords
            )

            users = self.client.get_users_max_priority('http://project')
            assert 1901 in users
            assert 1902 not in users
            assert 1903 not in users
            assert 1904 not in users
            assert 1905 not in users
            assert len(users) == 1

            date = datetime.datetime.today()  # today, compreso time
            self.client.add_giorno_irreperibilita(
                1901,
                date.year, date.month, date.day,
            )
            users = self.client.get_users_max_priority('http://project')
            assert 1901 not in users
            assert 1902 not in users
            assert 1903 in users
            assert 1904 not in users
            assert 1905 in users
            assert len(users) == 2
            users = self.client.get_users_max_priority('http://projectsss')
            assert users == []

        with self.subTest('filter_max_priority'):
            users = self.client.filter_max_priority(
                [1903, 1905, 1906, 2000],
                'http://project',
            )
            assert 1901 not in users
            assert 1902 not in users
            assert 1903 in users
            assert 1904 not in users
            assert 1905 in users
            assert 2000 not in users
            assert 1906 not in users
            assert len(users) == 2

            users = self.client.filter_max_priority(
                [1905, 1906, 2000],
                'http://project',
            )
            assert 1901 not in users
            assert 1902 not in users
            assert 1903 not in users
            assert 1904 not in users
            assert 1905 in users
            assert 2000 not in users
            assert 1906 not in users
            assert len(users) == 1

    def test_remove_giorno_irreperibilita(self):
        res = self.client.create(
            _id=90,
            name='Timoty',
            surname='Granziero',
            telegram='123322').inserted_id
        assert res == 90
        self.client.add_giorno_irreperibilita(
            '123322',
            2020, 6, 16,
        )
        # Doppione
        self.client.add_giorno_irreperibilita(
            '123322',
            2020, 6, 16,
        )
        self.client.add_giorno_irreperibilita(
            '123322',
            2021, 6, 16,
        )

        user = self.client.users({'telegram': '123322'}).next()
        assert 2020 == user['irreperibilita'][0].year
        assert 6 == user['irreperibilita'][0].month
        assert 16 == user['irreperibilita'][0].day
        assert datetime.datetime(2020, 6, 16) in user['irreperibilita']
        assert datetime.datetime(2021, 6, 16) in user['irreperibilita']
        assert datetime.datetime(2020, 7, 16) not in user['irreperibilita']
        assert len(user['irreperibilita']) == 2

        self.client.remove_giorno_irreperibilita(
            '123322',
            2020, 6, 16,
        )
        self.client.remove_giorno_irreperibilita(  # Rimuozione fallita
            '123322',
            2020, 11, 16,
        )

        user = self.client.users({'telegram': '123322'}).next()
        assert datetime.datetime(2020, 6, 16) not in user['irreperibilita']
        assert datetime.datetime(2021, 6, 16) in user['irreperibilita']
        assert len(user['irreperibilita']) == 1
