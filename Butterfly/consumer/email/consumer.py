"""
File: consumer.py
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

Versione: 0.2.0
Creatore: Samuele Gardin, samuelegardin1997@gmail.com
Autori:
    Matteo Marchiori, matteo.marchiori@gmail.com
    Nicola Carlesso, nicolacarlesso@outlook.it
"""

from pathlib import Path
import json
import smtplib
from email.message import EmailMessage
import os

from kafka import KafkaConsumer

from consumer.consumer import Consumer


class EmailConsumer(Consumer):
    """Implementa Consumer"""

    _CONFIG_PATH = Path(__file__).parents[2] / 'config' / 'config.json'

    def __init__(self, consumer: KafkaConsumer):
        super(EmailConsumer, self).__init__(consumer)

        with open(self._CONFIG_PATH) as file:
            configs = json.load(file)
        self._sender = configs['email']['sender']

        try:
            # Psw, prima da config.json poi da var d'ambiente
            self._psw = configs['email']['psw']
            if self._psw == '':
                self._psw = None
        except KeyError:
            self._psw = None

        # venv BUTTERFLY_EMAIL_PSW
        if self._psw == None:
            try:
                self._psw = os.environ['BUTTERFLY_EMAIL_PSW']
            except KeyError as e:
                exit(1)

    def send(self, receiver: str, mail_text: str):
        """Manda il messaggio finale, tramite il server mail,
        all'utente finale.
        """
        with smtplib.SMTP('smtp.gmail.com', 587) as mailserver:
            mailserver.ehlo()
            mailserver.starttls()

            try:
                # Autenticazione
                mailserver.login(self._sender, self._psw)  # Login al server SMTP

                msg = EmailMessage()
                msg['Subject'] = (
                    "[Butterfly] Segnalazione progetto "
                    f"{mail_text['project_name']}")

                msg['From'] = self._sender
                msg['To'] = receiver
                msg.set_content(self.format(mail_text))
                msg.add_alternative(f"""\
                <html>
                    <body>
                        {self.format_html(mail_text)}
                    </body>
                </html>
                    """, subtype='html')

                try:  # Tenta di inviare l'Email
                    mailserver.send_message(msg)
                except smtplib.SMTPException:
                    print('Errore, email non inviata. ')

            # Errore di autenticazione
            except smtplib.SMTPAuthenticationError:
                print('Email e password non corrispondono.')

            # Interruzione da parte dell'utente della task
            except KeyboardInterrupt:
                print('\nInvio email annullato. '
                      'In ascolto di altri messaggi ...')

            finally:
                mailserver.quit()

    def format(self, msg):
        """Restituisce una stringa con una formattazione migliore da un
        oggetto JSON (Webhook).
        """
        if msg['object_kind'] == 'push':
            return self._format_push_no_html(msg)

        elif msg['object_kind'] == 'issue':
            return self._format_issue_no_html(msg)

        res = ''
        res = self._preamble(msg['object_kind'])

        res += ''.join([
            f' nel progetto {msg["project_name"]} ',
            f'\n\nSorgente: {msg["app"].capitalize()}',
            f'\nAutore: {msg["author"]}'
            f'\n\n Informazioni: '
            f'\n - Titolo: \t\t{msg["title"]}',
            f'\n - Descrizione: \n'
            f'  {msg["description"]}',
            f'\n - Azione: \t{msg["action"]}'
        ])

        return res

    def format_html(self, msg: dict) -> str:
        """Restituisce una stringa in formato HTML da un
        oggetto JSON.
        """
        if msg['object_kind'] == 'push':
            return self._format_push_html(msg)

        elif msg['object_kind'] == 'issue':
            return self._format_issue_html(msg)

        res = '<p>'
        res += self._preamble(msg['object_kind'])

        res += ''.join([
            f' nel progetto <strong>{msg["project_name"]}</strong>',
            f' su {msg["app"].capitalize()}.</p>',
            '<ul>'
            f'<li><strong>Autore:</strong> {msg["author"]}</li>'
            f'<li><strong>Titolo:</strong> {msg["title"]}</li>',
            f'<li><strong>Descrizione:</strong> '
            f'{msg["description"]}</li>',
            f'<li><strong>Azione:</strong> {msg["action"]}</li>'
            '</ul>'
        ])
        return res

    @classmethod
    def _format_push_no_html(cls, msg: dict) -> str:
        """Formatta un messaggio di push
        e restituisce il risultato.
        """
        res = ''.join([
            f'È stato fatto un push '
            f'nel progetto {msg["project_name"]} ',
            f' su {msg["app"].capitalize()}.\n',
            f'{msg["commits_count"]} nuovo/i commit da {msg["author"]}:\n'
            '\n'
        ])
        for commit in msg['commits']:
            res += (f'- {commit["message"]} '
                    f'({commit["id"]});'
                    '\n')
        return res

    @classmethod
    def _format_push_html(cls, msg: dict) -> str:
        """Formatta un messaggio di push in HTML
        e restituisce il risultato.
        """
        res = ''.join([
            f'<p>È stato fatto un push '
            f'nel progetto <strong>{msg["project_name"]}</strong>',
            f' su {msg["app"].capitalize()}.</p>',
            f'<p>{msg["commits_count"]} nuovo/i commit da {msg["author"]}:</p>'
            '\n<ul>'
        ])
        for commit in msg['commits']:
            res += (f'<li>{commit["message"]} '
                    f'(<code>{commit["id"]}</code>);'
                    '</li>\n')
        res += '\n</ul>'
        return res

    @classmethod
    def _format_issue_html(cls, msg: dict) -> str:
        """Formatta un messaggio di issue in HTML
        e restituisce il risultato.
        """
        if msg['action'] == 'open':
            action_text = 'aperta'
        elif msg['action'] == 'update':
            action_text = 'modificata'
        elif msg['action'] == 'close':
            action_text = 'chiusa'
        elif msg['action'] == 'reopen':
            action_text = 'riaperta'

        res = ''.join([
            f'<p>È stata {action_text} una issue ',
            f'nel progetto <strong>{msg["project_name"]}</strong>',
            f' su {msg["app"].capitalize()}.\n</p>\n<ul>',
            # f'\n\n{cls._bold}Informazioni:{cls._bold} '
            f'\n<li><strong>Autore:</strong> {msg["author"]};</li>'
            f'\n<li><strong>Titolo:</strong> {msg["title"]};</li>',
            f'\n<li><strong>Descrizione:</strong> '
            f'{msg["description"]};</li></ul>',
        ])
        return res

    @classmethod
    def _format_issue_no_html(
        cls,
        msg: dict,
    ):
        """Formatta un messaggio di push
        e restituisce il risultato.
        """
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
            f'nel progetto {msg["project_name"]}',
            f' su {msg["app"].capitalize()}\n',
            # f'\n\nInformazioni: '
            f'\n - Autore: {msg["author"]}'
            f'\n - Titolo: {msg["title"]}',
            f'\n - Descrizione: '
            f'{msg["description"]}',
        ])
        return res

    def _preamble(self, field):
        """Preambolo del messaggio.
        """

        res = ''
        if field == 'issue':
            res += 'È stata aperta una issue '

        elif field == 'push':
            res += 'È stata fatto un push '

        elif field == 'issue-note':
            res += 'È stata commentata una issue '

        elif field == 'commit-note':
            res += 'È stato commentato un commit '

        else:
            raise KeyError

        return res
