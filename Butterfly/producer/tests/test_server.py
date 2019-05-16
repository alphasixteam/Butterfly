"""
File: test_server.py
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
    Ciprian Voinea, ciprianv96@hotmail.com
"""

from unittest.mock import MagicMock, patch

import pytest

import producer
from producer.server import FlaskServer


def test_server():
    flask_mock = MagicMock()
    producer_mock = MagicMock()

    server = FlaskServer(flask_mock, producer_mock, 'gitlab')
    server.run(MagicMock())

    flask_mock.run.assert_called_once()


@patch('producer.server.request')
def test_webhook_handler(request_mock):
    request_mock.headers = {}
    request_mock.headers['Content-Type'] = 'application/json'
    request_mock.get_json.return_value = {}

    producer_mock = MagicMock()
    producer_mock.produce.return_value = None

    server = FlaskServer(MagicMock(), producer_mock, 'gitlab')
    value = server._webhook_handler()
    assert value == ('Ok', 200)

    producer_mock.produce.side_effect = KeyError()
    value = server._webhook_handler()
    assert value == ('Messaggio malformato', 402)

    request_mock.headers['Content-Type'] = 'xml'
    value = server._webhook_handler()
    assert value == ('', 400)
