"""
File: ClientGP.py
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
Creatore: Laura Cameran, lauracameran@gmail.com
Autori:
    Nicola Carlesso, nicolacarlesso@outlook.it
"""

from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaTimeoutError

from gestore_personale.creator import KafkaConsumerCreator
from gestore_personale.creator import KafkaProducerCreator
from gestore_personale.concrete_processor import GitlabProcessor
from gestore_personale.concrete_processor import RedmineProcessor
from mongo_db.facade import MongoFacade
from mongo_db.singleton import MongoSingleton
from mongo_db.users import MongoUsers
from mongo_db.projects import MongoProjects


class ClientGP():
    """
        Client del gestore personale. Interagisce con kafka
    """

    def __init__(
            self,
            consumer: KafkaConsumer,
            producer: KafkaProducer,
            mongo: MongoFacade
    ):
        assert isinstance(producer, KafkaProducer)
        assert isinstance(consumer, KafkaConsumer)
        self._consumer = consumer
        self._producer = producer
        self._mongo = mongo

    def read_messages(self):
        """
           Metodo in ascolto delle code di kafka
        """
        for topic in self._consumer.subscription():
            print(f'- {topic}')
        print()
        # Per ogni messaggio ricevuta da Kafka, processiamolo
        # in modo da poterlo reinserirlo in Telegram o Email
        for message in self._consumer:
            self.process(message.value)

    def process(self, message: dict):
        """
            Processa i messaggi in entrata
        """
        tecnology = message['app']
        if tecnology == 'gitlab':
            processore_messaggio = GitlabProcessor(
                message, self._mongo
            )
        elif tecnology == 'redmine':
            processore_messaggio = RedmineProcessor(
                message, self._mongo
            )

        # controllo se è il primo messaggio di un progetto
        # processore_messaggio = Processor(message, self._mongo.instantiate())
        mappa_contatto_messaggio = processore_messaggio.prepare_message()
        if (mappa_contatto_messaggio['telegram'] == []
                and mappa_contatto_messaggio['email'] == []):
            self.generate_lost_message(message)
        else:
            self.send_all(mappa_contatto_messaggio, message)

    def send_all(self, map_message_contact: dict, message: dict):
        """
            app_ricevente sarà telegram o email (chiave,valore)
        """
        for app_ricevente, contact_list in map_message_contact.items():
            for contact in contact_list:
                try:
                    message['receiver'] = contact
                    # Inserisce il messaggio in Kafka,
                    # serializzato in formato JSON
                    self._producer.send(
                        app_ricevente, message
                    )
                    self._producer.flush(10)  # Attesa 10 secondi
                # Se non riesce a mandare il messaggio in 10 secondi
                except KafkaTimeoutError:
                    print('Impossibile inviare il messaggio\n')

    def generate_lost_message(self, message: dict):
        """
            Produce nella coda `lostmessages` il messaggio che non ha
            destinatari.
        """
        self._producer.send(
            'lostmessages',
            message,
        )

    def close(self):
        """
            Chiude la connessione con Producer e Consumer associati.
        """
        self._producer.close()
        self._consumer.close()


if __name__ == "__main__":
    kafka_consumer = KafkaConsumerCreator().create()
    kafka_producer = KafkaProducerCreator().create()
    mongo = MongoFacade(
        MongoUsers(MongoSingleton.instance()),
        MongoProjects(MongoSingleton.instance()),
    )
    client = ClientGP(kafka_consumer, kafka_producer, mongo)
    try:
        client.read_messages()
    except KeyboardInterrupt:
        pass
    finally:
        client.close()
