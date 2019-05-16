"""
File: roducer.py
Data creazione: 2019-02-18

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

Versione: 0.3.1
Creatore: Timoty Granziero, timoty.granziero@gmail.com
Autori:
    Laura Cameran, lauracameran@gmail.com
    Samuele Gardin, samuelegardin@gmail.com
"""

from producer.producer import Producer


class RedmineProducer(Producer):
    """Classe concreta `RedmineProducer`. Implementa `Producer`.
    """

    def webhook_kind(self, whook: dict):
        """Restituisce il tipo di segnalazione (Per Redmine c'è solo 'issue', al momento).
        """

        return 'issue'
