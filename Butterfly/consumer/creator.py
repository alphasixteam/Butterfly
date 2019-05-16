"""
File: ConsumerCreator.py
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
Creatore: Timoty Granziero, timoty.granziero@gmail.com
Autori:

"""
from abc import ABC, abstractmethod
import json

from kafka import KafkaConsumer
import kafka.errors

# from consumer.consumer import Consumer


class ConsumerCreator(ABC):
    @abstractmethod
    def create(self, configs: dict, topic: str) -> KafkaConsumer:
        pass


class KafkaConsumerCreator(ConsumerCreator):

    def create(self, configs: dict, topic: str) -> KafkaConsumer:
        # Converte stringa 'inf' nel relativo float

        notify = False
        while True:  # Attende una connessione con il Broker
            try:
                kafka_consumer = KafkaConsumer(
                    topic,  # Chiamata polimorfa
                    # Deserializza i messaggi dal formato JSON a oggetti Python
                    value_deserializer=(
                        (lambda m: json.loads(m.decode('utf-8')))
                    ),
                    **configs,
                )
                break
            except kafka.errors.NoBrokersAvailable:
                if not notify:
                    notify = True

            except KeyboardInterrupt:
                print(' Closing Consumer ...')
                # exit(1)

        return kafka_consumer
