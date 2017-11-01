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

Copyright © 2016 Stéphane Veyret stephane_DOT_veyret_AT_neptura_DOT_org

:us: :gb:

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see http://www.gnu.org/licenses/.

:fr:

Ce programme est un logiciel libre ; vous pouvez le redistribuer ou le modifier suivant les termes de la GNU General Public License telle que publiée par la Free Software Foundation ; soit la version 3 de la licence, soit (à votre gré) toute version ultérieure.

Ce programme est distribué dans l'espoir qu'il sera utile, mais SANS AUCUNE GARANTIE ; sans même la garantie tacite de QUALITÉ MARCHANDE ou d'ADÉQUATION à UN BUT PARTICULIER. Consultez la GNU General Public License pour plus de détails.

Vous devez avoir reçu une copie de la GNU General Public License en même temps que ce programme ; si ce n'est pas le cas, consultez http://www.gnu.org/licenses.

# Pré-requis

Pour utiliser ce greffon, vous devez avoir :
* l'interface en ligne de commande pour [Grammalecte](http://grammalecte.net/?download_div) téléchargée et installée sur la machine ;
* une version de _pluma_ capable d'exécuter les greffons Python (cela peut nécessiter une compilation particulière) ;
* et, bien sûr, les installations Python 2 (2.7 minimum) et Python 3 (3.3 minimum) nécessaires au fonctionnement de ces deux pré-requis.

# Installation

Téléchargez la version désirée sur [la page des _releases_](https://github.com/sveyret/pluma-grammalecte/releases), au format _zip_ ou _tar.gz_, puis décompressez-la dans le répertoire de votre choix.

La compilation et l'installation du greffon se fait à l'aide des commandes :

    make && make install

Par défaut, l'installation se fera pour tout le système, et nécessite donc les droits d'administration sur la machine. Si vous souhaitez une installation différente, vous pouvez utiliser les variables :
* `DESTDIR` pour faire une installation dans un répertoire différent, généralement utilisé en phase de _stage_ avant une installation réelle,
* `LOCALE_INSTALL` pour indiquer le répertoire d'installation des traductions,
* `PLUGIN_INSTALL` pour indiquer le répertoire d'installation du greffon.

Pour une installation en local, vous pouvez, par exemple, exécuter la commande :

    make && make LOCALE_INSTALL=$HOME/.local/share/locale PLUGIN_INSTALL=$HOME/.local/share install

Dans ce dernier cas, il vous faudra modifier la configuration du greffon en éditant (ou créant, si nécessaire) le fichier `$HOME/.config/pluma/grammalecte.conf`. Ce fichier est au format JSON. Les valeurs qui vous seront les plus utiles sont `locale-dir` pour indiquer le répertoire d'installation des traductions et `grammalecte-cli` si votre installation de l'interface de Grammalecte ne se trouve pas à l'emplacement prévu par défaut `/opt/grammalecte/cli.py`.

Exemple :

    > cat ~/.config/pluma/grammalecte.conf
    { "locale-dir": "/home/user/.local/share/locale", "g-cli": "/home/user/grammalecte/cli.py" }

# Utilisation

Pour le moment, le greffon se contente de souligner en temps réel (ou presque !) les erreurs d'orthographe ou grammaire dans _pluma_ lorsque la vérification automatique est activée. Pour activer ou désactiver la vérification automatique, utilisez l'option « Vérification automatique » dans le menu « Outils ». Par défaut, l'option est désactivée, mais si vous l'activez pour un fichier donné, elle le restera pour ce fichier, même après sa fermeture.

## Configuration

La configuration de Grammalecte est écrite dans des fichiers JSON. Ces fichiers se trouvent :
* pour la configuration globale au système, dans `/etc/pluma/grammalecte.conf` ;
* pour la configuration spécifique à l'utilisateur, dans `$HOME/.config/pluma/grammalecte.conf` ;
* pour la configuration spécifique à un fichier, dans les métadonnées du fichier.

Chaque fichier de configuration peut surcharger les valeurs présentes dans le fichier plus global. À contrario, une valeur non définie dans le fichier plus précis sera recherchée dans le fichier plus global.

Les paramètres configurables sont les suivants :
* `locale-dir` contient le chemin vers le répertoire des traductions ;
* `analyze-options` contient les options d'analyse et leurs valeurs ;
* `auto-analyze-active` indique si la vérification automatique est activée ou non ;
* `auto-analyze-timer`<sup>*</sup> contient la fréquence de rafraichissement pour l'analyse automatique.
* `g-python-exe` contient l'exécutable Python 3, utilisé pour Grammalecte (utile si votre installation Python 3 n'est pas dans le PATH ou a un nom particulier) ;
* `g-cli` contient le chemin complet vers la ligne de commande de Grammalecte ;
* `g-cli-params`<sup>*</sup> contient des paramètres à utiliser avec la ligne de commande de Grammalecte ;
* `g-analyze-params`<sup>*</sup> contient les paramètres utilisés pour l'analyse par Grammalecte ;
* `g-options-params`<sup>*</sup> contient les paramètres utilisés pour la recherche des options de Grammalecte ;
* `g-options-regex`<sup>*</sup> est l'expression rationnelle permettant l'extraction des résultats de Grammalecte pour la recherche des options.

[*] Les options marquées d'un <sup>*</sup> sont pour les utilisateurs avertis uniquement, à ne modifier que si vous savez ce que vous faites !

# À faire

## Version 0.3

- [ ] Ajouter l'IHM pour modifier la configuration de Grammalecte.

### Version 0.4

- [ ] Afficher une info-bulle sur les erreurs.
- [ ] Gérer le clic-droit avec la souris sur les erreurs (suggestions, ignorer, etc.)

### Version 1.0

- [ ] Ajouter une correction interactive.

### Autre

- [ ] Se débarrasser de l'avertissement : g_autocorrect.py:174: GtkWarning: IA__gtk_text_iter_set_line_offset: assertion 'char_on_line <= chars_in_line' failed
  iterator.set_line_offset(errorDesc[offset])
- [ ] Optimiser la correction (n'envoyer qu'un seul paragraphe lorsque possible).

