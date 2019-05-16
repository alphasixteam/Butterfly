"""
File: test_creator.py
Data creazione: 2019-02-20

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

Versione: 0.1.1
Creatore: Timoty Granziero, timoty.granziero@gmail.com
"""

from unittest.mock import patch, MagicMock


from producer.creator import KafkaProducerCreator
import producer


@patch('producer.creator.KafkaProducer')
def test_producer_creator(kafka_mock):
    producer.creator.KafkaProducer()
    assert kafka_mock is producer.creator.KafkaProducer

    kafka_mock.return_value = MagicMock()

    creator = KafkaProducerCreator()
    creator.create({'bootstrap_servers': 'localhost'})

    assert kafka_mock.assert_called
    assert kafka_mock.assert_called
