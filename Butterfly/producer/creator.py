"""
File: creator.py
Data creazione: 2019-02-12

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

Versione: 0.4.0
Creatore: Timoty Granziero, timoty.granziero@gmail.com
"""

from abc import ABC, abstractmethod
import json

from kafka import KafkaProducer
import kafka.errors

from producer.producer import Producer


class ProducerCreator(ABC):
    """Interfaccia `ProducerCreator`. Un `ProducerCreator` ha il
    compito di inizializzare un `KafkaProducer` concreto.
    """

    @abstractmethod
    def create(self, configs: dict) -> KafkaProducer:
        """Restituisce un'istanza concreta di `KafkaProducer`, inizializzando un

        Parameters:

        `configs`: dizionario contenente le configurazioni per il
        `KafkaProducer`.
        """


class KafkaProducerCreator(ProducerCreator):

    def create(self, configs: dict) -> Producer:
        """Restituisce un'istanza concreta di `KafkaProducer`, inizializzando un

        Parameters:

        `configs`: dizionario contenente le configurazioni per il
        `KafkaProducer`.
        """

        notify = False
        while True:  # Attende una connessione con il Broker
            try:
                kafka_producer = KafkaProducer(
                    # Serializza l'oggetto Python in un
                    # oggetto JSON, codifica UTF-8
                    value_serializer=lambda m: json.dumps(m).encode('utf-8'),
                    **configs
                )
                break
            except kafka.errors.NoBrokersAvailable:
                if not notify:
                    notify = True

            except KeyboardInterrupt:
                exit(1)

        return kafka_producer
