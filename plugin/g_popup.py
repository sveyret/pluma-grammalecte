# -*- coding: utf-8 -*-
#
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

""" Manage the popup menu to display on top of an error """

import gtk
import subprocess

from g_config import GrammalecteConfig

from g_error import GErrorDesc

class GPopupMenu():
	""" Create and manage the popup menu """

	def __init__(self, menu, error, autocorrector):
		""" Create the menu options """
		mi = gtk.SeparatorMenuItem()
		mi.show()
		menu.prepend(mi)
		mi = gtk.ImageMenuItem(gtk.STOCK_SPELL_CHECK)
		mi.set_label(_("_Suggestions"))
		mi.set_submenu(self.build_suggestion_menu(error, autocorrector))
		mi.show_all()
		menu.prepend(mi)

	def build_suggestion_menu(self, error, autocorrector):
		""" Build the suggestion menu """
		config = autocorrector.get_config()
		topmenu = gtk.Menu()

		suggestions = error[GErrorDesc.SUGGESTIONS]
		if len(suggestions) == 0:
			mi = gtk.MenuItem(_("(no suggestions)"))
			mi.set_sensitive(False)
			mi.show_all()
			topmenu.append(mi)
		else:
			menu = topmenu
			count = 0
			for suggestion in suggestions:
				if count == 6:
					mi = gtk.SeparatorMenuItem()
					mi.show()
					menu.append(mi)
					mi = gtk.MenuItem(_("_More"))					
					mi.show_all()
					menu.append(mi)
					menu = gtk.Menu()
					mi.set_submenu(menu)
					count = 0
				mi = gtk.MenuItem(suggestion)
				mi.show_all()
				menu.append(mi)
				mi.connect("activate", self.on_menu_replace, error, suggestion,
					autocorrector)
				count += 1

		mi = gtk.SeparatorMenuItem()
		mi.show()
		topmenu.append(mi)
		mi = gtk.MenuItem(_("Ignore _rule"))
		mi.set_sensitive(error[GErrorDesc.RULE] is not None)
		mi.show_all()
		topmenu.append(mi)
		mi.connect(
			"activate", self.on_menu_ign_rule, error[GErrorDesc.RULE], config)
		mi = gtk.MenuItem(_("Ignore _error"))
		mi.show_all()
		topmenu.append(mi)
		mi.connect(
			"activate", self.on_menu_ign_error, error[GErrorDesc.CONTEXT],
			config)
		mi = gtk.MenuItem(_("_Add"))
		mi.set_sensitive(error[GErrorDesc.OPTION] == \
			GrammalecteConfig.GRAMMALECTE_OPTION_SPELLING)
		mi.show_all()
		topmenu.append(mi)
		mi.connect(
			"activate", self.on_menu_add, error[GErrorDesc.CONTEXT], config)
		mi = gtk.SeparatorMenuItem()
		mi.show()
		topmenu.append(mi)
		mi = gtk.MenuItem(_("_See the rule"))
		mi.set_sensitive(error[GErrorDesc.URL] is not None)
		mi.show_all()
		topmenu.append(mi)
		mi.connect("activate", self.on_menu_info, error[GErrorDesc.URL])
		return topmenu

	def on_menu_replace(self, item, error, suggestion, autocorrector):
		""" Replace error with suggestion """
		vBuffer = autocorrector.get_buffer()
		start, end = autocorrector.convert_limits(error, vBuffer)
		oldText = vBuffer.get_slice(start, end)
		if oldText == error[GErrorDesc.CONTEXT][1]:
			vBuffer.begin_user_action()
			vBuffer.delete(start, end)
			vBuffer.insert(start, suggestion)
			vBuffer.end_user_action()

	def on_menu_ign_rule(self, item, rule, config):
		""" Ignore the rule in the file """
		config.add_value(GrammalecteConfig.IGNORED_RULES, rule)

	def on_menu_ign_error(self, item, context, config):
		""" Ignore the error in the file """
		config.add_value(GrammalecteConfig.IGNORED_ERRORS, list(context))

	def on_menu_add(self, item, context, config):
		""" Add the error to global configuration """
		config.add_value(GrammalecteConfig.IGNORED_ERRORS, list(context), 1)

	def on_menu_info(self, item, url):
		""" Open the URL """
		subprocess.Popen(['xdg-open', url])

