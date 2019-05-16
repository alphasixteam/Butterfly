"""
File: test_ClientGP.py
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

from kafka import KafkaProducer, KafkaConsumer
from mongo_db.facade import MongoFacade
from gestore_personale.client import ClientGP
from gestore_personale.processor import Processor

# Kafka producer mock
KAFKA_PRODUCER = MagicMock()
KAFKA_PRODUCER.__class__ = KafkaProducer

# Kafka consumer mock
KAFKA_CONSUMER = MagicMock()
KAFKA_CONSUMER.__class__ = KafkaConsumer

# Mongo mock
MONGO = MagicMock()
MONGO.__class__ = MongoFacade

# Processor = Mock()

client = ClientGP(KAFKA_CONSUMER, KAFKA_PRODUCER, MONGO)


message = {
    'app': 'gitlab',
    'object_kind': 'issue-note',
    'title': 'Issue numero quindici',
    'description': 'Questa è una stuqwerpida descrizione',
    'project_id': 'http/sdfbwjfenw',
    'labels': [],
}

message2 = {
    'app': 'redmine',
    'object_kind': 'issue',
    'title': 'Issue numero quinewrtdici',
    'description': 'Questa è una wqer descrizione',
    'project_id': 'http/itttt',  # diventa 'project_id'
    'action': 'opened',
    'labels': ['fix']
}

map_message_contacts = {
    'email': ['2@gmail.com', '8@gmail.com'],
    'telegram': ['2', '3']
}


KAFKA_CONSUMER.__iter__ = MagicMock(return_value=iter([message, message2]))
# Processor.prepare_message.return_value = map_message_contacts
MONGO.instantiate.return_value = MagicMock()
# MONGO.instantiate.get_users_from_list_with_max_priority.__iter__ = Mock(
#     return_value=iter(1,2)
# )
# .return_value.__iter__.return_value =
MONGO.get_users_from_list_with_max_priority = MagicMock()
# MONGO.get_users_from_list_with_max_priority.__iter__.return_value = 'a'


@pytest.mark.skip()
def test_send_all():
    KAFKA_PRODUCER.send = MagicMock()

    client.send_all(map_message_contacts, message)

    KAFKA_PRODUCER.send.called
    KAFKA_PRODUCER.send.assert_called_with(
        'telegram',
        {'app': 'gitlab', 'object_kind': 'issue-note',
            'title': 'Issue numero quindici',
            'description': 'Questa è una stuqwerpida descrizione',
            'project_id': 'http/sdfbwjfenw', 'receiver': '3'})
    # KAFKA_PRODUCER.send.assert_called_with('email', {'app': 'gitlab', 'object_kind': 'note', 'title': 'Issue numero quindici', 'description': 'Questa è una stuqwerpida descrizione', 'project_id': 'http/sdfbwjfenw', 'receiver': '3'})

    # KAFKA_PRODUCER.send.assert_called_once()  # Deve dare false: 4


# TODO: rivedere
@pytest.mark.skip()
def test_process():
    client.send_all = MagicMock()
    # Processor = Mock()
    # Processor.prepare_message.return_value = map_message_contacts

    client.process(message)  # Metodo da testare

    client.send_all.assert_called_once()
    # client.send_all.assert_called_with(
    #     map_message_contacts, message
    # )


# Controlla che la chiamata a process effetivamente avvenga per i due messaggi
# @pytest.mark.skip()
def test_read_message():
    client.process = MagicMock()

    client.read_messages()  # Metodo da testare

    # Verifichiamo che venga chiamato 2 volte per i 2 messaggi
    client.process.assert_any_call(message)
    client.process.assert_any_call(message2)


@pytest.mark.skip()
@patch('gestore_personale.concrete_processor.GitlabProcessor')
def test_lost_message(processor):
    processor.mappa_contatto_messaggio = {'telegram': [], 'email': []}
    # client.process(message2)
    # client.generate_lost_message(message)
    client.generate_lost_message = MagicMock()
    client.process(message2)

    client.generate_lost_message.assert_called_once()
