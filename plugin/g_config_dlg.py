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
import pluma
import re
import subprocess

from g_config import GrammalecteConfig
from g_view import GrammalecteViewHelper

class GrammalecteConfigDlg:
	""" The configuration dialog """
	__RESPONSE_CLEAR = 1
	__OPTION_KEY = "key"
	__OPTION_BUTTON = "button"
	__OPTION_GVAL = "global-value"
	__OPTION_FVAL = "file-value"

	def __init__(self, window, viewHelper):
		""" Prepare the dialog box """
		self.activeWindow = window
		self.viewHelper = viewHelper

		self.dialog = gtk.Dialog(_("Configuration"),
			self.activeWindow,
			gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
			(gtk.STOCK_CLEAR, GrammalecteConfigDlg.__RESPONSE_CLEAR,
			gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
			gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
		self.dialog.connect('delete-event', self.on_delete_event)
		self.dialog.set_default_size(450, 400)

		for button in self.dialog.get_action_area().get_children():
			if button.get_label() == "gtk-clear":
				self.button_clear = button
		if self.button_clear == None:
			raise Exception(_("Internal error"))

		box = self.__create_scope_box()
		if box != None:
			self.dialog.get_content_area().pack_start(box, False)
		self.__extract_options()

		box = gtk.VBox()
		self.dialog.get_content_area().add(
			self.__surround_with_scrollbars(box))
		for option in self.options:
			box.add(option[GrammalecteConfigDlg.__OPTION_BUTTON])
		self.__display_config(True)

		self.dialog.show_all()
		self.button_clear.hide()

	def __create_scope_box(self):
		""" Create the scope box """
		if self.viewHelper == None:
			self.globalOption = None
			return None
		else:
			filename = self.activeWindow.get_active_document() \
				.get_short_name_for_display()
			self.globalOption = gtk.RadioButton(label = _("Global"))
			fileOption = gtk.RadioButton(self.globalOption, filename)
			self.globalOption.set_active(True)
			box = gtk.HBox(True)
			box.add(self.globalOption)
			box.add(fileOption)
			self.globalOption.connect("toggled", self.on_toggle_scope)
			return box

	def __extract_options(self):
		""" Grab the options from Grammalecte """
		config = GrammalecteConfig() if self.viewHelper == None else \
			self.viewHelper.get_config()

		waitDlg = gtk.MessageDialog(
			self.activeWindow,
			gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
			message_format = _("Preparing Grammalecte options..."))
		waitDlg.show()
		self.__flush_events()

		self.__set_options(self.__call_grammalecte(
			config.get_value(GrammalecteConfig.GRAMMALECTE_PYTHON_EXE),
			config.get_value(GrammalecteConfig.GRAMMALECTE_CLI),
			config.get_value(GrammalecteConfig.GRAMMALECTE_OPTIONS_PARAMS)),
			config.get_value(GrammalecteConfig.GRAMMALECTE_OPTIONS_REGEX))
		self.__set_options_value(
			GrammalecteConfig(), GrammalecteConfigDlg.__OPTION_GVAL)
		self.__copy_global_in_file()
		self.__set_options_value(config, GrammalecteConfigDlg.__OPTION_FVAL)

		waitDlg.destroy()
		self.__flush_events()

	def __call_grammalecte(self, pythonExe, gramCli, gramOpts):
		""" Call the Grammalecte process to get available options """
		processArgs = []
		processArgs.append(pythonExe)
		processArgs.append(gramCli)
		for arg in gramOpts:
			processArgs.append(arg)
		process = subprocess.Popen(
			processArgs, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
		rawOptions, processError = process.communicate()
		if process.returncode != 0:
			print _("Error: Grammalecte process did not terminate" \
				" properly:\n{}").format(processError)
		return rawOptions

	def __set_options(self, rawOptions, regex):
		""" Set the options from the raw result """
		self.optionsByKey = {}
		self.options = []
		pattern = re.compile(regex)
		self.__set_option(
			GrammalecteConfig.GRAMMALECTE_OPTION_SPELLING,
			"True", _("Check Spelling"))
		for optionLine in rawOptions.splitlines():
			match = pattern.match(optionLine)
			if match != None:
				self.__set_option(*match.groups())

	def __set_option(self, optionName, optionValue, optionDesc):
		""" Set the options """
		if len(optionDesc) < len(optionName):
			optionDesc = "{} ({})".format(optionDesc, optionName)
		option = {
			GrammalecteConfigDlg.__OPTION_KEY: optionName,
			GrammalecteConfigDlg.__OPTION_BUTTON: gtk.CheckButton(optionDesc),
			GrammalecteConfigDlg.__OPTION_GVAL: optionValue == "True" }
		self.optionsByKey[optionName] = option
		self.options.append(option)

	def __set_options_value(self, config, optionVal):
		""" Set the options value depending on configuration """
		options = config.get_value(GrammalecteConfig.ANALYZE_OPTIONS)
		for optionName in options:
			if self.optionsByKey.has_key(optionName):
				self.optionsByKey[optionName][optionVal] = options[optionName]

	def __surround_with_scrollbars(self, box):
		""" Surround the given box with scrollbars """
		scrollBox = gtk.ScrolledWindow()
		scrollBox.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		scrollBox.add_with_viewport(box)
		return scrollBox

	def on_delete_event(self, dialog, event):
		""" Dialog box was manually closed """
		self.dialog.destroy()

	def on_toggle_scope(self, widget):
		""" Manage the toggle scope event """
		forGlobal = self.globalOption.get_active()
		self.__update_config(not forGlobal)
		self.__display_config(forGlobal)
		if forGlobal:
			self.button_clear.hide()
		else:
			self.button_clear.show()

	def run(self):
		""" Execute the dialog """
		config = GrammalecteConfig() if self.viewHelper == None else \
			self.viewHelper.get_config()

		response = GrammalecteConfigDlg.__RESPONSE_CLEAR
		while response == GrammalecteConfigDlg.__RESPONSE_CLEAR:
			response = self.dialog.run()
			if response == GrammalecteConfigDlg.__RESPONSE_CLEAR:
				self.__clear_config(config)
		self.dialog.destroy()
		if response == gtk.RESPONSE_ACCEPT:
			forGlobal = True if self.globalOption == None else \
				self.globalOption.get_active()
			self.__update_config(forGlobal)
			self.__save_config(config)
		return response == gtk.RESPONSE_ACCEPT

	def __clear_config(self, config):
		""" Clear the configuration """
		self.__copy_global_in_file()
		autoAnalyze = config.get_value(GrammalecteConfig.AUTO_ANALYZE_ACTIVE)
		config.clear()
		config.set_value(GrammalecteConfig.AUTO_ANALYZE_ACTIVE, autoAnalyze)
		self.__display_config(False)

	def __copy_global_in_file(self):
		""" Copy the global values in file values """
		for option in self.options:
			option[GrammalecteConfigDlg.__OPTION_FVAL] = \
				option[GrammalecteConfigDlg.__OPTION_GVAL]

	def __display_config(self, forGlobal):
		""" Update display from configuration """
		valueKey = GrammalecteConfigDlg.__OPTION_GVAL if forGlobal else \
			GrammalecteConfigDlg.__OPTION_FVAL
		for option in self.options:
			option[GrammalecteConfigDlg.__OPTION_BUTTON].set_active(
				option[valueKey])
		
	def __update_config(self, forGlobal):
		""" Update the dialog configuration from user input """
		for option in self.options:
			value = option[GrammalecteConfigDlg.__OPTION_BUTTON].get_active()
			changed = False
			if forGlobal:
				changed = option[GrammalecteConfigDlg.__OPTION_GVAL] != value
				option[GrammalecteConfigDlg.__OPTION_GVAL] = value
			if not forGlobal or changed:
				option[GrammalecteConfigDlg.__OPTION_FVAL] = value

	def __save_config(self, config):
		""" Save the configuration """
		gconfig = {}
		fconfig = {}
		for option in self.options:
			key = option[GrammalecteConfigDlg.__OPTION_KEY]
			gvalue = option[GrammalecteConfigDlg.__OPTION_GVAL]
			fvalue = option[GrammalecteConfigDlg.__OPTION_FVAL]
			gconfig[key] = gvalue
			if gvalue != fvalue:
				fconfig[key] = fvalue
		if len(gconfig) == 0:
			gconfig = None
		if len(fconfig) == 0:
			fconfig = None
		config.set_value(GrammalecteConfig.ANALYZE_OPTIONS, gconfig, 1)
		config.set_value(GrammalecteConfig.ANALYZE_OPTIONS, fconfig)

	def __flush_events(self):
		""" Clear pending events """
		while gtk.events_pending():
			gtk.main_iteration(True)

