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

from g_config import GrammalecteConfig
from g_analyzer import GrammalecteAnalyzer
from g_autocorrect import GrammalecteAutoCorrector

class GrammalecteWindowHelper:
	""" The Window helper """
	DATA_TAG = "GrammalecteWindowHelper"

	def __init__(self, window):
		""" Initialize the helper """
		self.__window = window
		self.__analyzer = GrammalecteAnalyzer()
		self.__tabRemovedId = \
			self.__window.connect("tab-removed", self.tab_removed)
		for view in self.__window.get_views():
			self.__associate(view)
		self.__tabAddedId = self.__window.connect("tab-added", self.tab_added)

	def deactivate(self):
		""" Deactivate the helper """
		self.__window.disconnect(self.__tabAddedId)
		for view in self.__window.get_views():
			self.__deassociate(view)
		self.__window.disconnect(self.__tabRemovedId)
		self.__analyzer.terminate()
		self.__analyzer = None
		self.__window = None

	def update_ui(self):
		""" UI update requested """
		pass

	def tab_added(self, action, tab):
		""" Tab added event """
		self.__associate(tab.get_view())

	def tab_removed(self, action, tab):
		""" Tab removed event """
		self.__deassociate(tab.get_view())

	def __associate(self, view):
		""" Associate view and corrector """
		view.set_data(
			GrammalecteAutoCorrector.DATA_TAG,
			GrammalecteAutoCorrector(view, self.__analyzer))

	def __deassociate(self, view):
		""" Deassociate view and corrector, if any """
		helper = view.get_data(GrammalecteAutoCorrector.DATA_TAG)
		if helper != None:
			helper.deactivate()
			view.set_data(GrammalecteAutoCorrector.DATA_TAG, None)

