"""
File: db_controller_test.py
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

Versione: 0.2.1
Creatore: Timoty Granziero, timoty.granziero@gmail.com
"""

import unittest
from mongo_db.db_controller import DBConnection, DBController, pymongo


class TestDBController(unittest.TestCase):

    # Chiamato all'inizio
    @classmethod
    def setUpClass(cls):  # NOSONAR
        cls.client = DBConnection('butterfly_test')

        # Droppa il database `butterfly_test`
        cls.client._client.drop_database('butterfly_test')

        # Copia il db `butterfly` in `butterfly_test`
        cls.client._client.admin.command(
            'copydb',
            fromdb='butterfly',
            todb='butterfly_test'
        )

        cls.controller = DBController(cls.client, False)

    # Chiamato alla fine
    @classmethod
    def tearDownClass(cls):  # NOSONAR
        cls.client.close()

    def test_db_instances(self):
        collection = self.client.db.users
        # Cerca un documento qualsiasi
        self.assertIsNotNone(collection.find_one({}))

        self.assertIsNotNone(collection.find_one({'_id': 1}))
        self.assertIsNotNone(collection.find_one({'_id': 2}))
        self.assertIsNotNone(collection.find_one({'_id': 3}))

        timoty = collection.find_one({'name': 'Timoty'})
        self.assertIsNotNone(timoty)
        self.assertEqual(timoty['name'], 'Timoty')
        self.assertEqual(timoty['surname'], 'Granziero')
        self.assertEqual(timoty['sostituto'], 2)
        self.assertEqual(timoty['telegram'], '@user1')
        self.assertEqual(timoty['preferenza'], 'telegram')
        self.assertIsNone(timoty['email'])
        self.assertIn('mongodb', timoty['keywords'])
        self.assertIn('python', timoty['keywords'])
        self.assertIn('test', timoty['keywords'])

        simone = collection.find_one({
            'surname': 'Granziero',  # La virgola sottointende AND
            'topics': {
                '$size': 2  # Matcha array topics di dimensione 2
            }}
        )
        self.assertIsNotNone(simone)
        self.assertEqual(simone['name'], 'Simone')
        self.assertEqual(simone['surname'], 'Granziero')
        self.assertEqual(simone['sostituto'], 1)
        self.assertEqual(simone['telegram'], '@user2')
        self.assertEqual(simone['email'], 'simone.granziero@gmail.com')
        self.assertEqual(simone['preferenza'], 'email')
        self.assertGreaterEqual(len(simone['irreperibilità']), 3)
        self.assertGreaterEqual(len(simone['keywords']), 2)
        self.assertIn('2019-07-17', simone['irreperibilità'])
        self.assertEqual(simone['sostituto'], 1)

        mattia = collection.find_one({
            'name': 'Mattia',
            'surname': 'Ridolfi',
        })

        self.assertIsNotNone(mattia)
        self.assertEqual(mattia['name'], 'Mattia')
        self.assertEqual(mattia['surname'], 'Ridolfi')
        self.assertEqual(mattia['sostituto'], 1)
        self.assertEqual(mattia['preferenza'], 'email')
        self.assertEqual(mattia['email'], 'mattia.ridolfi@gmail.com')
        self.assertIsNone(mattia['telegram'])
        self.assertGreaterEqual(len(mattia['keywords']), 2)
        self.assertGreaterEqual(len(mattia['topics']), 0)

        collection = self.client.db.projects

        project1 = collection.find_one({
            'url': 'http://localhost/redmine/project-1'
        })

        self.assertIsNotNone(project1)
        self.assertEqual(project1['name'], 'Project-1')
        self.assertEqual(project1['app'], 'redmine')

        project2 = collection.find_one({
            'url': 'http://localhost/gitlab/gitlab-2'
        })

        self.assertIsNotNone(project2)
        self.assertEqual(project2['name'], 'Gitlab-2')
        self.assertEqual(project2['app'], 'gitlab')

        collection = self.client.db.topics

        topic1 = collection.find_one({
            'label': 'bug',
            'project': 'http://localhost/redmine/project-1',
        })

        self.assertIsNotNone(topic1)

        topic2 = collection.find_one({
            'label': 'enhancement',
        })

        self.assertIsNotNone(topic2)

    # @unittest.skip('debugging')
    def test_insert_delete_user(self):
        with self.subTest('Insert user'):
            collection = self.client.db.users
            documents_count = self.client.db.users.count_documents({})

            result = self.controller.insert_user(
                name='Giovanni',
                surname='Masala',
                telegram='@giovanni',
                topics=[4],
                keywords=['rotella', 'java'],
                preferenza='telegram',
                sostituto='@user1'
            )

            self.assertIsNotNone(result)
            self.assertIsNotNone(
                collection.find_one({
                    'telegram': '@giovanni'
                })
            )
            self.assertEqual(
                documents_count+1,
                self.client.db.users.count_documents({}),
            )

        with self.subTest('Insert user raises'):

            # Campo inesistente
            self.assertRaises(
                AssertionError,
                self.controller.insert_user,
                _id=10123,
                name='Giovannii',
                surname='Masalaa',
                telegram='@giovannino',
                topics=[4],
                keywords=['rotella', 'java'],
                preferenza='telegram',
                sostituto='@user1',
                namee='kappa',
            )

            # Campi telegram e email entrambi assenti
            self.assertRaises(
                AssertionError,
                self.controller.insert_user,
                _id=10124,
                name='Giovannii',
                surname='Masalaa',
                topics=[4],
                keywords=['rotella', 'java'],
            )

            # Telegram già presente
            self.assertRaises(
                AssertionError,
                self.controller.insert_user,
                _id=10123,
                name='Giovannii',
                surname='Masalaa',
                telegram='@user1',
                topics=[4],
                keywords=['rotella', 'java'],
                preferenza='telegram',
            )

            # Email già presente
            self.assertRaises(
                AssertionError,
                self.controller.insert_user,
                _id=10123,
                name='Giovannii',
                surname='Masalaa',
                email='mattia.ridolfi@gmail.com',
                topics=[4],
                keywords=['rotella', 'java'],
                preferenza='email',
            )

            # Preferenza non valida
            self.assertRaises(
                AssertionError,
                self.controller.insert_user,
                _id=10123,
                name='Giovannii',
                surname='Masalaa',
                email='mattia.ridolfi@gmail.com',
                topics=[4],
                keywords=['rotella', 'java'],
                preferenza='telegram',
            )

        with self.subTest('Delete user'):
            collection = self.client.db.users
            documents_count = self.client.db.users.count_documents({})

            result = self.controller.delete_one_user('@giovanni')

            self.assertIsNotNone(result)
            self.assertEqual(result.deleted_count, 1)
            self.assertIsNone(
                collection.find_one({
                    '_id': 10,
                })
            )
            self.assertEqual(
                documents_count,
                self.client.db.users.count_documents({})+1,
            )

            # Controlla un delete fallito
            documents_count = self.client.db.users.count_documents({})
            result = self.controller.delete_one_user('aaaaa')
            self.assertEqual(
                documents_count,
                self.client.db.users.count_documents({}),
            )

    def test_insert_delete_project(self):
        with self.subTest('Insert project'):
            collection = self.client.db.projects
            documents_count = self.client.db.projects.count_documents({})

            result = self.controller.insert_project({
                "url": "http://localhost/gitlab/project-10",
                "name": "Project-10",
                "app": "gitlab",
            })

            self.assertIsNotNone(result)
            self.assertIsNotNone(
                collection.find_one({
                    'name': 'Project-10',
                })
            )
            self.assertEqual(
                documents_count+1,
                self.client.db.projects.count_documents({}),
            )
            self.assertRaises(
                pymongo.errors.DuplicateKeyError,
                self.controller.insert_project,
                {
                    "url": "http://localhost/gitlab/project-10",
                    "name": "Project-10",
                    "app": "gitlab",
                }
            )

        with self.subTest('Delete project'):
            collection = self.client.db.projects
            documents_count = self.client.db.projects.count_documents({})

            result = self.controller.delete_one_project(
                'http://localhost/gitlab/project-10'
            )

            self.assertIsNotNone(result)
            self.assertEqual(result.deleted_count, 1)
            self.assertIsNone(
                collection.find_one({
                    'url': 'http://localhost/gitlab/project-10'
                })
            )
            self.assertEqual(
                documents_count,
                self.client.db.projects.count_documents({})+1,
            )

            # Controlla un delete fallito
            documents_count = self.client.db.projects.count_documents({})
            result = self.controller.delete_one_project('aaaaa')
            self.assertEqual(
                documents_count,
                self.client.db.projects.count_documents({}),
            )

    def test_insert_delete_topic(self):
        with self.subTest('Insert topic'):
            collection = self.client.db.topics
            documents_count = self.client.db.topics.count_documents({})
            result = self.controller.insert_topic(
                'wip',
                'http://localhost/gitlab/project-1',
            )

            self.assertIsNotNone(result)
            self.assertIsNotNone(
                collection.find_one({
                    'project': 'http://localhost/gitlab/project-1',
                })
            )
            self.assertEqual(
                documents_count+1,
                self.client.db.topics.count_documents({}),
            )

        with self.subTest('Delete topic'):
            collection = self.client.db.topics
            documents_count = self.client.db.topics.count_documents({})

            result = self.controller.delete_one_topic(
                'wip',
                'http://localhost/gitlab/project-1',
            )

            self.assertIsNotNone(result)
            self.assertEqual(result.deleted_count, 1)
            self.assertIsNone(
                collection.find_one({
                    'project': 'http://localhost/gitlab/project-1',
                    'label': 'wip',
                })
            )
            self.assertEqual(
                documents_count,
                self.client.db.topics.count_documents({})+1,
            )

            # Controlla un delete fallito
            documents_count = self.client.db.topics.count_documents({})
            result = self.controller.delete_one_topic('aaaaa', 'aaaaa')
            self.assertEqual(
                documents_count,
                self.client.db.topics.count_documents({}),
            )

    # @unittest.expectedFailure
    def test_collection(self):
        users = self.controller.collection('users')

        self.assertEqual(users.count_documents({}), 3)

        index = 0
        for value in users.find({}):
            with self.subTest(i=index):
                self.assertIsNotNone(value['name'])
                self.assertIsNotNone(value['surname'])

                if value['telegram'] is None:
                    self.assertIsNotNone(value['email'])
                else:
                    self.assertIsNotNone(value['telegram'])

                self.assertEqual(type(value['topics']), list)
                self.assertEqual(type(value['keywords']), list)
                self.assertEqual(type(value['irreperibilità']), list)
            index += 1

    def test_users(self):
        users = self.controller.users({
            'name': 'Simone',
            'surname': 'Granziero',
        })
        self.assertIsNotNone(users[0])

    def test_projects(self):
        projects = self.controller.projects({
            'app': 'redmine',
        })
        self.assertIsNotNone(projects[0])

    # @unittest.expectedFailure
    def test_keywords(self):
        keywords = self.controller.user_keywords('mattia.ridolfi@gmail.com')
        self.assertIn('CI', keywords)
        self.assertIn('jenkins', keywords)
        self.assertNotIn('mango', keywords)
        self.assertNotIn('ingranaggio', keywords)
        self.controller.add_keywords(
            'mattia.ridolfi@gmail.com',
            'mango',
            'ingranaggio',
            'CI',  # Questa non verrà aggiunta perchè doppia
        )
        keywords = self.controller.user_keywords('mattia.ridolfi@gmail.com')
        self.assertRaises(
            AssertionError,
            self.controller.add_keywords,
            'User20@'
        )
        self.assertIn('mango', keywords)
        self.assertIn('ingranaggio', keywords)

    def test_topics(self):
        t_id = '@user2'
        topics = self.controller.user_topics(t_id)

        count = self.controller.collection('users').count_documents({
            'telegram': t_id,
            'topics': {'$size': 2},
        })
        self.assertEqual(count, 1)
        for topic in topics:
            self.assertIsNotNone(topic['_id'])
            self.assertIsNotNone(topic['label'])
            self.assertIsNotNone(topic['project'])

        self.controller.add_user_topic(
            '@user2', 'wontfix', 'http://localhost/gitlab/gitlab-2'
        )

        self.controller.add_user_topic_from_id(
            '@user2', 0
        )

        count = self.controller.collection('users').count_documents({
            'telegram': t_id,
            'topics': {'$size': 4},
        })
        self.assertEqual(count, 1)

        self.assertRaises(
            AssertionError,
            self.controller.add_user_topic,
            '@user20',
            'wontfix',
            'http://localhost/gitlab/gitlab-2',
        )
        self.assertRaises(
            AssertionError,
            self.controller.add_user_topic,
            '@user2',
            'wontfixx',
            'http://localhost/gitlab/gitlab-2',
        )
        self.assertRaises(
            AssertionError,
            self.controller.add_user_topic,
            '@user2',
            'wontfix',
            'http:///localhost/gitlab/gitlab-2',
        )
        self.assertRaises(
            AssertionError,
            self.controller.user_topics,
            '@@teleegram'
        )

    def test_exists(self):
        with self.subTest('projects'):
            self.assertTrue(
                self.controller.project_exists(
                    'http://localhost/redmine/project-2'
                )
            )
            self.assertTrue(
                self.controller.project_exists(
                    'http://localhost/gitlab/gitlab-2'
                )
            )
            self.assertFalse(
                self.controller.project_exists(
                    'http://llocalhost/redmine/project-2'
                )
            )
            self.assertFalse(
                self.controller.project_exists(
                    'http://localhost/redmine/project-2/'
                )
            )

        with self.subTest('topics'):
            self.assertTrue(
                self.controller.topic_exists(
                    label='enhancement',
                    project='http://localhost/gitlab/gitlab-2',
                )
            )
            self.assertTrue(
                self.controller.topic_exists(
                    label='wontfix',
                    project='http://localhost/gitlab/gitlab-2',
                )
            )
            self.assertFalse(
                self.controller.topic_exists(
                    label='enhancementt',
                    project='http://localhost/gitlab/gitlab-2',
                )
            )
            self.assertFalse(
                self.controller.topic_exists(
                    label='wontfix',
                    project='http://localhostt/gitlab/gitlab-2',
                )
            )
            self.assertTrue(
                self.controller.topic_from_id_exists(
                    1,
                )
            )
            self.assertTrue(
                self.controller.topic_from_id_exists(
                    2,
                )
            )
            self.assertTrue(
                self.controller.topic_from_id_exists(
                    3,
                )
            )
            self.assertFalse(
                self.controller.topic_from_id_exists(
                    12123,
                )
            )
            self.assertFalse(
                self.controller.topic_from_id_exists(
                    12123134,
                )
            )

        with self.subTest('users'):
            self.assertTrue(
                self.controller.user_exists(
                    '@user2',
                )
            )
            self.assertTrue(
                self.controller.user_exists(
                    'mattia.ridolfi@gmail.com',
                )
            )
            self.assertFalse(
                self.controller.user_exists(
                    'mattia.ridolfi@gmail.it',
                )
            )
            self.assertFalse(
                self.controller.user_exists(
                    'banana',
                )
            )

    # @unittest.skip('debug')
    def test_update_preference(self):

        with self.subTest('Inserimento user'):
            documents_count = self.client.db.users.count_documents({})
            collection = self.client.db.users

            # Inserimento nuovo utente per evitare data races
            result = self.controller.insert_user(
                _id=105,
                name='Giovanni',
                surname='Mastrota',
                email='revolver@hotmail.it',
                telegram='@giovannimastrota',
                topics=[
                    4,
                    5
                ],
                keywords=[
                    'gear',
                    'rotella',
                    'java',
                ],
                preferenza='telegram',
                sostituto='mattia.ridolfi@gmail.com',
            )

            self.assertIsNotNone(result)
            self.assertIsNotNone(
                collection.find_one({
                    '_id': 105,
                })
            )
            self.assertEqual(
                documents_count+1,
                self.client.db.users.count_documents({}),
            )
            count = self.controller.collection('users').count_documents({
                'email': 'revolver@hotmail.it',
                "telegram": "@giovannimastrota",
                'preferenza': 'telegram',
            })
            self.assertEqual(count, 1)

        with self.subTest('Update preference'):
            self.controller.update_user_preference(
                '@giovannimastrota', 'email')

            self.assertRaises(
                AssertionError,
                self.controller.update_user_preference,
                '@user22',
                'telegram'
            )
            self.assertRaises(
                AssertionError,
                self.controller.update_user_preference,
                '@user2',
                'telegramm'
            )
            self.assertRaises(  # Preference su campo non None
                AssertionError,
                self.controller.update_user_preference,
                'mattia.ridolfi@gmail.com',
                'telegram'
            )
            count = self.controller.collection('users').count_documents({
                'email': 'revolver@hotmail.it',
                "telegram": "@giovannimastrota",
                'preferenza': 'email',
            })
            self.assertEqual(count, 1)

    def test_user_has_telegram(self):
        self.assertTrue(
            self.controller.user_has_telegram('@user2')
        )
        self.assertFalse(
            self.controller.user_has_telegram('mattia.ridolfi@gmail.com')
        )
        self.assertRaises(
            AssertionError,
            self.controller.user_has_telegram,
            'aaaaaaaa'
        )

    def test_user_has_email(self):
        self.assertTrue(
            self.controller.user_has_email('mattia.ridolfi@gmail.com')
        )
        self.assertFalse(
            self.controller.user_has_email('@user1')
        )
        self.assertRaises(
            AssertionError,
            self.controller.user_has_email,
            'aaaaaaaa'
        )

    # @unittest.skip('debugging')
    def test_update_user_data(self):

        with self.subTest('Insert user'):
            collection = self.client.db.users
            documents_count = self.client.db.users.count_documents({})

            result = self.controller.insert_user(
                _id=939,
                name='Mattia',
                surname='Masala',
                email=None,
                telegram='@rodo',
                topics=[
                    1,
                    2,
                    4
                ],
                keywords=[
                    'rotella',
                    'java',
                ],
                preferenza='telegram',
                sostituto='@user2',
            )

            result = self.controller.insert_user(
                _id=940,
                name='Michele',
                surname='Rapanello',
                email='michele.rapanello@hotmail.it',
                telegram=None,
                topics=[
                    1,
                    5,
                    4
                ],
                keywords=[
                    'python',
                    'java',
                    'crudo'
                ],
                preferenza='email',
                sostituto='@rodo',
            )

            self.assertIsNotNone(result)
            self.assertIsNotNone(
                collection.find_one({
                    '_id': 939,
                })
            )
            self.assertEqual(
                documents_count+2,
                self.client.db.users.count_documents({}),
            )

        with self.subTest('Update Telegram'):

            self.controller.update_user_telegram('@rodo', '@sancrispino')

            self.assertRaises(
                AssertionError,
                self.controller.update_user_telegram,
                '@rodo',
                '@reverendo',
            )
            self.assertRaises(
                AssertionError,
                self.controller.update_user_telegram,
                '@reverendo',
                '@user2',
            )
            self.assertTrue(self.controller.user_exists('@sancrispino'))
            self.assertFalse(self.controller.user_exists('@rodo'))

        with self.subTest('Update Email'):
            self.controller.update_user_email(
                'michele.rapanello@hotmail.it',
                'ccc@gmail.com',
            )
            self.assertRaises(
                AssertionError,
                self.controller.update_user_email,
                'michele.rapanello@hotmail.it',
                'aaaaa@cc.gmail.com',
            )
            self.assertRaises(
                AssertionError,
                self.controller.update_user_email,
                '@user2',
                'ccc@gmail.com'
            )
            self.assertTrue(self.controller.user_exists('ccc@gmail.com'))
            self.assertFalse(self.controller.user_exists(
                'michele.rapanello@hotmail.it'))

        with self.subTest('Update name'):
            # self.user
            pre = self.controller.user('ccc@gmail.com')
            self.assertEqual(pre['name'], 'Michele')
            self.controller.update_user_name(
                'ccc@gmail.com',
                'Matteo'
            )
            post = self.controller.user('ccc@gmail.com')
            self.assertEqual(post['name'], 'Matteo')
            self.assertRaises(
                AssertionError,
                self.controller.update_user_name,
                '@user22',
                'a',
            )

        with self.subTest('Update surname'):
            pre = self.controller.user('ccc@gmail.com')
            self.assertEqual(pre['surname'], 'Rapanello')
            self.controller.update_user_surname(
                'ccc@gmail.com',
                'Morgana'
            )
            post = self.controller.user('ccc@gmail.com')
            self.assertEqual(post['surname'], 'Morgana')
            self.assertRaises(
                AssertionError,
                self.controller.update_user_surname,
                '@user22',
                'a'
            )

        with self.subTest('Update sostituto'):
            pre = self.controller.user('ccc@gmail.com')
            self.assertEqual(pre['sostituto'], 939)
            self.controller.update_user_sostituto(
                'ccc@gmail.com',
                '@user1',
            )
            post = self.controller.user('ccc@gmail.com')
            self.assertEqual(post['sostituto'], 1)

    def test_user(self):
        obj = self.controller.user('@user1')
        self.assertEqual(obj['name'], 'Timoty')
        self.assertRaises(
            AssertionError,
            self.controller.user,
            'abcsd'
        )


# Funzione chiamata solo con runner.run(...)
# Scommentare le righe:
# runner = unittest.TextTestRunner()
# runner.run(suite())
# E commentare unittest.main() per customizzare
# i test da lanciare
def suite():
    suite = unittest.TestSuite()

    suite.addTest(TestDBController('test_db_instances'))

    suite.addTest(TestDBController('test_insert_user'))
    suite.addTest(TestDBController('test_insert_project'))
    suite.addTest(TestDBController('test_insert_topic'))

    suite.addTest(TestDBController('test_delete_user'))
    suite.addTest(TestDBController('test_delete_topic'))
    suite.addTest(TestDBController('test_delete_project'))

    return suite


if __name__ == '__main__':
    unittest.main()

    # runner = unittest.TextTestRunner()
    # runner.run(suite())
