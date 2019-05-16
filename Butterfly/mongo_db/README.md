# MongoDB

Per il corretto funzionamento del prodotto è necessario avere un'istanza di MongoDB configurata correttamente e visibile dal Gestore Personale oppure avere `mongodb` corretamente installato in locale.

In caso di esecuzione in locale, per avviare il daemon di MongoDB, dare il comando:

    $ sudo service mongod start
    
L'immagine che è stata scelta per istanziare MongoDB è quella della [repository ufficiale di Mongo](https://hub.docker.com/_/mongo) ed è la versione **4.0.9**.

# Popolare il Database

Dall'interno dell'istanza del controller del Gestore Personale alla cartella `Butterfly/`, dare il comando:

    $ python3 -m mongo_db.populate

per popolare il database, attraverso il file `db.json`.

# Configurazione

È importante quando si utilizza un'istanza non in locale di MongoDB modificare il file `etc/mongod.conf.orig` in modo tale che si possano effettuare richieste in remoto.

	# network interfaces
	net:
		port: 27017
		# bindIp: 127.0.0.1
		bindIp: 0.0.0.0
		
Per indicare al controller del Gestore Personale l'indirizzo dell'istanza di MongoDB modificare il file di configurazione `config.json` nella cartella mongo_db.

	{
    	"mongo": {
	        "ip": "localhost",
	        "port": 27017,
        	"database": "butterfly"
	    }
	}

# Lanciare i test

Dalla cartella `Butterfly/` dare il comando:

    $ python3 -m mongo_db.tests.db_controller_test

Per i test verrà creato un Database clone.