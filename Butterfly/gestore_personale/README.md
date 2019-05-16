# Gestore Personale
Il **Gestore Personale** è la componente del sistema **Butterfly** usata per la gestione dei dati relativi a **utenti** e **progetti**. Per svolgere il suo scopo tale componente è stata suddivisa in due sottocomponenti, **client** e **controller**, rispettivamente per la gestione delle interazioni con le code di Kafka e con l'utente.

## Client
**Gestore Personale Client** : [![Automated build](https://img.shields.io/docker/cloud/automated/alphasix/gestore-personale-client.svg)](https://cloud.docker.com/u/alphasix/repository/docker/alphasix/gestore-personale-client) [![Build status](https://img.shields.io/docker/cloud/build/alphasix/gestore-personale-client.svg)](https://cloud.docker.com/u/alphasix/repository/docker/alphasix/gestore-personale-client) [![Pulls](https://img.shields.io/docker/pulls/alphasix/gestore-personale-client.svg)](https://cloud.docker.com/u/alphasix/repository/docker/alphasix/gestore-personale-client)

Questa sottocomponente del Gestore Personale è configurata in modo da rimanere in ascolto sulle code di Kafka in output dai **Producer Redmine** e **GitLab**. Quando arriva un messaggio relativo a una issue o a un commit, esso viene scomposto e confrontato con i dati salvati sul database **MongoDB** relativi ai progetti.
In caso il progetto non esista, esso viene automaticamente salvato. In caso contrario il messaggio viene inoltrato agli utenti interessati a seconda della priorità di progetto impostata e delle preferenze impostate attraverso il **Controller**.

## Controller
**Gestore Personale** : [![Automated build](https://img.shields.io/docker/cloud/automated/alphasix/gestore-personale.svg)](https://cloud.docker.com/u/alphasix/repository/docker/alphasix/gestore-personale) [![Build status](https://img.shields.io/docker/cloud/build/alphasix/gestore-personale.svg)](https://cloud.docker.com/u/alphasix/repository/docker/alphasix/gestore-personale) [![Pulls](https://img.shields.io/docker/pulls/alphasix/gestore-personale.svg)](https://cloud.docker.com/u/alphasix/repository/docker/alphasix/gestore-personale)

Questa sottocomponente resta in ascolto attraverso un server HTTP utilizzando la libreria Flask delle richieste degli utenti, che possono modificare i propri dati e le proprie preferenze relative ai progetti, ai giorni di irreperibilità e alla piattaforma di messaggistica preferita.
Gli utenti amministratori possono inoltre aggiungere altri utenti, rimuovere progetti e preferenze associate e visualizzare nel dettaglio tutti i dati relativi a utenti e progetti esistenti.

### Web
Questa sottocomponente del controller viene usata per gestire le richieste provenienti da un client Web. Viene usata attraverso l'interfaccia Web.

### Api
Questa sottocomponente del controller viene usata per gestire le richieste provenienti da un client HTTP qualsiasi con supporto al formato JSON.
Le richieste effettuate devono rispettare lo stile architetturale REST secondo le regole illustrate nel Manuale Utente.

# API REST

Per la gestione delle risorse di Butterfly abbiamo utilizzato lo standard architetturale delle API Rest.
Il root path sottinteso sarà sempre homeUrl/api/v1/.
Ad esempio, per effettuare la GET dell'user `@user1`, l'indirizzo sarà:
    
    GET \homeUrl/api/v1/user/@user1

## User

**User** è la risorsa utente. È possibile visualizzare, aggiungere, modificare o rimuovere gli utenti tramite una semplice richiesta HTTP.

### Visualizzazione
È possibile visualizzare i dati di un utente tramite la richiesta:
	
    GET  /user/<id>
    
**Esempio di input**
Un esempio di richiesta è
   
    GET  /user/abcd@bc.it
    
senza alcun dato nel payload della richiesta.

**Esempio di output**
In caso la richiesta vada a buon fine, un esempio di output è:
        
    {
        "_id": {
            "$oid": "5cd07bb9c331755af7f5ea00"
        },
        "name": "Mattia",
        "surname": "Cruciani",
        "email": "abcd@bc.it",
        "telegram": "1234",
        "admin": false,
        "preference": "email",
        "irreperibilita": [
            {
                "$date": "2018-12-05"
            },
            {
                "$date": "2019-04-08"
            },
            {
                "$date": "2019-04-15"
            },
            {
                "$date": "2019-04-07"
            },
            {
                "$date": "2019-06-07"
            },
            {
                "$date": "2019-06-08"
            },
            {
                "$date": "2019-06-09"
            }
        ],
        "projects": [
            {
                "url": "http://localhost/gitlab/gitlab-2",
                "priority": 2,
                "topics": [
                    "java",
                    "coding",
                    "criptovaluta"
                ],
                "keywords": [
                    "kw1",
                    "kw2",
                    "kw3"
                ]
            }
        ]
    }
        

Nel caso l'utente richiesto non venga trovato, verrà restituito il seguente messaggio:
        
    {
        "error": "Utente inesistente."
    }
 
### Inserimento
È possibile inserire un nuovo utente tramite la richiesta:
    
    POST /user

È inoltre possibile dare i seguenti campi di tipo stringa alla richiesta, per aggiungere in fase di creazione i dati:
- `name`
- `surname`
- `telegram`
- `email`

Almeno uno tra i campi `Email` e `ID Telegram` vanno fornite insieme al payload.

**Esempio di input**
Un esempio di richiesta è

    POST  /user
    
con i seguenti dati nel corpo della richiesta
    
    {
        "name": "Matteo",
        "surname": "Marchiori",
        "email": "matteo.marchiori97@gmail.com",
        "telegram": "123456"
    }
        
**Esempio di output**
In caso la richiesta vada a buon fine, verrà restituito il seguente messaggio
        
    {
        "ok": "Utente inserito correttamente"
    }
        
Nel caso l'utente da inserire esista già, verrà restituito il seguente messaggio

    {
        "error": "L'utente inserito esiste già."
    }

Nel caso non vengano inseriti almeno email o telegram, verrà restituito il seguente messaggio

    {
        "error": "Si prega di inserire almeno email o telegram per inserire l'utente."
    }
    

### Modifica

È possibile modificare un utente tramite la richiesta

    PUT /user/<id>

È possibile dare i seguenti campi di tipo stringa alla richiesta, per aggiungere in fase di modifica i dati:
- `name`
- `surname`
- `telegram`
- `email`

**Esempio di input**
Un esempio di richiesta è

    PUT /user/1234

con i seguenti dati nel corpo della richiesta:
    	
    {
        "name": "Marco",
        "surname": "Rossi",
        "telegram": "1235"
    }

**Esempio di output**
In caso la richiesta vada a buon fine, verrà restituito il seguente messaggio
    
    {
        "ok": "Utente modificato correttamente"
    }

In caso non vengano forniti almeno Email o ID Telegram, verrà restituito il seguente messaggio
   
    {
        "error": "Si prega di inserire almeno email o telegram per modificare l'utente."
    }
    
In caso almeno uno degli identificativi forniti coincida con quello di un altro utente, verrà restituito il seguente messaggio
    
    {
        "error": "I dati inseriti confliggono con altri già esistenti."
    }
	
### Rimozione

È possibile rimuovere un utente dal sistema \progetto\ con la richiesta
    
    DELETE /user/<id>

Se il campo `<id>` corrisponde a un ID presente nel sistema, esso verrà rimosso.

**Esempio di input**
Un esempio di richiesta è

    DELETE  /user/abcd@bc.it

senza alcun dato nel payload della richiesta.

**Esempio di output**
In caso la richiesta vada a buon fine, verrà restituito il seguente messaggio:
	
    {
        "ok": "Utente rimosso correttamente"
    }
	
### Project
Project è la risorsa relativa ai progetti. È possibile visualizzare o rimuovere i progetti tramite una semplice richiesta HTTP.

## Visualizzazione
È possibile visualizzare i progetti tramite la richiesta

    GET /project/<id>
    
Se il campo `<id>` corrisponde a un progetto, verranno mostrati i dati relativi a tale progetto.

**Esempio di input**
Un esempio di richiesta è

    GET /project/http://localhost/gitlab/gitlab-2
    
senza alcun dato nel \gloss{payload} della richiesta.

**Esempio di output**
In caso la richiesta vada a buon fine, un esempio di output è:
    
    {
        "_id": {
            "$oid": "5cd1b509c331756598e9c00b"
        },
        "url": "http://localhost/gitlab/gitlab-2",
        "name": "Gitlab-2",
        "app": "gitlab",
        "topics": [
            "java",
            "coding",
            "enhancement",
            "bug"
        ]
    }
    
In caso il progetto richiesto non esista, verrà restituito il seguente messaggio:
    
    {
        "error": "Progetto inesistente."
    }
	
### Rimozione

È possibile rimuovere un progetto dal sistema Butterfly con la richiesta
    
    DELETE /project/<id>

Se il campo `<id>` corrisponde a un progetto, esso verrà rimossa dal sistema.

**Esempio di input**
Un esempio di richiesta è

    DELETE /project/http://localhost/gitlab/gitlab-2

senza alcun dato nel \gloss{payload} della richiesta.

**Esempio output**
In caso la richiesta vada a buon fine, verrà restituito il seguente messaggio
    
    {
        "ok": "Progetto rimosso correttamente"
    }
        


# Popolazione del database o reset
Prima di popolare il database essere sicuri che il controller sia collegato correttamente all'istanza di MongoDB e che questa sia configurata correttamente come come scritto nel [README](https://github.com/Vashy/AlphaSix/tree/develop/Butterfly/mongo_db/README.md) apposito.
Per popolare il database al primo avvio, posizionarsi in `Butterfly/` e dare il comando:

    $ python3 -m mongo_db.populate

Questo popola il database con l'utente amministratore e i suoi dati presenti nel file `config.json` presenti nella cartella `Butterfly/mongo_db/`.

# Avvio del controller
Per avviare il controller, posizionarsi in `Butterfly/` e dare il comando

    $ python3 -m gestore_personale.controller

Tale comando inizializza il server HTTP Flask, che resta in ascolto delle richieste dei client. Questo viene comunque lanciato all'istanziazione del container.

# Avvio del client
Per avviare il client, posizionarsi in `Butterfly/` e dare il comando

    $ python3 -m gestore_personale.client

Tale comando fa partire la parte Processor. Questo viene comunque lanciato all'istanziazione del container.


Per vedere l'installazione e la configurazione che è stata effettuata per la proponente vi rimandiamo ai documenti Manuale Utente e Manuale Sviluppatore rilasciati insieme al prodotto.
