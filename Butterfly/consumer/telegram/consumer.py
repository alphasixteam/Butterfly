"""
File: cnsumer.py
Data creazione: 2019-02-18

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

import json
from pathlib import Path

from kafka import KafkaConsumer
import requests

from consumer.consumer import Consumer


class TelegramConsumer(Consumer):

    _bold_open = '<b>'
    _bold_close = '</b>'
    _code_open = '<code>'
    _code_close = '</code>'

    """Implementa Consumer"""
    _CONFIG_PATH = Path(__file__).parents[2] / 'config' / 'config.json'

    def __init__(self, consumer: KafkaConsumer):
        super(TelegramConsumer, self).__init__(consumer)

        with open(self._CONFIG_PATH) as file:
            configs = json.load(file)
        self._token = configs['telegram']['token_bot']

    def send(self, receiver: str, msg: dict) -> bool:
        """Manda il messaggio finale, tramite il bot,
        all'utente finale.
        """

        # Richiesta POST per l'invio del messaggio finale
        # via Telegram API
        response = requests.post(
            'https://api.telegram.org/'
            f'bot{self._token}'
            '/sendMessage',
            data={
                'chat_id': receiver,
                'text': self.format(msg),
                'parse_mode': 'html',
            })
        if response.ok:
            chat = response.json()["result"]["chat"]
            return True
        return False

    @classmethod
    def format(cls, msg: dict) -> str:
        """Restituisce una stringa con una formattazione migliore da un
        oggetto JSON (Webhook).

        Arguments:
        msg -- JSON object

        Formato: HTML
        <b>bold text</b>
        <i>italic text</i>
        [inline URL](http://www.example.com/)
        [inline mention of a user](tg://user?id=123456789)
        <code>inline fixed-width code</code>
        <pre>block_language
        pre-formatted fixed-width code block
        </pre>
        """

        # Queste chiamate vanno bene sia per i webhook di rd che per gt

        res = ''

        if msg['object_kind'] == 'issue':
            return cls._format_issue(msg)

        elif msg['object_kind'] == 'push':
            return cls._format_push(msg)

        elif msg['object_kind'] == 'issue-note':
            res += f'È stata commentata una issue '

        elif msg['object_kind'] == 'commit-note':
            res += f'È stato commentato un commit '

        else:
            raise KeyError

        res += ''.join([
            f'nel progetto {cls._bold_open}{msg["project_name"]}{cls._bold_close} ',
            f' su {msg["app"].capitalize()}\n',
            # f'\n\n{cls._bold_open}Informazioni:{cls._bold_close} '
            f'\n - {cls._bold_open}Autore:{cls._bold_close} {msg["author"]}'
            f'\n - {cls._bold_open}Titolo:{cls._bold_close} {msg["title"]}',
            f'\n - {cls._bold_open}Descrizione:{cls._bold_close} '
            f'{msg["description"]}',
        ])
        if 'action' in msg:
            res += f'\n - {cls._bold_open}Azione:{cls._bold_close} {msg["action"]}'

        return res

    @classmethod
    def _format_issue(
        cls,
        msg: dict,
    ):

        if msg['action'] == 'open':
            action_text = 'aperta'
        elif msg['action'] == 'update':
            action_text = 'modificata'
        elif msg['action'] == 'close':
            action_text = 'chiusa'
        elif msg['action'] == 'reopen':
            action_text = 'riaperta'

        res = ''.join([
            f'È stata {action_text} una issue ',
            f'nel progetto {cls._bold_open}{msg["project_name"]}{cls._bold_close} ',
            f' su {msg["app"].capitalize()}\n',
            # f'\n\n{cls._bold_open}Informazioni:{cls._bold_close} '
            f'\n - {cls._bold_open}Autore:{cls._bold_close} {msg["author"]}'
            f'\n - {cls._bold_open}Titolo:{cls._bold_close} {msg["title"]}',
            f'\n - {cls._bold_open}Descrizione:{cls._bold_close} '
            f'{msg["description"]}',
        ])
        return res

    @classmethod
    def _format_push(
        cls,
        msg: dict,
        id_precision: int = 5,
        commits_count: int = 3
    ):
        """Formatta un messaggio di push in markdown
        e restituisce il risultato.
        """
        res = ''.join([
            f'È stato fatto un push '
            f'nel progetto {cls._bold_open}{msg["project_name"]}{cls._bold_close}',
            f' su {msg["app"].capitalize()}\n\n',
            f'{msg["commits_count"]} nuovi commit da {msg["author"]}:\n'
        ])
        for commit in msg['commits']:
            res += (f'- {commit["message"]} '
                    f'({cls._code_open}{commit["id"][:id_precision]}{cls._code_close}..)'
                    '\n')
            commits_count -= 1
            if commits_count == 0:
                res += '- ...\n'
                break
        return res
