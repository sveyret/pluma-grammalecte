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

import gtk

from g_config import GrammalecteConfig

from g_analyzer import GrammalecteAnalyzer
from g_config_dlg import GrammalecteConfigDlg
from g_view import GrammalecteViewHelper

#<menuitem name="CheckGrammalecte" action="CheckGrammalecte"/>
_ui_str = """
<ui>
	<menubar name="MenuBar">
		<menu name="ToolsMenu" action="Tools">
			<placeholder name="ToolsOps_1">
				<separator />
				<menuitem name="AutoGrammalecte" action="AutoGrammalecte"/>
				<menuitem name="ConfigGrammalecte" action="ConfigGrammalecte"/>
				<separator />
			</placeholder>
		</menu>
	</menubar>
</ui>
"""

class GrammalecteWindowHelper:
	""" The Window helper """
	DATA_TAG = "GrammalecteWindowHelper"

	def __init__(self, window):
		""" Initialize the helper """
		self.__window = window
		self.__analyzer = GrammalecteAnalyzer()
		self.__eventTabRemovedId = self.__window.connect(
			"tab-removed", self.on_tab_removed)
		for view in self.__window.get_views():
			self.__associate(view)
		self.__eventTabAddedId = self.__window.connect(
			"tab-added", self.on_tab_added)
		self.__insert_menu()

	def deactivate(self):
		""" Deactivate the helper """
		self.__remove_menu()
		self.__window.disconnect(self.__eventTabAddedId)
		for view in self.__window.get_views():
			self.__deassociate(view)
		self.__window.disconnect(self.__eventTabRemovedId)
		self.__analyzer.terminate()
		self.__analyzer = None
		self.__window = None

	def __insert_menu(self):
		""" Insert the Grammalecte menu """
		manager = self.__window.get_ui_manager()
		self.__actionGroup = gtk.ActionGroup("GrammalecteActions")
		self.__actionGroup.add_actions([("CheckGrammalecte",
			gtk.STOCK_SPELL_CHECK,
			_("_Check Syntax..."),
			"<shift>F7",
			_("Check the current document for incorrect grammar and spelling"),
			self.on_menu_check),
			('ConfigGrammalecte',
			None,
			_('Configure _Grammalecte...'),
			None,
			_("Configure the Grammalecte rules"),
			self.on_menu_config)])
		self.__actionGroup.add_toggle_actions([('AutoGrammalecte',
			None,
			_('_Autocheck Syntax'),
			None,
			_("Automatically grammar and spell-check the current document"),
			self.on_menu_auto)])
		manager.insert_action_group(self.__actionGroup, -1)
		self.__uiId = manager.add_ui_from_string(_ui_str)

	def __remove_menu(self):
		""" Remove the menu """
		manager = self.__window.get_ui_manager()
		manager.remove_ui(self.__uiId)
		manager.remove_action_group(self.__actionGroup)
		manager.ensure_update()

	def update_ui(self):
		""" UI update requested """
		tab = self.__window.get_active_tab()
		view = None if tab == None else tab.get_view()
		helper = None if view == None else view.get_data(
			GrammalecteViewHelper.DATA_TAG)
		sensitive = helper != None and not helper.is_readonly()
		autoActive = helper != None and helper.get_config().get_value(
			GrammalecteConfig.AUTO_ANALYZE_ACTIVE)
		self.__actionGroup.set_sensitive(sensitive)
		self.__actionGroup.get_action("AutoGrammalecte").set_active(autoActive)

	def on_tab_added(self, action, tab):
		""" Mange the tab added event """
		self.__associate(tab.get_view())
		self.update_ui()

	def on_tab_removed(self, action, tab):
		""" Manage the tab removed event """
		self.__deassociate(tab.get_view())
		self.update_ui()

	def __associate(self, view):
		""" Associate view and helper """
		helper = view.get_data(GrammalecteViewHelper.DATA_TAG)
		if helper == None:
			helper = GrammalecteViewHelper(view, view.get_buffer(), self)
			view.set_data(GrammalecteViewHelper.DATA_TAG, helper)

	def __deassociate(self, view):
		""" Deassociate view and helper, if any """
		helper = view.get_data(GrammalecteViewHelper.DATA_TAG)
		if helper != None:
			helper.deactivate()
			view.set_data(GrammalecteViewHelper.DATA_TAG, None)

	def on_menu_check(self, action):
		pass

	def on_menu_auto(self, action):
		""" Manage automatic toggle menu """
		tab = self.__window.get_active_tab()
		view = None if tab == None else tab.get_view()
		helper = None if view == None else view.get_data(
			GrammalecteViewHelper.DATA_TAG)
		if helper != None and not helper.is_readonly():
			helper.set_auto_analyze(action.get_active())

	def on_menu_config(self, action):
		""" Change configuration """
		dialog = GrammalecteConfigDlg()
		if dialog.run():
			pass

	def get_analyzer(self):
		return self.__analyzer

