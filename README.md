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

# Aperçu

![Infobulle](https://user-images.githubusercontent.com/6187210/32458521-fd71a990-c32c-11e7-8b2b-43764d608480.png)

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

Dans ce dernier cas, il vous faudra modifier la configuration du greffon en éditant (ou créant, si nécessaire) le fichier `$HOME/.config/pluma/grammalecte.conf`. Ce fichier est au format JSON. Les valeurs qui vous seront les plus utiles sont `locale-dir` pour indiquer le répertoire d'installation des traductions et `g-cli` si votre installation de l'interface de Grammalecte ne se trouve pas à l'emplacement prévu par défaut `/opt/grammalecte/cli.py`.

Exemple :

    > cat ~/.config/pluma/grammalecte.conf
    { "locale-dir": "/home/user/.local/share/locale", "g-cli": "/home/user/grammalecte/cli.py" }

# Utilisation

## Vérification automatique

Lorsque la vérification automatique est activée, le greffon souligne en temps réel les erreurs d'orthographe ou grammaire dans _pluma_. Lorsque le curseur de la souris survole une erreur, une bulle d'information est affiché pour expliquer le problème détecté. Pour activer ou désactiver la vérification automatique, utilisez l'option « Vérification linguistique automatique » dans le menu « Outils ». Par défaut, l'option est désactivée, mais si vous l'activez pour un fichier donné, elle le restera pour ce fichier, même après sa fermeture.

## Menu contextuel

Lorsque le curseur est sur une erreur, l'éventuel menu contextuel est enrichi d'un nouveau sous-menu « Suggestions ». Ce sous-menu contient les options suivantes :
* la liste des suggestions liées à l'erreur, afin de remplacer l'erreur par une proposition ;
* `Ignorer la règle` qui permet de signaler à Grammalecte de ne plus afficher d'erreur par rapport à cette règle de grammaire dans le document en cours ;
* `Ignorer l'erreur` pour que cette erreur ne soit plus signalée dans le document en cours (si un même contexte d'erreur est trouvé plusieurs fois dans le fichier, il sera ignoré à chaque fois — le contexte d'erreur correspond à ce qui est affiché dans l'info-bulle lorsque le curseur survole l'erreur) ;
* `Ajouter` permet d'ajouter l'erreur dans le dictionnaire personnel afin qu'elle ne soit plus détectée quel que soit le document (l'action est en fait la même que pour `Ignorer l'erreur` mais la configuration est enregistrée dans la configuration de l'utilisateur et non dans les métadonnées du fichier) ;
* `Voir la règle` ouvre une page Internet si un lien est fourni avec la règle de grammaire.

## Configurer

Pour sélectionner les options utilisées avec Grammalecte, vous pouvez aller dans le menu « Outils » et choisir l'option « Configurer Grammalecte... ». Une fenêtre présente alors les options disponibles que vous pouvez cocher ou non. Notez que vous pouvez sélectionner des options différentes par défaut (en choisissant « Global ») et pour le fichier en cours (en choisissant son nom). Les options globales seront enregistrées dans votre configuration utilisateur, tandis que les options spécifiques au fichier se retrouveront dans ses métadonnées. Il est possible de supprimer toute la configuration (options spécifiques, règles ou erreurs ignorées, etc.) d'un fichier depuis cette boite de dialogue à l'aide du bouton « Effacer ».

# Configuration

La configuration de Grammalecte est écrite dans des fichiers JSON. Ces fichiers se trouvent :
* pour la configuration globale au système, dans `/etc/pluma/grammalecte.conf` ;
* pour la configuration spécifique à l'utilisateur, dans `$HOME/.config/pluma/grammalecte.conf` ;
* pour la configuration spécifique à un fichier, dans les métadonnées du fichier.

Chaque fichier de configuration peut surcharger les valeurs présentes dans le fichier plus global. À contrario, une valeur non définie dans le fichier plus précis sera recherchée dans le fichier plus global.

Les paramètres configurables sont les suivants :
* `locale-dir` contient le chemin vers le répertoire des traductions ;
* `analyze-options` contient les options d'analyse et leurs valeurs ;
* `auto-analyze-active` indique si la vérification automatique est activée ou non ;
* `auto-analyze-timer`<sup>1</sup> contient la fréquence de rafraichissement pour l'analyse automatique ;
* `analyze-wait-ticks`<sup>1</sup> contient la durée de carence (en dixièmes de seconde) sans évènement avant de lancer l'analyse automatique ;
* `ign-rules`<sup>2</sup> contient les règles qui sont ignorés par Grammalecte ;
* `ign-errors`<sup>2</sup> contient les erreurs (orthographe ou grammaire) qui doivent être ignorés ;
* `g-python-exe` contient l'exécutable Python 3, utilisé pour Grammalecte (utile si votre installation Python 3 n'est pas dans le PATH ou a un nom particulier) ;
* `g-cli` contient le chemin complet vers la ligne de commande de Grammalecte ;
* `g-cli-params`<sup>1</sup> contient des paramètres à utiliser avec la ligne de commande de Grammalecte ;
* `g-analyze-params`<sup>1</sup> contient les paramètres utilisés pour l'analyse par Grammalecte ;
* `g-options-params`<sup>1</sup> contient les paramètres utilisés pour la recherche des options de Grammalecte ;
* `g-options-regex`<sup>1</sup> est l'expression rationnelle permettant l'extraction des résultats de Grammalecte pour la recherche des options.

[1] Ces options sont pour les utilisateurs avertis uniquement, à ne modifier que si vous savez ce que vous faites !

[2] Ces options se cumulent au niveau des différents fichiers, c'est-à-dire que les tableaux définis à un niveau du dessus sont complétés et non remplacés par ceux du niveau inférieur.

# À faire

## Version 1.0

- [ ] Ajouter un moyen d'éditer le « dictionnaire personnel ».
- [ ] Lors d'un remplacement de mot, supprimer l'erreur du stock et ajuster le stock pour prendre en compte le décalage au niveau des caractères (ajoutés ou supprimés selon la longueur du mot de remplacement).
- [ ] Ajouter des suggestions pour les fautes d'orthographe.
- [ ] Ajouter une correction interactive.

## Autre

- [ ] Optimiser la correction (n'envoyer qu'un seul paragraphe lorsque possible).

