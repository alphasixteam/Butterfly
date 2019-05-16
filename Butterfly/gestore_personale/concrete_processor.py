"""
File: concrete_processor.py
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

from gestore_personale.processor import Processor


class GitlabProcessor(Processor):
    """
        Classe processore di Gitlab
    """

    def _filter_users_by_topic(self, users: list, kind: str) -> list:
        """
        Cerca gli utenti disponibili nella data della notifica iscritti ai
        topic della segnalazione
        :param users: lista di utenti appartenenti al progetto della
            segnalazione e disponibili nel giorno della segnalazione
        :param kind: tipologia della segnalazione per GitLab
        :return: lista di utenti iscritti a quel topic
        """

        if kind == 'push':
            full_string = ''
            # Concatena i messaggi di tutti i commit
            for commit in self._message['commits']:
                full_string = ' '.join([
                    full_string,
                    commit['message'],
                ])
            return self._mongofacade.get_match_keywords(
                users,
                self._message['project_id'],
                full_string,
            )

        if kind == 'commit-note':
            return self._mongofacade.get_match_keywords(
                users,
                self._message['project_id'],
                self._message['title'],
            )

        # Se la segnalazione consiste in una issue
        elif kind == 'issue' or 'issue-note':
            self._check_labels(self._message['labels'])
            return self._mongofacade.get_match_labels(
                users,
                self._message['project_id'],
                self._message['labels'],
            )

        else:
            raise NameError('Type doesn\'t exist')

    def _check_labels(self, labels: list):
        """Guarda se le label della segnalazione
        legate al progetto indicati esistono.
        Funzione ausiliaria per `_filter_user_by_project`.
        Lavora come RedmineProcessor._check_label
        :param labels: lista delle label della segnalazione
        """
        project = self._message['project_id']
        label_project = self._mongofacade.get_label_project(project)
        for label in labels:
            if label not in label_project:
                self._mongofacade.insert_label_by_project(project, label)


class RedmineProcessor(Processor):
    """
        Classe processore di Redmine
    """

    def _filter_users_by_topic(self, users: list, kind: str) -> list:
        """
        Cerca gli utenti disponibili nella data della notifica iscritti ai
        topic della segnalazione
        :param users: lista di utenti appartenenti al progetto della
            segnalazione e disponibili nel giorno della segnalazione
        :param kind: tipologia della segnalazione per redmine
        :return: lista di utenti iscritti a quel topic
        """
        # L'unico tipo di segnalazioni possono essere 'issue'
        if kind != 'issue':
            raise NameError('Type not exists')

        self._check_labels(self._message['labels'])
        return self._mongofacade.get_match_labels(
            users,
            self._message['project_id'],
            self._message['labels'],
        )

    def _check_labels(self, labels: list):
        """
        Guarda se le label della segnalazione legate al progetto indicati
        esistono

        :param labels: lista delle label della segnalazione
        """
        project = self._message['project_id']
        label_project = self._mongofacade.get_label_project(project)
        for label in labels:
            if label not in label_project:
                self._mongofacade.insert_label_by_project(project, label)
