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

import gio

from g_config import SelfConfigContainer, GrammalecteConfig

from g_autocorrect import GrammalecteAutoCorrector

class GrammalecteViewHelper(SelfConfigContainer):
	""" A helper attached to the view """
	DATA_TAG = "GrammalecteViewHelper"
	__CONFIG_METADATA = "metadata::pluma-grammalecte"

	def __init__(self, view, document, windowHelper):
		""" Initialize the helper """
		self.__view = view
		self.__document = document
		self.__windowHelper = windowHelper
		self.__filename = self.__document.get_uri()
		self.__gFile = None if self.__filename is None else \
			gio.File(self.__filename)
		self.__config = GrammalecteConfig(self)
		self.__autocorrect = None
		if self.is_auto_checked():
			self.__set_auto_analyze(True)
		self.__eventDocSavedId = self.__document.connect(
			"saved", self.on_doc_saved)
		self.__eventDocLoadedId = self.__document.connect(
			"loaded", self.on_doc_loaded)

	def deactivate(self):
		""" Disconnect the helper from the view """
		self.__document.disconnect(self.__eventDocLoadedId)
		self.__document.disconnect(self.__eventDocSavedId)
		self.__set_auto_analyze(False)
		self.__config.close()
		self.__config = None
		self.__gFile = None
		self.__filename = None
		self.__windowHelper = None
		self.__document = None
		self.__view = None

	def set_auto_analyze(self, active):
		"""
			Set auto-analyze to active or not.

			:param active: indicate if auto-analyze must be active or not.
			:type active: boolean
		"""
		self.__config.set_value(GrammalecteConfig.AUTO_ANALYZE_ACTIVE, active)
		self.__set_auto_analyze(active)

	def __set_auto_analyze(self, active):
		""" Set auto-analyze without changing the configuration """
		if active and self.__autocorrect == None:
			self.__autocorrect = GrammalecteAutoCorrector(self)
		elif not active and self.__autocorrect != None:
			self.__autocorrect.deactivate()
			self.__autocorrect = None

	def refresh_analyze(self):
		""" Execute the analyze as it may be obsolete """
		if self.__autocorrect != None:
			self.__autocorrect.ask_request()

	def on_doc_saved(self, document, error):
		""" Manage the document saved event """
		if error == None:
			self.__filename = self.__document.get_uri()
			self.__gFile = None if self.__filename is None else \
				gio.File(self.__filename)

	def on_doc_loaded(self, document, error):
		""" Manage the document loaded event """
		if error == None and (self.__document != document or \
			self.__filename != document.get_uri() or \
			(self.__autocorrect != None) != self.is_auto_checked()):
			view = self.__view
			windowHelper = self.__windowHelper
			self.deactivate()
			self.__init__(view, document, windowHelper)
			self.__windowHelper.update_ui()

	def get_self_config(self):
		""" Get the configuration from metadata """
		config = None
		if self.__gFile != None:
			info = self.__gFile.query_info(
				GrammalecteViewHelper.__CONFIG_METADATA)
			config = info.get_attribute_as_string(
				GrammalecteViewHelper.__CONFIG_METADATA)
		if config == None:
			config = SelfConfigContainer.EMPTY
		return config

	def set_self_config(self, config):
		""" Set the configuration in metadata """
		if self.__gFile != None:
			self.__gFile.set_attribute_string(
				GrammalecteViewHelper.__CONFIG_METADATA, config)

	def is_auto_checked(self):
		""" Indicate if automatic check is on """
		return self.__config.get_value(GrammalecteConfig.AUTO_ANALYZE_ACTIVE) \
			and not self.is_readonly()

	def is_readonly(self):
		""" Indicate if the associated document is read-only """
		return not self.__view.get_editable()

	def get_view(self):
		""" Get the (real) view attached to the helper """
		return self.__view

	def get_config(self):
		""" Get the configuration of the helper """
		return self.__config

	def get_analyzer(self):
		""" Get the analyzer """
		return self.__windowHelper.get_analyzer()

