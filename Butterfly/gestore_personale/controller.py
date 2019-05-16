"""
File: controller.py
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
Creatore: Matteo Marchiori, matteo.marchiori@gmail.com
Autori:
"""

# Usage: python3 __file__.py

from os import urandom

from flask import Flask
import flask_restful

from mongo_db.facade import MongoFacade
from mongo_db.users import MongoUsers
from mongo_db.projects import MongoProjects
from mongo_db.singleton import MongoSingleton
from gestore_personale.observer import Observer
from gestore_personale.api import User, PostUser, Project
from gestore_personale.api import Preference, PostPreference, ApiHandler
from gestore_personale.web import Web


class Controller(Observer):
    """
        Classe controller dell'architettura MVC del gestore personale.
    """

    def __init__(
        self,
        server: Flask,
        api: flask_restful.Api,
        handler: ApiHandler,
        web: Web,
        model: MongoFacade
    ):
        self._server = server
        self._api = api
        self._handler = handler
        self._web = web
        self._user = User
        self._post_user = PostUser
        self._project = Project
        self._preference = Preference
        self._post_preference = PostPreference

        # mapping delle risorse con i rispettivi URL
        self._api.add_resource(
            self._user,
            '/api/v1/user/<url>',
            resource_class_kwargs={'model': model}
        )

        self._api.add_resource(
            self._post_user,
            '/api/v1/user',
            resource_class_kwargs={'model': model}
        )

        self._api.add_resource(
            self._project,
            '/api/v1/project/<path:url>',
            resource_class_kwargs={'model': model}
        )

        self._api.add_resource(
            self._preference,
            '/api/v1/preference/<url>',
            resource_class_kwargs={'model': model}
        )

        self._api.add_resource(
            self._post_preference,
            '/api/v1/preference',
            resource_class_kwargs={'model': model}
        )

        # mapping delle API REST
        self._user.addObserver(self._user, obs=self)
        self._post_user.addObserver(self._post_user, obs=self)
        self._user.addObserver(self._project, obs=self)
        self._preference.addObserver(self._preference, obs=self)
        self._post_preference.addObserver(self._post_preference, obs=self)

        # mapping degli URL coi metodi
        self._server.add_url_rule(
            '/',
            'panel',
            self._web.panel,
            methods=['GET', 'POST']
        )

        self._server.add_url_rule(
            '/web_user',
            'web_user',
            self._web.web_user,
            methods=['GET', 'POST', 'PUT', 'DELETE']
        )

        self._server.add_url_rule(
            '/web_project',
            'web_project',
            self._web.web_project,
            methods=['POST', 'DELETE']
        )

        self._server.add_url_rule(
            '/web_preference',
            'web_preference',
            self._web.web_preference,
            methods=['PUT']
        )

    def update(self, resource: str, request_type: str, url: str, msg: str):
        """
            Metodo update dell'observer
        """
        if resource == 'user':
            return self._handler.api_user(request_type, url, msg)
        elif resource == 'project':
            return self._handler.api_project(request_type, url, msg)
        elif resource == 'preference':
            return self._handler.api_preference(request_type, url, msg)


def main():
    flask = Flask(__name__)
    flask.secret_key = urandom(16)
    api = flask_restful.Api(flask)
    mongo = MongoSingleton.instance()
    users = MongoUsers(mongo)
    projects = MongoProjects(mongo)
    facade = MongoFacade(users, projects)
    web = Web(facade)
    handler = ApiHandler(facade)
    Controller(
        flask,
        api,
        handler,
        web,
        facade
    )
    flask.run(host='0.0.0.0', debug=True)


if __name__ == "__main__":
    main()
