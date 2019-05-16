"""
File: factory.py
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

from webhook.factory import WebhookFactory
from webhook.webhook import Webhook
from webhook.gitlab.issue_webhook import GitlabIssueWebhook
from webhook.gitlab.push_webhook import GitlabPushWebhook
from webhook.gitlab.issue_comment_webhook import GitlabIssueCommentWebhook
from webhook.gitlab.commit_comment_webhook import GitlabCommitCommentWebhook


class GitlabWebhookFactory(WebhookFactory):
    """Crea Webhook del tipo `GitlabWebhook`."""

    def create_webhook(self, kind: str) -> Webhook:
        """Crea un `GitlabWebhook` concreto in base al parametro.

        Parameters:

        `kind` - può essere 'issue', 'push', ...

        Raises:

        `NameError` - se il tipo di webhook non viene riconosciuto.
        """
        if kind == 'issue':
            return GitlabIssueWebhook()

        if kind == 'push':
            return GitlabPushWebhook()

        if kind == 'commit-note':
            return GitlabCommitCommentWebhook()

        if kind == 'issue-note':
            return GitlabIssueCommentWebhook()

        raise NameError()  # default
