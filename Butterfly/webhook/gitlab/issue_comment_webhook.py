"""
File: issue_comment_webhook.py
Data creazione: 2019-02-15

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
"""
from pathlib import Path
import json
import os

import requests

from webhook.webhook import Webhook

# ChqrHpxfCsFsCY1N28Wx

class GitlabIssueCommentWebhook(Webhook):
    """`GitLabIssueCommentWebhook` implementa `Webhook`.
    Parse degli eventi di commento di una Issue di Gitlab.
    """
    _config_path = Path(__file__).parents[2] / 'config' / 'config.json'

    def parse(self, whook: dict = None):
        """Parsing del file JSON. Restituisce un riferimento al dizionario
        ottenuto.
        """

        assert whook is not None

        with open(GitlabIssueCommentWebhook._config_path, 'r') as f:
            configs = json.load(f)

        if os.environ['GITLAB_PRIVATE_TOKEN']:
            configs['PRIVATE-TOKEN'] = os.environ['GITLAB_PRIVATE_TOKEN']

        if os.environ['GITLAB_BASE_URL']:
            configs['base_url'] = os.environ['GITLAB_BASE_URL']

        webhook = {}
        webhook['app'] = 'gitlab'
        webhook['object_kind'] = 'issue-note'
        webhook['title'] = whook['issue']['title']
        webhook['project_id'] = json.dumps(str(configs['base_url']) + str(whook['project']['path_with_namespace'])).strip('"')
        webhook['project_name'] = whook['project']['name']
        webhook['author'] = whook['user']['name']
        webhook['description'] = whook['object_attributes']['description']
        webhook['action'] = 'comment'
        webhook['labels'] = self.project_labels(
            configs['base_url'],  # url dell'istanza Gitlab
            whook['project']['id'],  # id del progetto
            # Token privato di GitLab di un utente che ha accesso al progetto
            configs['PRIVATE-TOKEN'],
        )
        return webhook

    def project_labels(self, base_url: str, project_id: str, token: str):
        """Restituisce i nomi delle labels relative al progetto `project_id`.
        """
        result = requests.get(
            f'{base_url}/api/v4/projects/{project_id}/labels',
            headers={'PRIVATE-TOKEN': token}
        )
        labels = []
        if result.ok:  # 200
            # Salva solo i nomi delle label
            for label in result.json():
                labels.append(label['name'])
        return labels
