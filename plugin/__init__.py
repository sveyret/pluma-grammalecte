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

import pluma

from g_config import GrammalecteConfig

from g_window import GrammalecteWindowHelper

class GrammalectePlugin(pluma.Plugin):
	""" The plugin manager """
	def __init__(self):
		""" Initialize plugin """
		pluma.Plugin.__init__(self)

	def activate(self, window):
		""" Start the plugin """
		window.set_data(
			GrammalecteWindowHelper.DATA_TAG, GrammalecteWindowHelper(window))

	def deactivate(self, window):
		""" Stop the plugin """
		windowHelper = window.get_data(GrammalecteWindowHelper.DATA_TAG)
		if windowHelper is not None:
			windowHelper.deactivate()
			window.set_data(GrammalecteWindowHelper.DATA_TAG, None)
		GrammalecteConfig.terminate()

	def update_ui(self, window):
		""" UI needs refresh """
		window.get_data(GrammalecteWindowHelper.DATA_TAG).update_ui()

