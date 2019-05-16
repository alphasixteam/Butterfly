"""
File: webhook.py
Data creazione: 2019-02-15

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

Versione: 0.1.1
Creatore: Timoty Granziero, timoty.granziero@gmail.com
"""

from abc import ABC, abstractmethod


class Webhook(ABC):
    """Interfaccia `Webhook`"""

    @abstractmethod
    def parse(self, whook: dict):
        """Parsing del file `JSON` associato al webhook. Restituisce un
        `dict` contenente i campi di interesse.
        """
