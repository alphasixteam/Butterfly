"""
File: run.py
Data creazione: 2019-03-29

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
Creatore: Samuele Gardin, samuelegardin1997@gmail.com
Autori:

"""

from pathlib import Path
import json
import os

from consumer.telegram.consumer import TelegramConsumer
from consumer.creator import KafkaConsumerCreator


_config_path = Path(__file__).parents[2] / 'config' / 'config.json'


def _open_kafka_configs(path: Path = _config_path):
    """Apre il file di configurazione per Kafka.
    """

    with open(path) as file:
        configs = json.load(file)

    if(os.environ['KAFKA_IP'] and os.environ['KAFKA_PORT']):
        configs['kafka']['bootstrap_servers'] = os.environ['KAFKA_IP'] + ':' + os.environ['KAFKA_PORT']

    configs = configs['kafka']
    timeout = 'consumer_timeout_ms'
    if (timeout in configs
            and configs[timeout] == 'inf'):
        configs[timeout] = float('inf')
    return configs


def main():
    # Ottiene le configurazioni da Kafka
    configs = _open_kafka_configs()
    topic = 'telegram'

    # Istanzia il KafkaConsumer
    try:
        kafka = KafkaConsumerCreator().create(configs, topic)
    except kafka.errors.KafkaConfigurationError as e:
        exit(-1)

    # Istanzia il TelegramConsumer
    consumer = TelegramConsumer(kafka)

    try:
        consumer.listen()  # Ascolta i messaggi
    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()  # Chiude la connessione


if __name__ == '__main__':
    main()
