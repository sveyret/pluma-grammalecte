# pluma-grammalecte

pluma-grammalecte est un greffon permettant l'intégration du correcteur grammatical _Grammalecte_ dans l'éditeur _pluma_.

# Language/langue

:us: :gb:

Grammalecte is a French language grammar checker. Therefore, it is supposed that anyone interrested by this project has at least basic knowledge of French. That's why all documentation is in French only.

Anyway, because English is the language of programming, the code, including variable names and comments, are in English.

:fr:

Grammalecte est un correcteur grammatical pour la langue française. Aussi, on suppose que toute personne intéressée par ce projet a au moins une connaissance basique du français. C'est pourquoi toute la documentation est uniquement en français.

Toutefois, l'anglais étant la langue de la programmation, le code source, incluant les noms de variables et les commentaires, sont en anglais.

# Licence

:us: :gb:

Copyright © 2016 Stéphane Veyret stephane_DOT_veyret_AT_neptura_DOT_org

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see http://www.gnu.org/licenses/.

:fr:

Ce programme est un logiciel libre ; vous pouvez le redistribuer ou le modifier suivant les termes de la GNU General Public License telle que publiée par la Free Software Foundation ; soit la version 3 de la licence, soit (à votre gré) toute version ultérieure.

Ce programme est distribué dans l'espoir qu'il sera utile, mais SANS AUCUNE GARANTIE ; sans même la garantie tacite de QUALITÉ MARCHANDE ou d'ADÉQUATION à UN BUT PARTICULIER. Consultez la GNU General Public License pour plus de détails.

Vous devez avoir reçu une copie de la GNU General Public License en même temps que ce programme ; si ce n'est pas le cas, consultez http://www.gnu.org/licenses.

# Pré-requis

Pour utiliser ce greffon, vous devez avoir :
* l'interface en ligne de commande pour Grammalecte installée sur la machine ;
* une version de _pluma_ compilée avec la possibilité d'exécuter les greffons Python ;
* et, bien sûr, les installations Python 2 et Python 3 nécessaires au fonctionnement de ces deux pré-requis.

# Installation

La compilation et l'installation du greffon se fait à l'aide des commandes :

    make && make install

Par défaut, l'installation se fera pour tout le système, et nécessite donc les droits d'administration sur la machine. Si vous souhaitez une installation différente, vous pouvez utiliser les variables :
* `DESTDIR` pour faire une installation dans un répertoire différent, généralement utilisé en phase de _stage_ avant une installation réelle,
* `LOCALE_INSTALL` pour indiquer le répertoire d'installation des traductions,
* `PLUGIN_INSTALL` pour indiquer le répertoire d'installation du greffon.

Pour une installation en local, vous pouvez, par exemple, exécuter la commande :

    make && make LOCALE_INSTALL=$HOME/.local/share/locale PLUGIN_INSTALL=$HOME/.local/share install

Dans ce dernier cas, il vous faudra modifier la configuration du greffon en éditant (ou créant, si nécessaire) le fichier `$HOME/.config/pluma/grammalecte.conf`. Ce fichier est au format JSON. Les valeur qui vous seront le plus utiles sont `locale-dir` pour indiquer le répertoire d'installation des traductions et `grammalecte-cli` si votre installation de l'interface de Grammalecte ne se trouve pas à l'emplacement prévu par défaut `/opt/grammalecte/cli.py`.

Exemple :

    > cat ~/.config/pluma/grammalecte.conf
    { "locale-dir": "/home/user/.local/share/locale", "grammalecte-cli": "/home/user/grammalecte/cli.py" }

# Utilisation

Pour le moment, le greffon se contente de souligner les erreurs d'orthographe ou grammaire dans _pluma_ lorsqu'il est activé.

## Configuration

La configuration de Grammalecte est écrite dans des fichiers JSON. Ces fichiers se trouvent :
* pour la configuration globale au système, dans `/etc/pluma/grammalecte.conf` ;
* pour la configuration spécifique à l'utilisateur, dans `$HOME/.config/pluma/grammalecte.conf` ;
* pour la configuration spécifique à un fichier, dans un fichier (caché) nommé comme le fichier, mais préfixé par un point et suffixé par `-grammalecte`.

Chaque fichier de configuration peut surcharger les valeurs présentes dans le fichier plus global. À contrario, une valeur non définie dans le fichier plus précis sera recherchée dans le fichier plus global.

Les paramètres configurables sont :
* `grammalecte-cli` qui contient le chemin complet vers la ligne de commande de Grammalecte ;
* `locale-dir` qui contient le chemin vers le répertoire des traductions ;
* `grammalecte-python-exe` qui contient l'exécutable Python 3, utilisé pour Grammalecte (utile si votre installation Python 3 n'est pas dans le PATH ou a un nom particulier) ;
* `grammalecte-analyze-params` qui contient les paramètres utilisés pour l'analyse par Grammalecte (pour utilisateurs avertis uniquement) ;
* `grammalecte-analyze-timer` qui contient la fréquence de rafraichissement de Grammalecte (pour utilisateurs avertis uniquement).

# Voir aussi

Ce greffon _pluma_ s'appuie sur [l'analyseur grammatical Grammalecte](https://www.dicollecte.org/).

# À faire

- [ ] Faire tout l'IHM.
- [ ] Trier les résultats ?
- [ ] Se débarrasser de l'avertissement : g_autocorrect.py:174: GtkWarning: IA__gtk_text_iter_set_line_offset: assertion 'char_on_line <= chars_in_line' failed
  iterator.set_line_offset(errorDesc[offset])

