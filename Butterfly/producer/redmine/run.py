"""
File: run.py
Data creazione: 2019-02-19

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

Versione: 0.2.0
Creatore: Timoty Granziero, timoty.granziero@gmail.com
Autori:
    Laura Cameran, lauracameran@gmail.com
    Samuele Gardin, samuelegardin@gmail.com
"""

from pathlib import Path
import json
import os

from flask import Flask

from producer.server import FlaskServer
from producer.creator import KafkaProducerCreator
from producer.redmine.producer import RedmineProducer
from webhook.redmine.factory import RedmineWebhookFactory

_CONFIG_PATH = Path(__file__).parents[2] / 'config' / 'config.json'

def _open_configs(path: Path):
    with open(path) as file:
        config = json.load(file)

    if (os.environ['KAFKA_IP'] and os.environ['KAFKA_PORT']):
        config['kafka']['bootstrap_servers'] = os.environ['KAFKA_IP'] + ':' + os.environ['KAFKA_PORT']

    return config


def main():
    configs = _open_configs(_CONFIG_PATH)
    kafka = KafkaProducerCreator().create(configs['kafka'])
    producer = RedmineProducer(kafka, RedmineWebhookFactory())

    server = FlaskServer(Flask(__name__), producer, 'redmine')
    server.run(configs)


if __name__ == '__main__':
    main()
