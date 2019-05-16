"""
File: producer.py
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

from kafka import KafkaProducer
from kafka.errors import KafkaTimeoutError
from webhook.factory import WebhookFactory


class Producer(ABC):
    """Classe astratta Producer

    Attributes:
        `kafka_producer`: istanza di `KafkaProducer`
        `webhook_factory`: istanza di `WebhookFactory`
    """

    def __init__(
            self,
            kafka_producer: KafkaProducer,
            webhook_factory: WebhookFactory,
    ):
        assert isinstance(kafka_producer, KafkaProducer)
        assert isinstance(webhook_factory, WebhookFactory)

        self._webhook_factory = webhook_factory
        self._producer = kafka_producer

    def produce(self, whook: dict):
        """Produce il messaggio `whook` nel Topic designato del Broker"""
        webhook = self._webhook_factory.create_webhook(
            self.webhook_kind(whook)
        )
        # Parse del JSON associato al webhook ottenendo un oggetto Python
        webhook = webhook.parse(whook)
        try:
            # Inserisce il messaggio in Kafka, serializzato in formato JSON
            self._producer.send(webhook['app'], webhook)

            self._producer.flush(10)  # Attesa 10 secondi
        # Se non riesce a mandare il messaggio in 10 secondi
        except KafkaTimeoutError:
            print('Impossibile inviare il messaggio\n')

    @abstractmethod
    def webhook_kind(self, whook: dict):
        """Dato un `dict` con chiave `object_kind`, ne restituisce il valore.

        Parameters:

        `whook` - Webhook contenente campi specifici per il Topic.
        """

    def close(self):
        """Chiude la connessione con Kafka.
        """
        self._producer.close()
