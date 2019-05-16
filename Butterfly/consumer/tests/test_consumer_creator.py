"""
File: test_consumer_creator.py
Data creazione: 2019-02-13

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
Creatore: Timoty Granziero, timoty.granziero@gmail.com
Autori:
    Samuele Gardin, samuelegardin1997@gmail.com
"""

from unittest.mock import patch

from consumer.creator import KafkaConsumerCreator, KafkaConsumer

@patch('consumer.creator.json.loads')
@patch('consumer.creator.kafka.errors.NoBrokersAvailable', autospec=True)
@patch('consumer.creator.KafkaConsumer', autospec=True)
def test_create(
        kafka,
        errors,
        json_loads,
):

    creator = KafkaConsumerCreator()
    kafka_consumer = creator.create({}, 'topic')

    kafka.assert_called_once()
    assert isinstance(kafka_consumer, KafkaConsumer)
