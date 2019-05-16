# Producer

Il Producer è il componente che resta in ascolto degli webhook provenienti dal suo applicativo specifico (e.g. Redmine, GitLab). Ha lo scopo di immettere i messaggi su Kafka in formato JSON, conservando solo i campi di interesse e aggiungendone eventualmente di propri.

## GitLab Producer [![Automated build](https://img.shields.io/docker/cloud/automated/alphasix/producer-gitlab.svg)](https://cloud.docker.com/u/alphasix/repository/docker/alphasix/producer-gitlab) [![Build status](https://img.shields.io/docker/cloud/build/alphasix/producer-gitlab.svg)](https://cloud.docker.com/u/alphasix/repository/docker/alphasix/producer-gitlab) [![Pulls](https://img.shields.io/docker/pulls/alphasix/producer-gitlab.svg)](https://cloud.docker.com/u/alphasix/repository/docker/alphasix/producer-gitlab)
Il Producer di GitLab si occupa di ascoltare gli webhook provenienti dai progetti di GitLab che hanno configurato la porta relativa al componente, e di immettere nella coda "gitlab" di Kafka i messaggi.

## Redmine Producer [![Automated build](https://img.shields.io/docker/cloud/automated/alphasix/producer-redmine.svg)](https://cloud.docker.com/u/alphasix/repository/docker/alphasix/producer-redmine) [![Build status](https://img.shields.io/docker/cloud/build/alphasix/producer-gitlab.svg)](https://cloud.docker.com/u/alphasix/repository/docker/alphasix/producer-gitlab) [![Pulls](https://img.shields.io/docker/pulls/alphasix/producer-redmine.svg)](https://cloud.docker.com/u/alphasix/repository/docker/alphasix/procuder-redmine)

Il Producer di Redmine si occupa di ascoltare gli webhook provenienti dai progetti di Redmine che hanno configurato la porta relativa al componente, e di immettere nella coda "redmine" di Kafka i messaggi.

Per vedere l'installazione e la configurazione che è stata effettuata per la proponente vi rimandiamo ai documenti Manuale Utente e Manuale Sviluppatore rilasciati insieme al prodotto.