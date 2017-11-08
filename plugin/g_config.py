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

"""
	Manage the configuration of pluma-grammalecte.
	This module has a generic class DictConfig and a specific class
	GrammalecteConfig, inheriting from the former.
"""

import glib
import gobject
import json
import os

class SelfConfigContainer:
	"""
		An object containing its configuration.

		A class inheriting from this one should manage itself the storage of
		its configuration (as a JSON string). This is useful for example for an
		object managing file metadata.
	"""

	EMPTY = "{}"

	def get_self_config(self):
		"""
			Get the configuration of the object.

			The configuration is a string parsable in JSON.

			:return: the configuration of the object.
			:rtype: str
		"""
		pass

	def set_self_config(self, config):
		"""
			Set the configuration of the object.

			The configuration is a string parsable in JSON.

			:param config: the configuration of the object.
			:type config: str
		"""
		pass

class DictConfig(gobject.GObject):
	"""
		A configuration stored as a dictionnary.

		The configuration can be initialized with a dictionnary or with a JSON
		formatted file. In the latter case, modifications made to the
		configuration will be saved to the file. The file storage may be
		managed by an external object, useful for example to store the
		configuration in a document metadata.
		The configuration can have a parent, which is used when a value in
		child is None for a given path.
		Configuration values are accessed throw xPath-like definition.
	"""

	__gsignals__ = {
		"updated": (
			gobject.SIGNAL_RUN_LAST,
			gobject.TYPE_NONE,
			(gobject.TYPE_INT, gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)),
		"cleared": (
			gobject.SIGNAL_RUN_LAST,
			gobject.TYPE_NONE,
			(gobject.TYPE_INT,))
	}

	def __init__(self, data, parent = None):
		"""
			Initialize the instance.

			:param data: either the initialization dict for read-only, or the
			full name (including path) to the file where configuration is read.
			:param parent: (optional) the parent to use if configuration option
			is not found in current configuration.
			:type data: dict, str
			:type parent: DictConfig, None
		"""
		gobject.GObject.__init__(self)

		if data is None:
			self.__init_config({})
		elif type(data) is str:
			self.__init_file(data)
		elif type(data) is dict:
			self.__init_config(data)
		elif isinstance(data, SelfConfigContainer):
			self.__init_self_config(data)
		else:
			raise AttributeError

		self.__dirty = False

		self.__parent = parent
		if self.__parent is not None:
			self.__eventUpdatedId = \
				self.__parent.connect("updated", self.on_updated)
			self.__eventClearedId = \
				self.__parent.connect("cleared", self.on_cleared)

	def __init_file(self, filename):
		"""
			Initialize the instance with a file.

			:param filename: the full name of the file.
			:type filename: str
		"""
		self.__filedef = filename
		self.__config = {}
		try:
			if os.path.exists(self.__filedef):
				with open(self.__filedef, 'r') as cfile:
					self.__config = json.loads(cfile.read())
		except:
			pass

	def __init_config(self, config):
		"""
			Initialize the instance with configuration.

			:param config: the read-only configuration.
			:type config: dict
		"""
		self.__filedef = None
		self.__config = config

	def __init_self_config(self, selfConfig):
		"""
			Initialize the instance with a self config container.

			:param selfConfig: the object.
			:type selfConfig: SelfConfigContainer
		"""
		self.__filedef = selfConfig
		self.__config = {}
		try:
			self.__config = json.loads(self.__filedef.get_self_config())
		except:
			pass

	def __del__(self):
		"""
			Delete the configuration object.
		"""
		if self.__parent is not None:
			self.__parent.disconnect(self.__eventUpdatedId)
			self.__parent.disconnect(self.__eventClearedId)
		self.__parent = None
		self.__config = None
		self.__filedef = None

	def on_updated(self, config, level, xPath, newValue):
		"""
			Manage the updated event comming from parent.
		"""
		self.emit("updated", level + 1, xPath, newValue)

	def on_cleared(self, config, level):
		"""
			Manage the cleared event comming from parent.
		"""
		self.emit("cleared", level + 1, xPath, newValue)

	def get_value(self, xPath):
		"""
			Get the value corresponding to the given xPath.

			If no entry is found associated to the given xPath, the method
			recurse to the parent configuration, if available. If neither a
			value is found nor a parent defined, it will return None.

			:param xPath: the xPath-like query to reach the value.
			:type xPath: str
			:return: the value at matching position, or None.
			:rtype: any
		"""
		result = self.__find(xPath)
		if result is None and self.__parent is not None:
			result = self.__parent.get_value(xPath)
		elif type(result) is dict and self.__parent is not None:
			result = {}
			for key in self.__get_keys(xPath):
				result[key] = self.get_value(xPath + "/" + key)
		return result

	def __get_keys(self, xPath):
		"""
			Get all the keys in the dict at xPath location.

			If the object at given location is not a dict, the key set will be
			empty.

			:param xPath: the xPath-like query to reach the dict.
			:type xPath: str
			:return: a set of keys, or an empty set if no key.
			:rtype: set
		"""
		keys = set()
		if self.__parent is not None:
			keys.update(self.__parent.__get_keys(xPath))
		value = self.__find(xPath)
		if type(value) is dict:
			for key in value:
				keys.add(key)
		return keys

	def set_value(self, xPath, newValue, level = 0):
		"""
			Update the value corresponding to the given xPath.

			If the path to the value does not exist, it is created, unless it
			is a list. The update is made on the parent at given level. A level
			of 0 means to modify this configuration, 1 is for this parent's
			configuration, 2 is for this grand-parent's, etc.

			:param xPath: the xPath-like query to reach the value.
			:param newValue: the new value to set at given position.
			:param level: (optional) the parent level.
			:type xPath: str
			:type newValue: any
			:type level: int
		"""
		if level == 0:
			if self.__find(xPath) != newValue:
				self.__update(xPath, newValue)
				self.__dirty = True
				self.emit("updated", 0, xPath, newValue)
		elif self.__parent is not None:
			self.__parent.set_value(xPath, newValue, level - 1)

	def __find(self, xPath):
		"""
			Find the value corresponding to the given xPath.

			Returns None if no entry is found associated to the given xPath,
			without searching in parents.

			:param xPath: the xPath-like query to reach the value.
			:type xPath: str
			:return: the value at matching position, or None.
			:rtype: any
		"""
		value = self.__config
		try:
			for name in xPath.strip("/").split("/"):
				try:
					name = int(name)
				except ValueError:
					pass
				value = value[name]
		except:
			value = None

		return value

	def __update(self, xPath, newValue):
		"""
			Update the value corresponding to the given xPath.

			If the path to the value does not exist, it is created, unless it
			is a list.

			:param xPath: the xPath-like query to reach the value.
			:param newValue: the new value to set at given position.
			:type xPath: str
			:type newValue: any
		"""
		entry = self.__config
		oldName = None
		try:
			for name in xPath.strip("/").split("/"):
				try:
					name = int(name)
				except ValueError:
					pass
				if oldName is not None:
					if not oldName in entry:
						entry[oldName] = {}
					entry = entry[oldName]
				oldName = name
			if oldName is not None:
				if newValue is None:
					del entry[oldName]
				else:
					entry[oldName] = newValue
		except:
			pass

	def clear(self, level = 0):
		"""
			Clear all the configuration.

			All the parameters are removed from this configuration. The removal
			is made on the parent at given level. A level of 0 means to modify
			this configuration, 1 is for this parent's configuration, 2 is for
			this grand-parent's, etc.

			:param level: (optional) the parent level.
			:type level: int
		"""
		if level == 0:
			self.__config = {}
			self.emit("cleared", 0)
		elif self.__parent is not None:
			self.__parent.clear(level - 1)

	def close(self):
		"""
			Close this configuration and the parents.

			If there are modifications and the configuration is associated to a
			valid file, it will be saved to disk.

			.. note:: A closed configuration can still be used, but should be
			closed again after.
		"""
		if self.__parent is not None:
			self.__parent.close()
		if self.__filedef is not None and self.__dirty:
			if type(self.__filedef) is str:
				self.__save_file()
			else:
				self.__save_self_config()

	def __save_file(self):
		""" Save configuration as file """
		try:
			configDir = os.path.dirname(self.__filedef)
			if not os.path.isdir(configDir):
				os.makedirs(configDir)
			with open(self.__filedef, 'w') as cfile:
				json.dump(self.__config, cfile, indent = 2)
			self.__dirty = False
		except:
			print _("Error: configuration file “{}” could not be saved") \
				.format(self.__filedef)

	def __save_self_config(self):
		""" Save configuration as metadata """
		try:
			self.__filedef.set_self_config(json.dumps(
				self.__config, separators = (",", ":")))
		except:
			print _("Error: configuration could not be saved")

