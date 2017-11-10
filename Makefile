# This file is part of pluma-grammalecte.
#
# pluma-grammalecte is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# pluma-grammalecte is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# pluma-grammalecte. If not, see <http://www.gnu.org/licenses/>.
#
# Ce fichier fait partie de pluma-grammalecte.
#
# pluma-grammalecte est un logiciel libre ; vous pouvez le redistribuer ou le
# modifier suivant les termes de la GNU General Public License telle que
# publiée par la Free Software Foundation ; soit la version 3 de la licence,
# soit (à votre gré) toute version ultérieure.
#
# pluma-grammalecte est distribué dans l'espoir qu'il sera utile, mais SANS
# AUCUNE GARANTIE ; sans même la garantie tacite de QUALITÉ MARCHANDE ou
# d'ADÉQUATION à UN BUT PARTICULIER. Consultez la GNU General Public License
# pour plus de détails.
#
# Vous devez avoir reçu une copie de la GNU General Public License en même
# temps que pluma-grammalecte ; si ce n'est pas le cas, consultez
# <http://www.gnu.org/licenses>.

# Directories
TARGET_DIR=target
LOCALE_DIR=$(TARGET_DIR)/locale
PLUGIN_DIR=$(TARGET_DIR)/plugin

# Target directories
LOCALE_INSTALL ?= /usr/share/locale
PLUGIN_INSTALL ?= /usr/lib

# Application id
APP_NAME=grammalecte
APP_TYPE=pluma-plugin
APP_PACKNAME=pluma-grammalecte
APP_VERSION=0.4
APP_AUTHOR=Stéphane Veyret

# Sources and targets
POS=$(wildcard po/*.po)
MOS=$(addsuffix /LC_MESSAGES/$(APP_PACKNAME).mo,$(addprefix $(LOCALE_DIR)/,$(notdir $(basename $(POS)))))
INI=plugin/$(APP_NAME).$(APP_TYPE)
PYS=$(filter-out $(wildcard plugin/test_*.py),$(wildcard plugin/*.py))
BIN=$(addprefix $(PLUGIN_DIR)/,$(notdir $(INI))) $(addprefix $(PLUGIN_DIR)/$(APP_NAME)/,$(notdir $(PYS)))

all: $(MOS) $(BIN)

po/$(APP_PACKNAME).pot:
	xgettext --package-name="$(APP_PACKNAME)" --package-version="$(APP_VERSION)" --copyright-holder="$(APP_AUTHOR)" -o "$@" -L Python plugin/*.py

%.po: po/$(APP_PACKNAME).pot
	[[ ! -f "$@" ]] || msgmerge -U "$@" "$<"
	[[ -f "$@" ]] || msginit -o "$@" -i "$<" -l "$(notdir $*)" --no-translator

%.mo: %.po
	msgfmt -o "$@" "$<"

$(LOCALE_DIR)/%/LC_MESSAGES/$(APP_PACKNAME).mo: po/%.mo
	mkdir -p "$(dir $@)"
	cp "$<" "$@"

$(PLUGIN_DIR)/%: plugin/%
	mkdir -p "$(dir $@)"
	cp "$<" "$@"

$(PLUGIN_DIR)/$(APP_NAME)/%.py: plugin/%.py
	mkdir -p "$(dir $@)"
	cp "$<" "$@"

check:
	python -m unittest discover plugin/

install:
	install -d -m755 "$(DESTDIR)$(LOCALE_INSTALL)"
	cp -r $(LOCALE_DIR)/* "$(DESTDIR)$(LOCALE_INSTALL)"
	install -d -m755 "$(DESTDIR)$(PLUGIN_INSTALL)/pluma/plugins"
	cp -r $(PLUGIN_DIR)/* "$(DESTDIR)$(PLUGIN_INSTALL)/pluma/plugins"

clean:
	rm -f *~
	rm -f plugin/*.pyc
	rm -f plugin/*~
	rm -f po/*.mo
	rm -f po/*~

mrproper: clean
	rm -rf $(TARGET_DIR)

.PHONY: all check install clean mrproper

