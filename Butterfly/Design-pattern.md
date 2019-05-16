#DESIGN PATTERNS

##Strutturali

###Adapter

Lo usiamo nel caso vi siano funzionalità in classi di librerie già esistenti da usare e migliorare, aggiungendo qualcosa in più.

Esito: **Forse**

Dove: **vedere le varie librerie**

###Facade

Lo usiamo nel caso di sistemi complessi, in cui sia necessario accedere a molte componenti distinte insieme. Facade ne nasconde la complessità.

Nel nostro caso non ne vediamo l'esigenza, perché i componenti sono già suddivisi, ben organizzati e non vi è la necessità di far dialogare più dei componenti adiacenti.

Esito: **scartato**

###Decorator

Serve per aggiungere funzionalità in modo dinamico a componenti.

Esito: **scartato**

###Proxy

Serve per controllare accessi, costruire on demand (efficiente), altro.

Esito: **scartato**

###Flyweight

Serve per oggetti a granularità molto fine (Integer, Character...)

Esito: **scartato**

## Creazionali

###Singleton

Va usato se si ha una singola istanza che si vuole mantenere univoca.

Esito: **valutare per gestore personale**

###Builder

Boh


###Abstract Factory

Va usato con famiglie di oggetti.

Esempio: Redmine e GitLab sono due famiglie di Producer, mentre Telegram ed email sono famiglie di Consumer.

Esito: **Valutare se questo o Template Method**

##Comportamentali

###Command

Serve per incapsulare la richiesta di un oggetto verso un altro. Si "salvano" più comandi e un Invoker li invoca a un certo punto.

Esito: **Valutare per gestore personale (da model a db?)**

###Iterator

Serve per un normale iteratore.

Esito: **Usarlo per strutture iterative (liste), ma in python le scorri con un comando...?**

###Observer

