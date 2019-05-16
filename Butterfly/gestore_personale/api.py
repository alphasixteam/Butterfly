"""
File: api.py
Data creazione: 2019-03-20

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

import json
import datetime

from flask import request
import flask_restful
from bson.json_util import dumps

from mongo_db.facade import MongoFacade
from gestore_personale.observer import Subject


class SubjectResource(type(Subject), type(flask_restful.Resource)):
    """
        Metaclasse per rendere Subject una Resource
    """
    pass


class Resource(Subject, flask_restful.Resource, metaclass=SubjectResource):
    """
        Classe per definire una risorsa.
    """

    def __init__(self, model: MongoFacade):
        super(Resource, self).__init__()
        self._model = model

    def notify(self, request_type: str, resource: str, url: str, msg: str):
        """
           Metodo per notificare gli osservatori della risorsa
        """
        for obs in self._lst:
            return obs.update(request_type, resource, url, msg)


class User(Resource):
    """
       Classe per rappresentare la risorsa User
    """

    def get(self, url: str):
        return self.notify('user', 'GET', url, None)

    def put(self, url: str):
        data = request.get_json(force=True)
        return self.notify('user', 'PUT', url, data)

    def delete(self, url: str):
        return self.notify('user', 'DELETE', url, None)


class PostUser(Resource):
    """
       Classe per rappresentare la risorsa User senza parametro
    """

    def post(self):
        data = request.get_json(force=True)
        return self.notify('user', 'POST', None, data)


class Project(Resource):
    """
       Classe per rappresentare la risorsa Project
    """

    def get(self, url: str):
        return self.notify('project', 'GET', url, None)

    def delete(self, url: str):
        return self.notify('project', 'DELETE', url, None)


class Preference(Resource):
    """
       Classe per rappresentare la risorsa Preference
    """

    def put(self, url: str) -> dict:
        data = request.get_json(force=True)
        return self.notify('preference', 'PUT', url, data)

    def delete(self, url: str) -> dict:
        data = request.get_json(force=True)
        return self.notify('preference', 'DELETE', url, data)


class PostPreference(Resource):
    """
       Classe per rappresentare la risorsa Preference senza parametro
    """

    def post(self):
        data = request.get_json(force=True)
        return self.notify('preference', 'POST', None, data)


class ApiHandler:
    """
       Classe per gestire le richieste alle Api REST
    """

    def __init__(
        self,
        model: MongoFacade
    ):
        self._model = model

    def api_user(self, request_type: str, url: str, msg: str):
        """
            Metodo per gestire le richieste alla risorsa User
        """

        if request_type == 'GET':
            # leggo dal database, se non lo trovo l'utente non esiste
            try:
                user = self._model.read_user(url)
                userjson = json.loads(dumps(user))
                if userjson.get('irreperibilita'):
                    # rendo leggibile l'irreperibilita
                    for i, data in enumerate(userjson['irreperibilita']):
                        userjson['irreperibilita'][i]['$date'] = \
                            datetime.datetime.strftime(
                                datetime.datetime.fromtimestamp(
                                    userjson['irreperibilita'][i]['$date']/1000
                                ),
                                format="%Y-%m-%d"
                            )
                return userjson
            except AssertionError:
                return {'error': 'Utente inesistente.'}, 404
        elif request_type == 'PUT':
            # leggo i campi della richiesta per le modifiche
            nome = msg.get('name')
            cognome = msg.get('surname')
            email = msg.get('email')
            telegram = msg.get('telegram')
            modify = {}
            # memorizzo i vecchi identificativi
            oldmail = self._model.get_user_email_web(url)
            oldtelegram = self._model.get_user_telegram_web(url)
            userid = oldmail if oldmail else oldtelegram
            if email or telegram:
                # aggiungo i campi da modificare
                if nome:
                    modify.update(nome=nome)
                if cognome:
                    modify.update(cognome=cognome)
                if email:
                    modify.update(email=email)
                if telegram:
                    modify.update(telegram=telegram)
                # controllo che i dati univoci non confliggano
                if ((
                    email and
                    self._model.user_exists(email) and
                    email != oldmail
                )or(
                    telegram and
                    self._model.user_exists(telegram) and
                    telegram != oldtelegram
                    )
                ):
                    return {'error': 'I dati inseriti confliggono\
 con altri già esistenti.'}, 409
                # aggiorno i dati
                if('nome' in modify):
                    self._model.update_user_name(
                        userid,
                        modify['nome']
                    )
                if('cognome' in modify):
                    self._model.update_user_surname(
                        userid,
                        modify['cognome']
                    )
                if(
                    'email' in modify and (
                        not oldmail or
                        modify['email'] != oldmail
                    )
                ):
                    self._model.update_user_email(
                        userid,
                        modify.get('email')
                    )
                    userid = modify['email']
                if('telegram' in modify and (
                    (not oldtelegram) or
                    (modify['telegram'] != oldtelegram)
                )):
                    self._model.update_user_telegram(
                        userid,
                        modify.get('telegram')
                    )
                    userid = modify['telegram']
                # controllo il caso identificativi da scambiare
                if('email' not in modify):
                    self._model.update_user_email(
                        userid,
                        ''
                    )
                    if oldmail:
                        userid = modify['telegram']
                    self._model.update_user_preference(
                        userid,
                        'telegram'
                    )
                if('telegram' not in modify):
                    self._model.update_user_telegram(
                        userid,
                        ''
                    )
                    if oldtelegram:
                        userid = modify['email']
                    self._model.update_user_preference(
                        userid,
                        'email'
                    )
                return {'ok': 'Utente modificato correttamente.'}, 200
            else:
                return {'error': 'Si prega di inserire almeno email o\
 telegram per modificare l\'utente.'}, 400
        elif request_type == 'DELETE':
            if url:
                self._model.delete_user(url)
                return {'ok': 'Utente rimosso correttamente'}, 200
        elif request_type == 'POST':
            # leggo i campi della richiesta per l'aggiunta utente
            nome = msg.get('name')
            cognome = msg.get('surname')
            email = msg.get('email')
            telegram = msg.get('telegram')
            if email or telegram:
                # controllo non ci siano conflitti con gli identificativi
                if (
                    (email and self._model.user_exists(email)) or
                    (telegram and self._model.user_exists(telegram))
                ):
                    return {'error': 'L\'utente inserito esiste già.'}, 409
                else:
                    self._model.insert_user(
                        name=nome,
                        surname=cognome,
                        email=email,
                        telegram=telegram
                    )
                    # imposto una preferenza di default
                    if email:
                        self._model.update_user_preference(email, 'email')
                    elif telegram:
                        self._model.update_user_preference(
                            telegram,
                            'telegram'
                        )
                    return {'ok': 'Utente inserito correttamente'}, 200
            else:
                return {'error': 'Si prega di inserire almeno email o telegram\
 per inserire l\'utente.'}, 409

    def api_project(self, request_type: str, url: str, msg: str):
        if request_type == 'GET':
            # se il progetto non esiste, restituisco l'errore
            try:
                project = self._model.read_project(url)
                projectjson = json.loads(dumps(project))
                return projectjson
            except AssertionError:
                return {'error': 'Progetto inesistente.'}, 404
        elif request_type == 'DELETE':
            if url:
                # elimino tutte le preferenze legate al progetto
                users = self._model.get_project_users(url)
                for user in users:
                    if user.get('email'):
                        userid = user['email']
                    elif user.get('telegram'):
                        userid = user['telegram']
                    self._model.remove_user_project(userid, url)
                # elimino il progetto
                self._model.delete_project(url)
                return {'ok': 'Progetto rimosso correttamente'}, 200

    def api_preference(self, request_type: str, url: str, msg: str):
        if request_type == 'PUT':
            # controllo il tipo di preferenza da modificare
            tipo = msg.get('tipo')
            if tipo == 'topics':
                # leggo i campi da modificare
                project = msg.get('project')
                priority = msg.get('priority')
                topics = msg.get('topics')
                keywords = msg.get('keywords')
                user_projects = self._model.get_user_projects(url)
                # controllo che l'utente sia interessato
                if(
                    user_projects and
                    any(voice['url'] == project for voice in user_projects)
                ):
                    project_data = self._model.read_project(project)
                    self._model.set_user_priority(
                        url, project, priority
                    )
                    self._model.reset_user_topics(
                        url,
                        project
                    )
                    # imposto i topics
                    for topic in topics:
                        if (
                            project_data and
                            project_data.get('topics') and
                            topic in project_data['topics']
                        ):
                            self._model.add_user_topics(
                                url,
                                project,
                                topic
                            )
                    # imposto le keywords
                    self._model.reset_user_keywords(
                        url,
                        project
                    )
                    project_data = self._model.read_project(
                        project
                    )
                    if project_data['app'] != 'redmine':
                        for keyword in keywords:
                            if keyword:
                                self._model.add_user_keywords(
                                    url,
                                    project,
                                    keyword
                                )
                    return {'ok': 'Preferenza modificata correttamente.'}, 200
                return {'error': 'Progetto non presente nelle\
 preferenze.'}, 404
            elif tipo == 'irreperibilita':
                # controllo il formato delle date
                try:
                    # ricevo le date
                    giorni = msg.get('giorni')
                    if giorni:
                        # metto in liste giorni vecchi e giorni nuovi
                        giorni_old = self._model.read_user(
                            url
                        ).get('irreperibilita')
                        giorni_new = []
                        for giorno in giorni:
                            giorni_new.append(
                                datetime.datetime.strptime(giorno, '%Y-%m-%d')
                            )
                        to_remove = []
                        # se il giorno vecchio non è tra i nuovi, va rimosso
                        # ma va fatto per mese, non in assoluto
                        if giorni_old and giorni_new:
                            for giorno in giorni_new:
                                to_remove.append(
                                    datetime.datetime.strptime(
                                        giorno.strftime('%Y') + '-\
' + giorno.strftime('%m'),
                                        '%Y-%m'
                                    )
                                )
                            for mese in to_remove:
                                month = mese.strftime('%m')
                                year = mese.strftime('%Y')
                                for giorno in giorni_old:
                                    if(
                                        giorno.strftime('%Y') == year and
                                        giorno.strftime('%m') == month
                                    ):
                                        self._model.\
                                            remove_giorno_irreperibilita(
                                                url,
                                                int(year),
                                                int(month),
                                                int(giorno.strftime('%d'))
                                            )
                            # aggiungo le nuove irreperibilità
                            for giorno in giorni_new:
                                self._model.add_giorno_irreperibilita(
                                    url,
                                    int(giorno.strftime('%Y')),
                                    int(giorno.strftime('%m')),
                                    int(giorno.strftime('%d'))
                                )
                        return {'ok': 'Preferenza modificata\
 correttamente'}, 200
                    return {'error': 'Giorni non inseriti.'}, 404
                except ValueError:
                    return {'error': 'Le date fornite non sono in formato\
 corretto.'}, 400
            elif tipo == 'piattaforma':
                platform = msg.get('platform')
                if platform == "telegram":
                    telegram = self._model.get_user_telegram_web(url)
                    if not telegram:
                        return {'error': 'Telegram non presente nel\
 sistema.'}, 404
                elif platform == "email":
                    email = self._model.get_user_email_web(url)
                    if not email:
                        return {'error': 'Email non presente nel\
 sistema.'}, 404
                else:
                    return {'error': 'La piattaforma deve essere telegram\
 o email.'}, 400
                self._model.update_user_preference(url, platform)
                return {'ok': 'Preferenza modificata correttamente'}, 200
            else:
                return {'error': 'Tipo di preferenza non trovato.'}, 400
        elif request_type == 'DELETE':
            project = msg.get('project')
            # controllo che il progetto esista e sia nelle preferenze
            try:
                if project and self._model.get_project_by_url(project):
                    self._model.remove_user_project(url, project)
                    return {'ok': 'Preferenza rimossa correttamente.'}, 200
                else:
                    return {'error': 'Nessun progetto selezionato o\
 progetto inesistente.'}, 400
            except AssertionError:
                return {'error': 'Progetto non presente nelle preferenze o\
 utente inesistente.'}, 400
        elif request_type == 'POST':
            user = msg.get('user')
            project = msg.get('project')
            # controllo che il progetto non esista e che l'utente esista
            try:
                if project and self._model.get_project_by_url(project):
                    self._model.add_user_project(user, project)
                    return {'ok': 'Preferenza aggiunta correttamente.'}, 200
                else:
                    return {'error': 'Nessun progetto selezionato o\
 progetto inesistente.'}, 400
            except AssertionError:
                return {'error': 'Progetto già presente o\
 utente inesistente.'}, 400
