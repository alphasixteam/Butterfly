"""
File: server.py
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

from pprint import pformat

from flask import Flask
from flask import request

from producer.producer import Producer


class FlaskServer:
    """Implementa `Server`.
    Avvia il server `Flask` che resta in ascolto degli webhook in base a
    come è configurato.
    """

    def __init__(self, flask: Flask, producer: Producer, topic: str):
        self._app = flask
        self._producer = producer
        self._topic = topic
        self._app.add_url_rule(
            '/',
            view_func=self._webhook_handler,
            methods=['POST']
        )

    def _webhook_handler(self) -> (str, int):
        """Processa il webhook e verifica se è malformato.

        Returns:

        `200` - Il webhook è stato inoltrato con successo.\n
        `400` - La richiesta non è di tipo `application/json`\n
        `401` - Il `Producer` non è stato in grado di inviare il
            messaggio
        """
        if request.headers['Content-Type'] == 'application/json':
            webhook = request.get_json()

            try:
                self._producer.produce(webhook)
            except KeyError:
                return 'Messaggio malformato', 402
            except NameError:
                # Errore messaggio malformato
                return 'Tipo di messaggio non riconosciuto', 401
            return 'Ok', 200  # Ok
        return '', 400  # Errore, tipo di richiesta non adatta

    def run(self, configs: dict):
        """Avvia il `FlaskServer` con le configurazioni nel file
        contenuto in `config_path`.

        Parameters:

        `configs` - dict contenente le configurazioni necessarie all'avvio
            del server.
        """

        self._app.run(
            host=configs[self._topic]['ip'],
            port=configs[self._topic]['port']
        )
