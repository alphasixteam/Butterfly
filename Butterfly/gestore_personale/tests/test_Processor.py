"""
File: test_Processor.py
Data creazione: 2019-03-13

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
Creatore: Ciprian Voinea, ciprianv96@hotmail.it
Autori:
    Nicola Carlesso, nicolacarlesso@outlook.it
"""


from unittest.mock import Mock, patch, MagicMock
import pytest
import unittest

from gestore_personale.processor import Processor


mongofacade = Mock()
message = {
    'app': 'redmine',
    'object_kind': 'issue',
    'title': 'Issue numero quindici',
    'description': 'Questa è una vbj descrizione',
    'project_url': 'http/sdfbwjfenw',  # diventa 'project_id'
    'action': 'updated',
    'label': 'bug'
}
p = Processor(message, mongofacade)
mongofacade.get_project_by_url.return_value = True
# mongofacade.insert_project.return_value =
mongofacade.get_users_available.return_value = ['1', '2', '8', '3', '4']
mongofacade.get_users_max_priority.return_value = ['2', '8', '3']


# def side_effect(value: list):
#     return value.append('GDM')

# mongofacade.get_users_from_list_with_max_priority.return_value = MagicMock(
#     side_effect=side_effect
# )
mongofacade.get_users_from_list_with_max_priority.return_value = ['111', '99']

p._filter_users_by_topic = Mock()
p._filter_users_by_topic.return_value = []


def side_effect(value):  # Mock per far finta di avere il telegram utente
    return value


def email_effect(value):  # Mock per avere la mail di quell'utente
    return value + '@gmail.com'


mongofacade.get_user_telegram = MagicMock(side_effect=side_effect)
mongofacade.get_user_email = MagicMock(side_effect=email_effect)


def test_prepare_message():
    msg = p.prepare_message()
    assert msg is not False
    # assertIsInstance(p, dict) # Non lo prende, non capisco perchè
    assert isinstance(msg, dict) is True
    assert msg == {
        'email': ['2@gmail.com', '8@gmail.com', '3@gmail.com'],
        'telegram': ['2', '8', '3']
    }

    # for k, vi in msg.items():
    #     for x in k:
    #         assert k == '2' or k == '8' or k =='1'


def test_check_project():
    url = p._check_project()
    assert url == 'http/sdfbwjfenw'


def test_get_involved_users():
    lista = p.get_involved_users(message['project_url'])
    assert lista == ['1', '2', '8', '3', '4']


def test_select_users_more_interested():
    lista = p.select_users_more_interested(message['project_url'])
    assert lista == ['2', '8', '3']


def test_filter_users_with_max_priority():
    users = ['111', '99', '54', '2']
    lista = p.filter_users_with_max_priority(users)
    assert lista == ['111', '99']


def test_get_telegram_contacts():
    users = ['111', '99', '54', '2']
    lista = p.get_telegram_contacts(users)
    assert lista is not []
    assert lista == ['111', '99', '54', '2']


def test_get_email_contacts():
    # Tutti i contatti hanno la mail
    users = ['32', '17', '14']
    lista = p.get_email_contacts(users)
    assert lista == ['32@gmail.com', '17@gmail.com', '14@gmail.com']

    # Ora nessuno di questi contatti ha la mail
    del mongofacade.get_user_email
    mongofacade.get_user_email = Mock()
    mongofacade.get_user_email.return_value = None
    li = p.get_email_contacts(users)
    assert li == []
