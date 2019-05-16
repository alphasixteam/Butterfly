"""
File: test_redmine_webhook.py
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

import json
from pathlib import Path

import pytest

from webhook.redmine.issue_webhook import RedmineIssueWebhook


def test_redmine_issue_webhook():
    webhook = RedmineIssueWebhook()

    with pytest.raises(AssertionError):
        webhook.parse(None)

    with open(
            Path(__file__).parents[3] /
            'webhook/redmine/tests' /
            'open_issue_redmine_webhook.json'
        ) as file:
        whook = json.load(file)

    webhook = webhook.parse(whook)

    assert webhook['app'] == 'redmine'
    assert webhook['object_kind'] == 'issue'
    assert webhook['title'] == 'Issue #1'
    assert webhook['description'] == 'This is a new issue'
    assert webhook['project_id'] == 1
    assert webhook['project_name'] == 'Test Project #1'
    assert webhook['action'] == 'opened'
    assert webhook['author'] == 'AlphaSix'
    assert webhook['labels'] == 'Bug'

    assert webhook['update'] == {}


def test_redmine_update_issue_webhook():
    webhook = RedmineIssueWebhook()

    with pytest.raises(AssertionError):
        webhook.parse(None)

    with open(
            Path(__file__).parents[3] /
            'webhook/redmine/tests' /
            'update_1_issue_redmine_webhook.json'
    ) as file:
        whook = json.load(file)

    webhook = webhook.parse(whook)

    assert webhook['app'] == 'redmine'
    assert webhook['object_kind'] == 'issue'
    assert webhook['title'] == 'Issue #1'
    assert webhook['description'] == 'This is a new issue'
    assert webhook['project_id'] == 1
    assert webhook['project_name'] == 'Test Project #1'
    assert webhook['action'] == 'updated'
    assert webhook['author'] == 'AlphaSix'
    assert webhook['labels'] == 'Bug'

    assert webhook['update']['comment'] == 'Editing Issue #1'
    assert webhook['update']['author'] == 'Redmine'
    assert webhook['update']['status'] == 'In Progress'
    assert webhook['update']['priority'] == 'Normal'