class GrammalecteConfig(DictConfig):
	"""
		A Grammalecte configuration for a given document.

		This configuration inherits from user and system configuration, if
		available.

		:Example:

		>>> config = GrammalecteConfig()

		>>> config.get_value(GrammalecteConfig.AUTO_ANALYZE_TIMER)
		500

		>>> config.set_value("top/sub", ["zero", {"1st": "1", "other": "yes"}])

		>>> config.get_value("top/sub/1/other")
		'yes'
	"""

	############
	# ALL CONFIGURATION CONSTANTS ARE HERE
	############
	LOCALE_DIR = "locale-dir"
	ANALYZE_OPTIONS = "analyze-options"
	AUTO_ANALYZE_ACTIVE = "auto-analyze-active"
	AUTO_ANALYZE_TIMER = "auto-analyze-timer"
	ANALYZE_WAIT_TICKS = "analyze-wait-ticks"
	GRAMMALECTE_PYTHON_EXE = "g-python-exe"
	GRAMMALECTE_CLI = "g-cli"
	GRAMMALECTE_ANALYZE_PARAMS = "g-analyze-params"
	GRAMMALECTE_OPTIONS_PARAMS = "g-options-params"
	GRAMMALECTE_OPTIONS_REGEX = "g-options-regex"

	__CLI_PARAMS = "g-cli-params"
	__CLI_FILE = "file"
	__CLI_OPTS_ON = "on"
	__CLI_OPTS_OFF = "off"
	GRAMMALECTE_CLI_FILE = __CLI_PARAMS + "/" + __CLI_FILE
	GRAMMALECTE_CLI_OPTS_ON = __CLI_PARAMS + "/" + __CLI_OPTS_ON
	GRAMMALECTE_CLI_OPTS_OFF = __CLI_PARAMS + "/" + __CLI_OPTS_OFF

	GRAMMALECTE_OPTION_SPELLING = "_orth_"

	__DEFAULT_CONFIG = {
		ANALYZE_OPTIONS: {},
		AUTO_ANALYZE_ACTIVE: False,
		AUTO_ANALYZE_TIMER: 500,
		ANALYZE_WAIT_TICKS: 12,
		GRAMMALECTE_PYTHON_EXE: "python3",
		GRAMMALECTE_CLI: "/opt/grammalecte/cli.py",
		__CLI_PARAMS: {
			__CLI_FILE: "-f",
			__CLI_OPTS_ON: "-on",
			__CLI_OPTS_OFF: "-off"
		},
		GRAMMALECTE_ANALYZE_PARAMS: ["-j", "-cl", "-owe", "-ctx"],
		GRAMMALECTE_OPTIONS_PARAMS: ["-lo"],
		GRAMMALECTE_OPTIONS_REGEX: "^([a-zA-Z0-9]+):\s*(True|False)\s*(.*)$"
	}

	__PLUMA_CONFIG_FILE = "/pluma/grammalecte.conf"
	__SYSTEM_CONFIG_FILE = "/etc" + __PLUMA_CONFIG_FILE
	__USER_CONFIG_FILE = glib.get_user_config_dir() + __PLUMA_CONFIG_FILE

	__globalInstance = None

	def __init__(self, selfConfig = None):
		"""
			Initialize the plugin configuration.

			:param selfConfig: (optional) the selfConfig container.
			:type selfConfig: SelfConfigContainer
		"""
		# Initialize global instance
		if GrammalecteConfig.__globalInstance is None:
			defaultConfig = DictConfig(GrammalecteConfig.__DEFAULT_CONFIG)
			systemConfig = DictConfig(GrammalecteConfig.__SYSTEM_CONFIG_FILE,
				defaultConfig)
			GrammalecteConfig.__globalInstance = \
				DictConfig(GrammalecteConfig.__USER_CONFIG_FILE, systemConfig)

		# Initialize local instance
		DictConfig.__init__(self, selfConfig, GrammalecteConfig.__globalInstance)

	@staticmethod
	def terminate():
		"""
			Terminate usage of all configurations.

			This will save global configuration files if needed.
		"""
		if GrammalecteConfig.__globalInstance is not None:
			GrammalecteConfig.__globalInstance.close()
			GrammalecteConfig.__globalInstance = None

import gettext
gettext.install("pluma-grammalecte",
	localedir = GrammalecteConfig().get_value(
		GrammalecteConfig.LOCALE_DIR), unicode = True)

if __name__ == "__main__":
	import doctest
	doctest.testmod()

