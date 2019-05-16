"""
File: test_Concreteprocessor.py
Data creazione: 2019-03-13

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
Creatore: Ciprian Voinea, ciprianv96@hotmail.it
Autori:
    Nicola Carlesso, nicolacarlesso@outlook.it
"""

from unittest.mock import Mock
from gestore_personale.concrete_processor import GitlabProcessor, RedmineProcessor


mongoFacade = Mock()
message_issue_gitlab = {
    'app': 'gitlab',
    'object_kind': 'issue',
    'title': 'Issue #1',
    'description': 'cose a caso',
    'project_id': 'https://nfnidd',
    'project_name': 'proj #1',
    'author': 'Tullio',
    'assignees': [
        'me',
        'te'
    ],
    'action': 'close',
    'labels': [
        'bug',
        'fix'
    ]
}

message_issue_redmine = {
'app': 'redmine',
    'object_kind': 'issue',
    'title': 'Issue #1',
    'description': 'cose a caso',
    'project_id': 1,
    'project_name': 'proj #1',
    'author': 'Tullio',
    'assignees': 'me',
    'action': 'close',
    'labels': 'Bug'
}

message_commit_gitlab = {
    'app': 'gitlab',
    'object_kind': 'issue',
    'title': 'Issue #1',
    'project_id': 'https://nfnidd',
    'project_name': 'proj #1',
    'author': 'Tullio'
}

message_commit_comment_gitlab = {
    'app': 'gitlab',
    'object_kind': 'note_issue',
    'title': 'Issue #1',
    'description': 'cose a caso',
    'project_id': 'https://nfnidd',
    'project_name': 'proj #1',
    'author': 'Tullio',
    'comment': 'commento'
}

mongoFacade.get_match_keywords.return_value = ['1', '2', '3', '4']
mongoFacade.get_match_labels.return_value = ['1', '2', '5']
users = ['1', '2', '3', '4', '5', '6', '7']


def test_gitlab_filter_push():
    p_gitlab = GitlabProcessor(message_commit_gitlab, mongoFacade)
    user_subscribes = p_gitlab._filter_users_by_topic(users, 'push')
    assert user_subscribes == ['1', '2', '3', '4']

def test_gitlab_filter_issue():
    p_gitlab = GitlabProcessor(message_issue_gitlab, mongoFacade)
    user_subscribers = p_gitlab._filter_users_by_topic(users, 'issue')
    assert user_subscribers == ['1', '2', '5']

def test_redmine_filter_issue():
    p_gitlab = RedmineProcessor(message_issue_redmine, mongoFacade)
    user_subscribers = p_gitlab._filter_users_by_topic(users, 'issue')
    assert user_subscribers == ['1', '2', '5']