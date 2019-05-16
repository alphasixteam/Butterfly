# Consumer

Il Consumer è il componente finale del sistema Butterfly. Esso resta in ascolto della sua coda specifica di Kafka per applicativo (e.g. Telegram, Email). Si occupa di inoltrare il messaggio al destinatario finale.

## Consumer Email [![Automated build](https://img.shields.io/docker/cloud/automated/alphasix/consumer-email.svg)](https://cloud.docker.com/u/alphasix/repository/docker/alphasix/consumer-email) [![Build status](https://img.shields.io/docker/cloud/build/alphasix/consumer-email.svg)](https://cloud.docker.com/u/alphasix/repository/docker/alphasix/consumer-email) [![Pulls](https://img.shields.io/docker/pulls/alphasix/consumer-email.svg)](https://cloud.docker.com/u/alphasix/repository/docker/alphasix/consumer-email)

Il Consumer Email si occupa di prelevare i messaggi all'interno della coda "email" in Kafka ed inoltrarli ai destinatari appropriati in base all'indirizzo Email indicato dal destinatario. La mail viene inviata dall'account specificato nei file di [configurazione](config.json) e la sua password viene definita tramite variabile di ambiente definita all'interno del Dockerfile.
## Consumer Telegram [![Automated build](https://img.shields.io/docker/cloud/automated/alphasix/consumer-telegram.svg)](https://cloud.docker.com/u/alphasix/repository/docker/alphasix/consumer-telegram) [![Build status](https://img.shields.io/docker/cloud/build/alphasix/consumer-email.svg)](https://cloud.docker.com/u/alphasix/repository/docker/alphasix/consumer-email) [![Pulls](https://img.shields.io/docker/pulls/alphasix/consumer-telegram.svg)](https://cloud.docker.com/u/alphasix/repository/docker/alphasix/consumer-telegram)

Il Consumer Telegram si occupa di prelevare i messaggi all'interno della coda "telegram" in Kafka ed inoltrarli ai destinatari appropriati in base all'ID Telegram dei destinatati.

Per individurare il proprio ID Telegram è consigliato usare [MyIDBot](tg://resolve?domain=storebot&start=myidbot) ed eseguire il comando `/getid`.

Per vedere l'installazione e la configurazione che è stata effettuata per la proponente vi rimandiamo ai documenti Manuale Utente e Manuale Sviluppatore rilasciati insieme al prodotto.