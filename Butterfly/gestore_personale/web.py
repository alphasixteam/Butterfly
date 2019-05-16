"""
File: web.py
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

import pathlib
import datetime
import calendar

from flask import request, session, redirect
from flask import url_for, render_template_string

from mongo_db.facade import MongoFacade

# directory per html
html = (pathlib.Path(__file__).parent / 'static' / 'html').resolve()


class Web:
    """
        Gestione delle richieste HTTP da client Web
    """

    def __init__(
        self,
        model: MongoFacade
    ):
        self._model = model

    # metodi di utilità
    def _users_id(self):
        ids = []
        for user in self._model.users():
            ids.append(user['_id'])
        return ids

    def _projects_id(self):
        ids = []
        for project in self._model.projects():
            ids.append(project['url'])
        return ids

    def _check_session(self):
        return 'email' in session or 'telegram' in session

    def _check_admin(self):
        return 'admin' in session

    def _check_values(self):
        return len(request.values) != 0

    def access(self):
        """
            Metodo per gestire l'accesso di un utente
        """
        fileHtml = html / 'access.html'
        page = fileHtml.read_text()
        userid = request.values.get('userid')
        # se è stato passato un id procedo, altrimenti no
        if userid:
            # se esiste l'utente procedo
            if self._model.user_exists(userid):
                # imposto le variabili di sessione
                session['email'] = self._model.get_user_email_web(userid)
                session['telegram'] = self._model.get_user_telegram_web(userid)
                if 'email' in session and session['email']:
                    session['userid'] = session['email']
                else:
                    session['userid'] = session['telegram']
                user = self._model.read_user(userid)
                # controllo se è amministratore o utente normale
                if 'admin' in user and user['admin'] == 1:
                    session['admin'] = 1
                return redirect(url_for('panel'), code=303)
            else:
                page = page.replace(
                    '*access*',
                    '<p>Accesso non riuscito. ' + userid + ' non trovato.</p>')
                page = page.replace('*userid*', userid)
        if request.values.get('access'):
            page = page.replace(
                    '*access*',
                    '<p>Si prega di inserire un identificativo \
per eseguire l\'accesso.</p>')
        page = page.replace('*access*', '')
        page = page.replace('*userid*', '')
        return page

    def logout(self):
        """
            Metodo per il logout
        """
        session.clear()

    def panel(self, error=''):
        """
            Metodo per la gestione del pannello di controllo
        """
        # controllo il login dell'utente
        if self._check_session():
            # controllo dell'utente amministratore
            if self._check_admin():
                fileHtml = html / 'adminpanel.html'
            else:
                fileHtml = html / 'panel.html'
            page = fileHtml.read_text()
            page = page.replace('*panel*', error)
            page = page.replace('*user*', session['userid'])
            try:
                return render_template_string(page)
            except TypeError:
                return page
        else:
            try:
                return render_template_string(self.access())
            except TypeError:
                return self.access()

    def add_user(self):
        """
            Metodo per aggiungere un utente
        """
        fileHtml = html / 'adduser.html'
        page = fileHtml.read_text()
        # leggo i dati in input
        nome = request.values.get('nome')
        cognome = request.values.get('cognome')
        email = request.values.get('email')
        telegram = request.values.get('telegram')
        # controllo ci sia almeno un identificativo
        if email or telegram:
            # rimpiazzo per comodità
            if nome:
                page = page.replace('*nome*', nome)
            if cognome:
                page = page.replace('*cognome*', cognome)
            if email:
                page = page.replace('*email*', email)
            if telegram:
                page = page.replace('*telegram*', telegram)
            # controllo l'univocità degli identificativi
            if (
                (email and self._model.user_exists(email)) or
                (telegram and self._model.user_exists(telegram))
            ):
                page = page.replace(
                    '*adduser*',
                    '<p>L\'utente inserito esiste già.</p>'
                )
            else:
                page = page.replace(
                    '*adduser*',
                    '<p>Utente inserito correttamente.</p>'
                )
                self._model.insert_user(
                    name=nome,
                    surname=cognome,
                    email=email,
                    telegram=telegram
                )
                if email:
                    self._model.update_user_preference(email, 'email')
                elif telegram:
                    self._model.update_user_preference(telegram, 'telegram')
        if 'postuser' in request.values:
            page = page.replace(
                    '*adduser*',
                    '<p>Si prega di inserire almeno email o telegram \
per inserire l\'utente.</p>')
        page = page.replace('*nome*', '')
        page = page.replace('*cognome*', '')
        page = page.replace('*email*', '')
        page = page.replace('*telegram*', '')
        page = page.replace('*adduser*', '')
        page = page.replace('*user*', session['userid'])
        return page

    def modify_user(self):
        """
            Metodo per modificare un utente
        """
        fileHtml = html / 'modifyuser.html'
        page = fileHtml.read_text()
        # ricevo i dati per la modifica
        nome = request.values.get('nome')
        cognome = request.values.get('cognome')
        email = request.values.get('email')
        telegram = request.values.get('telegram')
        modify = {}
        # controllo ci sia almeno un identificativo
        if email or telegram:
            # controllo quali dati sostituire
            if nome:
                page = page.replace('*nome*', nome)
                modify.update(nome=nome)
            if cognome:
                page = page.replace('*cognome*', cognome)
                modify.update(cognome=cognome)
            if email:
                page = page.replace('*email*', email)
                modify.update(email=email)
            if telegram:
                page = page.replace('*telegram*', telegram)
                modify.update(telegram=telegram)
            # controllo che i nuovi dati univoci non collidano con altri utenti
            if ((
                email and
                self._model.user_exists(email) and
                email != session.get('email')
            )or(
                telegram and
                self._model.user_exists(telegram) and
                telegram != session.get('telegram')
                )
            ):
                page = page.replace(
                    '*modifyuser*',
                    '<p>I dati inseriti confliggono\
 con altri già esistenti.</p>'
                )
            else:
                page = page.replace(
                    '*modifyuser*',
                    '<p>Utente modificato correttamente.</p>'
                )
                if('nome' in modify):
                    self._model.update_user_name(
                        session['userid'],
                        modify['nome']
                    )
                if('cognome' in modify):
                    self._model.update_user_surname(
                        session['userid'],
                        modify['cognome']
                    )
                # modifico gli identificativi se sono cambiati,
                # anche in sessione
                if(
                    'email' in modify and (
                        ('email' not in session) or
                        (modify['email'] != session['email'])
                    )
                ):
                    self._model.update_user_email(
                        session['userid'],
                        modify.get('email')
                    )
                    session['email'] = modify['email']
                    session['userid'] = modify['email']
                if('telegram' in modify and (
                    ('telegram' not in session) or
                    (modify['telegram'] != session['telegram'])
                )):
                    self._model.update_user_telegram(
                        session['userid'],
                        modify.get('telegram')
                    )
                    session['telegram'] = modify['telegram']
                    session['userid'] = modify['telegram']
                # caso in cui gli identificativi si invertano
                if('email' not in modify):
                    self._model.update_user_email(
                        session['userid'],
                        ''
                    )
                    if session.get('email'):
                        session.pop('email')
                        session['userid'] = session['telegram']
                    self._model.update_user_preference(
                        session['userid'],
                        'telegram'
                    )
                if('telegram' not in modify):
                    self._model.update_user_telegram(
                        session['userid'],
                        ''
                    )
                    if session.get('telegram'):
                        session.pop('telegram')
                        session['userid'] = session['email']
                    self._model.update_user_preference(
                        session['userid'],
                        'email'
                    )
        if 'putuser' in request.values:
            page = page.replace(
                    '*modifyuser*',
                    '<p>Si prega di inserire almeno email o telegram \
per modificare l\'utente.</p>')
        user = self._model.read_user(session['userid'])
        # rimpiazzo i campi per comodità
        page = page.replace('*nome*', user['name'] if user['name'] else '')
        page = page.replace(
            '*cognome*',
            user['surname'] if user['surname'] else ''
        )
        page = page.replace(
            '*email*',
            user['email'] if user['email'] else ''
        )
        page = page.replace(
            '*telegram*',
            user['telegram'] if user['telegram'] else ''
        )
        page = page.replace('*modifyuser*', '')
        page = page.replace('*user*', session['userid'])
        return page

    def remove_user(self):
        """
            Metodo per rimuovere un utente
        """
        fileHtml = html / 'removeuser.html'
        page = fileHtml.read_text()
        # ricevo l'identificativo dell'utente da rimuovere
        userid = request.values.get('userid')
        if userid:
            page = page.replace(
                '*removeuser*',
                '<p>Utente rimosso correttamente.</p>'
            )
            email = self._model.get_user_email_from_id(userid)
            telegram = self._model.get_user_telegram_from_id(userid)
            user = email if email else telegram
            self._model.delete_user_from_id(userid)
            # controllo se è l'utente corrente
            if user == session['email'] or user == session['telegram']:
                self.logout()
                return redirect(url_for('panel'), code=303)
        page = page.replace('*removeuser*', '')
        page = page.replace('*user*', session['userid'])
        # costruisco la lista di utenti memorizzati
        values = self._users_id()
        display = []
        for user in values:
            telegram = self._model.get_user_telegram_from_id(user)
            email = self._model.get_user_email_from_id(user)
            if telegram is None:
                telegram = ''
            if email is None:
                email = ''
            display.append(
                telegram +
                ' ' +
                email
            )
        options = '<select id="userid" name="userid">'
        for i, voice in enumerate(display):
            options += '<option value="' + str(values[i]) + '">'
            options += display[i]
            options += '</option>'
        options += '</select>'
        return page.replace('*userids*', options)

    def show_user(self):
        """
            Metodo per mostrare i dati degli utenti
        """
        fileHtml = html / 'showuser.html'
        page = fileHtml.read_text()
        page = page.replace('*user*', session['userid'])
        # ricevo l'id dell'utente da mostrare
        userid = request.values.get('userid')
        if userid:
            email = self._model.get_user_email_from_id(userid)
            telegram = self._model.get_user_telegram_from_id(userid)
            user = email if email else telegram
            # mostro l'utente
            page = page.replace('*showuser*', self.load_web_user(user))
        page = page.replace('*showuser*', '')
        # preparo la lista con gli utenti memorizzati e la mostro
        values = self._users_id()
        display = []
        for user in values:
            telegram = self._model.get_user_telegram_from_id(user)
            email = self._model.get_user_email_from_id(user)
            if telegram is None:
                telegram = ''
            if email is None:
                email = ''
            display.append(
                telegram +
                ' ' +
                email
            )
        options = '<select id="userid" name="userid">'
        for i, voice in enumerate(display):
            options += '<option value="' + str(values[i]) + '"'
            if str(values[i]) == userid:
                options += ' selected="selected"'
            options += '>'
            options += display[i]
            options += '</option>'
        options += '</select>'
        return page.replace('*userids*', options)

    def remove_project(self):
        """
            Metodo per rimuovere un progetto
        """
        fileHtml = html / 'removeproject.html'
        page = fileHtml.read_text()
        # ricevo l'id del progetto
        project = request.values.get('projectid')
        if project:
            page = page.replace(
                '*removeuser*',
                '<p>Progetto rimosso correttamente.</p>'
            )
            # rimuovo le preferenze associate al progetto
            users = self._model.get_project_users(project)
            for user in users:
                if user.get('email'):
                    userid = user['email']
                elif user.get('telegram'):
                    userid = user['telegram']
                self._model.remove_user_project(userid, project)
            # rimuovo il progetto
            self._model.delete_project(project)
        page = page.replace('*removeproject*', '')
        page = page.replace('*user*', session['userid'])
        # costruisco la lista di progetti da rimuovere
        values = self._projects_id()
        options = '<select id="projectid" name="projectid">'
        for value in values:
            options += '<option value="' + str(value) + '"'
            if str(value) == project:
                options += ' selected="selected"'
            options += '>'
            options += value
            options += '</option>'
        options += '</select>'
        return page.replace('*projectids*', options)

    def show_project(self):
        """
            Metodo per mostrare i dettagli dei progetti
        """
        fileHtml = html / 'showproject.html'
        page = fileHtml.read_text()
        # ricevo l'id del progetto da mostrare
        project = request.values.get('projectid')
        if project:
            # mostro il progetto
            page = page.replace(
                '*showproject*',
                self.load_web_project(project)
            )
        page = page.replace('*showproject*', '')
        page = page.replace('*user*', session['userid'])
        # mostro la lista dei progetti memorizzati
        values = self._projects_id()
        options = '<select id="projectid" name="projectid">'
        for value in values:
            options += '<option value="' + str(value) + '"'
            if str(value) == project:
                options += ' selected="selected"'
            options += '>'
            options += value
            options += '</option>'
        options += '</select>'
        return page.replace('*projectids*', options)

    def load_web_user(self, user: str):
        """
            Metodo per mostare i dettagli di un singolo utente
        """
        # carico i dati dell'utente
        user_projects = self._model.get_user_projects(user)
        table = '<table id="topics-table"><tr><th>URL</th><th>Priorità</th>\
<th>Labels</th><th>Keywords</th></tr>'
        # per ogni preferenza di progetto, mostro i dettagli
        for user_project in user_projects:
            project_data = self._model.read_project(
                user_project['url']
            )
            project_data['url'] = project_data['url'].lstrip().rstrip()
            row = '<tr>'
            row += '<td><a href="' + project_data['url'] + '\
" target="_blank">' + project_data['url'] + '</a></td>'
            row += '<td>' + str(user_project['priority']) + '</td><td>'
            if user_project.get('topics'):
                for topic in project_data['topics']:
                    if topic in user_project['topics']:
                        row += topic + ','
                row = row[:-1]  # elimino l'ultima virgola
            row += '</td><td>'
            if user_project['keywords']:
                for keyword in user_project['keywords']:
                    row += keyword
                    row += ','
                row = row[:-1]  # elimino l'ultima virgola
            row += '</td></tr>'
            table += row
        table += '</table>'
        return table

    def load_web_project(self, project: str):
        """
            Metodo per mostrare i dettagli di un singolo progetto
        """
        # carico i dati del progetto
        project = self._model.read_project(project)
        # mostro i dati del progetto
        table = '<table id="projects-table"><tr><th>URL</th><th>Name</th>\
<th>App</th><th>Topics</th></tr><tr><td><a href="' + project['url'] + '\
" target="_blank">' + project['url'] + '</a></td>\
<td>' + project['name'] + '</td><td>' + project['app'] + '</td><td>'
        if project.get('topics'):
            for topic in project['topics']:
                table += topic + ','
            table = table[:-1]  # elimino l'ultima virgola
        table += '</td></tr></table>'
        return table

    def web_user(self):
        """
            Metodo per gestire le chiamate HTTP di un client Web alla risorsa
            utente
        """
        # controllo se l'utente ha acceduto al sistema
        if self._check_session():
            # controllo il tipo di richiesta
            if request.method == 'GET':
                page = self.panel()
            elif request.method == 'POST':
                # controllo da dove proviene la richiesta, quindi un sottotipo
                if 'postlogout' in request.values:
                    self.logout()
                    page = self.panel()
                elif 'postuserpanelshow' in request.values:
                    page = self.show_user()
                else:
                    page = self.add_user()
            elif request.method == 'PUT':
                page = self.modify_user()
            elif request.method == 'DELETE':
                page = self.remove_user()
            page = self.removehtml(page)
            try:
                return render_template_string(page)
            except TypeError:
                return page
        else:
            return self.access()

    def web_project(self):
        """
            Metodo per gestire le chiamate HTTP di un client Web alla risorsa
            progetto
        """
        # controllo se l'utente ha acceduto al sistema
        if self._check_session():
            # controllo il tipo della richiesta
            if request.method == 'POST':
                page = self.show_project()
            elif request.method == 'DELETE':
                page = self.remove_project()
            page = self.removehtml(page)
            try:
                return render_template_string(page)
            except TypeError:
                return page
        else:
            return self.access()

    def load_preference_topic(self, message=''):
        """
            Metodo per caricare l'interfaccia delle preferenze legate ai topic
        """
        # carico le preferenze dell'utente
        user_projects = self._model.get_user_projects(session['userid'])
        # costruisco il form
        form = '<form id="topics">\
<fieldset id="topics-fieldset">\
<legend>Modifica preferenze dei topics</legend>\
<table id="topics-table"><tr><th>URL</th><th>Nome progetto</th>\
<th>Applicazione</th><th>Priorità</th><th>Labels</th><th>Keywords</th></tr>'
        for user_project in user_projects:
            project_data = self._model.read_project(
                user_project['url']
            )
            project_data['url'] = project_data['url'].lstrip().rstrip()
            row = '<tr>'
            row += '<td><a href="' + project_data['url'] + '\
" target="_blank">' + project_data['url'] + '</a></td>'
            row += '<td>' + project_data['name'] + '</td>'
            row += '<td>' + project_data['app'] + '</td>'
            row += '<td><select id="priority" name="\
' + project_data['url'] + '-priority">'
            for priority in range(1, 4):
                row += '<option'
                if priority == user_project['priority']:
                    row += ' selected="selected"'
                row += ' value="' + str(priority) + '">\
' + str(priority) + '</option>'
            row += '</select></td><td>'
            if project_data.get('topics'):
                for topic in project_data['topics']:
                    row += '<br/><label>' + topic + '</label>'
                    row += '<input type="checkbox" name="\
' + project_data['url'] + '-topics"'
                    if topic in user_project['topics']:
                        row += ' checked="checked"'
                    row += ' value="' + topic + '">'
            row += '</td><td><textarea id="textkeywords" name="\
' + project_data['url'] + '-keywords"'
            if project_data['app'] == 'redmine':
                row += 'disabled="disabled"'
            row += '>'
            if user_project['keywords']:
                for keyword in user_project['keywords']:
                    row += keyword
                    row += ','
                row = row[:-1]  # elimino l'ultima virgola
            row += '</textarea></td></tr>'
            form += row
        form += '</table><input id="putpreferencetopics" type="button" \
value="Modifica preferenze di progetti e topic"></fieldset></form>'
        form += message
        return form

    def load_preference_project(self, message=''):
        """
            Metodo per caricare l'interfaccia delle preferenze legate ai
            progetti
        """
        # carico i progetti memorizzati
        projects = self._model.projects()
        # costruisco il form
        form = '<form id="projects"><fieldset id="project-fieldset">\
<legend>Aggiungi e rimuovi progetti</legend><select name="project"\
 id="projects-select">'
        for project in projects:
            form += '<option value="' + project['url'] + '">\
' + project['name'] + ' - ' + project['app'] + '</option>'
        form += '</select> <input id="putpreferenceprojectsadd" type="button" \
value="Aggiungi il progetto">\
<input id="putpreferenceprojectsremove" type="button" \
value="Rimuovi il progetto"></fieldset></form>'
        form += message
        return form

    def load_preference_availability(
        self,
        message='',
        year=datetime.datetime.now().year,
        month=datetime.datetime.now().month
    ):
        """
            Metodo per caricare l'interfaccia delle preferenze legate ai
            giorni di irreperibilità
        """
        # carico i giorni del mese a parametro
        date = datetime.datetime(year, month, 1)
        # carico le preferenze dell'utente
        irreperibilita = self._model.read_user(
            session['userid']
        ).get('irreperibilita')
        # costruisco il form
        form = '<form id="availability">\
<fieldset id="availability-fieldset"><legend>Giorni di indisponibilità</\
legend><div id="calendario"></div><p>' + date.strftime("%B") + ' \
' + date.strftime('%Y') + '</p>'
        for day in range(1, calendar.monthrange(year, month)[1]+1):
            date = datetime.datetime(year, month, day)
            form += '<input class="day_checkbox" type="checkbox"\
name="indisponibilita[]" id="day_' + str(date.day) + '" value="\
' + str(date) + '"'
            if irreperibilita and date in irreperibilita:
                form += ' checked="checked"'
            form += '/><label class="day_label" for="day_' + str(date.day) + '\
">' + str(day) + '</label>'
        form += '<br/><input type="button"\
 id="putpreferenceavailabilityprevious" value="Mese precedente"/>\
<input type="button" id="putpreferenceavailabilitynext" value="Mese successivo\
"/><input type="hidden" name="mese" value="' + date.strftime("%m") + '"/>\
<input type="hidden" name="anno" value="' + date.strftime("%Y") + '"/>\
<br/><input id="putpreferenceavailability" type="button"\
 value="Modifica irreperibilità"/></fieldset></form>'
        form += message
        return form

    def load_preference_platform(self, message=''):
        """
            Metodo per caricare l'interfaccia delle preferenze legate
            alla piattaforma
        """
        # carico le preferenze dell'utente
        platform = self._model.read_user(session['userid']).get('preference')
        # costruisco il form
        form = '<form id="platform"><fieldset id="platform-fieldset">\
<legend>Piattaforma preferita</legend>\
<label for="email">Email</label>\
<input name="platform" id="email"\
type="radio" value="email"'
        if(platform == 'email'):
            form += ' checked = "checked"'
        form += '/><label for="telegram">Telegram</label>\
<input name="platform" id="telegram" type="radio" value="telegram"'
        if(platform == 'telegram'):
            form += ' checked = "checked"'
        form += '/><input id="putpreferenceplatform" \
type="button" value="Modifica piattaforma preferita"/></fieldset></form>'
        form += message
        return form

    def modifytopics(self):
        """
            Metodo per modificare le preferenze legate a labels e keywords
        """
        old = None
        # ciclo sui valori passati alla richiesta
        for key, value in request.values.items(multi=True):
            url = key.replace('-priority', '')
            url = url.replace('-topics', '')
            url = url.replace('-keywords', '')
            # controllo se è il primo progetto o se
            # prima label/keyword del nuovo progetto
            if not old or (url != old and url != 'putpreferencetopics'):
                self._model.reset_user_topics(
                    session['userid'],
                    url
                )
                self._model.reset_user_keywords(
                    session['userid'],
                    url
                )
                old = url
            # controllo sia un valore delle preferenze
            if url != 'putpreferencetopics':
                if 'priority' in key:
                    self._model.set_user_priority(
                        session['userid'], url, value
                    )
                elif 'topics' in key:
                    self._model.add_user_topics(
                        session['userid'],
                        url,
                        value
                    )
                elif 'keywords' in key:
                    project_data = self._model.read_project(
                        url
                    )
                    # redmine non ha le keywords
                    if project_data['app'] != 'redmine':
                        if value:
                            value = value.strip()
                            keywords = value.split(',')
                            self._model.add_user_keywords(
                                session['userid'],
                                url,
                                *keywords
                            )
        # costruisco l'interfaccia
        return self.load_preference_topic('<p>Preferenze dei topic aggiornate.\
        </p>')

    def addproject(self):
        """
            Metodo per aggiungere un progetto alle preferenze
        """
        message = '<p>Progetto aggiunto correttamente.</p>'
        # ricevo l'id del progetto
        project = request.values.get('project')
        # se è già presente prevengo l'eccezione
        try:
            if project:
                self._model.add_user_project(session['userid'], project)
            else:
                message = '<p>Nessun progetto selezionato.</p>'
        except AssertionError:
            message = '<p>Il progetto è già presente in lista.</p>'
        # costruisco l'interfaccia
        return self.load_preference_topic(message)

    def removeproject(self):
        """
            Metodo per rimuovere un progetto dalle preferenze
        """
        message = '<p>Progetto rimosso correttamente.</p>'
        # ricevo l'id del progetto
        project = request.values.get('project')
        # se non è già presente prevengo l'eccezione
        try:
            if project:
                self._model.remove_user_project(session['userid'], project)
            else:
                message = '<p>Nessun progetto selezionato.</p>'
        except AssertionError:
            message = '<p>Il progetto non è presente in lista.</p>'
        return self.load_preference_topic(message)

    def indisponibilita(self):
        """
            Metodo per modificare l'irreperibilità di un utente
        """
        # ricevo le date
        giorni = request.values.getlist('indisponibilita[]')
        month = request.values['mese']
        year = request.values['anno']
        # carico le vecchie date memorizzate
        giorni_old = self._model.read_user(
            session['userid']
        ).get('irreperibilita')
        # converto i nuovi giorni in lista
        giorni_new = []
        for giorno in giorni:
            giorni_new.append(
                datetime.datetime.strptime(giorno, '%Y-%m-%d %H:%M:%S')
            )
        # controllo quali giorni eliminare dai vecchi
        if giorni_old:
            for giorno_old in giorni_old:
                if (
                    giorno_old.strftime('%Y') == year and
                    giorno_old.strftime('%m') == month
                ):
                    if (
                        (giorni_new and giorno_old not in giorni_new) or
                        not giorni_new
                    ):
                        self._model.remove_giorno_irreperibilita(
                            session['userid'],
                            int(year),
                            int(month),
                            int(giorno_old.strftime('%d'))
                        )
        # memorizzo i nuovi giorni
        if giorni_new:
            for giorno in giorni_new:
                self._model.add_giorno_irreperibilita(
                    session['userid'],
                    int(year),
                    int(month),
                    int(giorno.strftime('%d'))
                )
        # carico l'interfaccia
        return self.load_preference_availability('<p>Giorni di indisponibilità\
 aggiornati.</p>')

    def previous_indisponibilita(self):
        """
            Metodo per cambiare il mese di irreperibilità al precedente
        """
        # controllo il mese in analisi
        mese = int(request.values['mese'])
        anno = int(request.values['anno'])
        # lo decremento
        if (mese == 1):
            anno = anno - 1
            mese = 12
        else:
            mese = mese - 1
        # memorizzo l'indisponibilità del mese corrente
        self.indisponibilita()
        # carico l'interfaccia
        return self.load_preference_availability('<p>Giorni di indisponibilità\
 aggiornati, mese cambiato.</p>', anno, mese)

    def next_indisponibilita(self):
        """
            Metodo per cambiare il mese di irreperibilità al successivo
        """
        # controllo il mese in analisi
        mese = int(request.values['mese'])
        anno = int(request.values['anno'])
        # lo incremento
        if (mese == 12):
            anno = anno + 1
            mese = 1
        else:
            mese = mese + 1
        # memorizzo l'indisponibilità del mese corrente
        self.indisponibilita()
        # carico l'interfaccia
        return self.load_preference_availability('<p>Giorni di indisponibilità\
 aggiornati, mese cambiato.</p>', anno, mese)

    def piattaforma(self):
        """
            Metodo per modificare la piattaforma di messaggistica preferita
        """
        # ricevo la nuova piattaforma
        platform = request.values['platform']
        if platform == "telegram":
            # controllo se l'id telegram esiste
            telegram = self._model.get_user_telegram_web(session['userid'])
            if not telegram:
                return self.load_preference_platform('<p>Non hai\
 memorizzato la piattaforma telegram nel sistema.</p>')
        if platform == "email":
            # controllo se l'email esiste
            email = self._model.get_user_email_web(session['userid'])
            if not email:
                return self.load_preference_platform('<p>Non hai\
 memorizzato la piattaforma email nel sistema.</p>')
        self._model.update_user_preference(session['userid'], platform)
        return self.load_preference_platform('<p>Piattaforma preferita \
aggiornata correttamente.</p>')

    def modify_preference(self):
        """
            Metodo per modificare una preferenza
        """
        fileHtml = html / 'preference.html'
        page = fileHtml.read_text()
        # controllo quale tipo di preferenza bisogna modificare
        if 'putpreferencepanel' in request.values:
            # controllo l'utente sia iscritto (prevengo logout non effettuati)
            try:
                page = page.replace('*topics*', self.load_preference_topic())
                page = page.replace(
                    '*projects*',
                    self.load_preference_project()
                )
                page = page.replace(
                    '*availability*',
                    self.load_preference_availability()
                )
                page = page.replace(
                    '*platform*',
                    self.load_preference_platform()
                )
            except AssertionError:
                return self.panel(error='Non sei più iscritto alla\
 piattaforma.')
        elif request.values.get('putpreferencetopics'):
            return self.modifytopics()
        elif request.values.get('putpreferenceprojectsadd'):
            return self.addproject()
        elif request.values.get('putpreferenceprojectsremove'):
            return self.removeproject()
        elif request.values.get('putpreferenceavailability'):
            return self.indisponibilita()
        elif request.values.get('putpreferenceavailabilityprevious'):
            return self.previous_indisponibilita()
        elif request.values.get('putpreferenceavailabilitynext'):
            return self.next_indisponibilita()
        elif request.values.get('putpreferenceplatform'):
            return self.piattaforma()
        page = page.replace('*user*', session['userid'])
        return page

    def web_preference(self):
        """
            Metodo per gestire le chiamate HTTP di un client Web alla risorsa
            preferenza
        """
        # controllo se l'utente ha acceduto al sistema
        if self._check_session():
            page = self.modify_preference()
            page = self.removehtml(page)
            try:
                return render_template_string(page)
            except TypeError:
                return page
        else:
            return self.access()

    def removehtml(self, page: str):
        """
            Metodo ausiliario per rimuovere stringhe non utili al caricamento
            dei pannelli
        """
        if 'panel' in request.values:
            page = page.replace("<!DOCTYPE html>", "")
            page = page.replace("<html id=\"html\">", "")
            page = page.replace("</html>", "")
        return page
