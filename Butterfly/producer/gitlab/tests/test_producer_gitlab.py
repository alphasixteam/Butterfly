"""
File: test_producer_gitlab.py
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


from unittest.mock import Mock

import pytest
from kafka import KafkaProducer

from producer.gitlab.producer import GitlabProducer
from webhook.factory import WebhookFactory


# Kafka producer mock
KAFKA_PRODUCER = Mock()
KAFKA_PRODUCER.__class__ = KafkaProducer

# Webhook mock
WEBHOOK_MOCK = Mock()
WEBHOOK_MOCK.parse.return_value = {'app': 'gitlab'}

# Factory mock
FACTORY = Mock()
FACTORY.__class__ = WebhookFactory
FACTORY.create_webhook.return_value = WEBHOOK_MOCK


def test_webhook_kind():
    producer = GitlabProducer(
        KAFKA_PRODUCER,
        FACTORY,
    )
    value = producer.webhook_kind({'object_kind': 'issue'})
    assert value == 'issue'


def test_produce():
    producer = GitlabProducer(
        KAFKA_PRODUCER,
        FACTORY
    )
    producer.produce({'object_kind': 'issue'})


# @pytest.mark.skip(reason="no way of currently testing this")
def test_constructor():
    with pytest.raises(AssertionError):
        GitlabProducer(FACTORY, FACTORY)

    with pytest.raises(AssertionError):
        GitlabProducer(KAFKA_PRODUCER, KAFKA_PRODUCER)
