"""
File: Consumer.py
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


from abc import ABC, abstractmethod
import json

from kafka import KafkaConsumer


class Consumer(ABC):
    """Interfaccia Consumer"""

    def __init__(self, consumer: KafkaConsumer):

        self._consumer = consumer

    def prelisten_hook(self):
        """Metodo ridefinibile dalle sotto classi per effettuare
        operazioni prima dell'avvio dell'ascolto dei messaggi.
        """

    def topics(self):
        """Restituisce i topic a cui il Consumer è iscritto.
        """
        return self._consumer.subscription()

    def listen(self):
        """Ascolta i messaggi provenienti dai Topic a cui il
        consumer è abbonato.

        Precondizione: i messaggi salvati nel broker devono essere
        in formato JSON, e devono contenere dei campi specifici
        definiti in nel modulo webhook
        """

        print('Listening to messages from topic:')
        for topic in self.topics():
            print(f'- {topic}')
        print()

        self.prelisten_hook()  # Hook!

        # Si mette in ascolto dei messsaggi dal Broker
        for message in self._consumer:

            value = message.value
            try:
                # receiver, value = self.format(value)

                # Invia il messaggio al destinatario finale
                self.send(value['receiver'], value)

            except json.decoder.JSONDecodeError:
                print(f'\n-----\n"{value}" '
                      'non è in formato JSON\n-----\n')
            except Exception as e:
                print('Errore nella formattazione del messaggio finale')
                print(repr(e))

    @abstractmethod
    def send(self, receiver: str, msg: dict) -> bool:
        """Invia il messaggio all'utente finale."""

    def close(self):
        """Chiude la connessione del Consumer"""
        self._consumer.close()
