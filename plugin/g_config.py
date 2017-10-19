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
import json
import os

class DictConfig:
	"""
		A configuration stored as a dictionnary.

		The configuration can be initialized with a dictionnary or with a JSON
		formatted file. In the latter case, modifications made to the
		configuration will be saved to the file.
		The configuration can have a parent, which is used when a value in
		child is None for a given path.
		Configuration values are accessed throw xPath-like definition.
	"""

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
		self.parent = parent
		self.dirty = False
		if data == None:
			self.__init_config({})
		elif type(data) is str:
			self.__init_file(data)
		elif type(data) is dict:
			self.__init_config(data)
		else:
			raise AttributeError

	def __init_file(self, filename):
		"""
			Initialize the instance with a file.

			:param filename: the full name of the file.
			:type filename: str
		"""
		self.filename = filename
		self.config = {}
		try:
			if os.path.exists(self.filename):
				with open(self.filename, 'r') as cfile:
					self.config = json.loads(cfile.read())
		except:
			pass

	def __init_config(self, config):
		"""
			Initialize the instance with configuration.

			:param config: the read-only configuration.
			:type config: dict
		"""
		self.filename = None
		self.config = config

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
		if result == None and self.parent != None:
			result = self.parent.get_value(xPath)
		return result

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
				self.dirty = True
		else:
			if self.parent != None:
				self.parent.set_value(xPath, newValue, level - 1)

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
		value = self.config
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
		entry = self.config
		oldName = None
		try:
			for name in xPath.strip("/").split("/"):
				try:
					name = int(name)
				except ValueError:
					pass
				if oldName != None:
					if not oldName in entry:
						entry[oldName] = {}
					entry = entry[oldName]
				oldName = name
			if oldName != None:
				entry[oldName] = newValue
		except:
			pass

	def close(self):
		"""
			Close this configuration and the parents.

			If there are modifications on this file, it will be saved to disk.

			.. note:: A closed configuration can still be used, but should be
			closed again after.
		"""
		if self.parent != None:
			self.parent.close()
		if self.filename != None and self.dirty:
			try:
				configDir = os.path.dirname(self.filename)
				if not os.path.isdir(configDir):
					os.makedirs(configDir)
				with open(self.filename, 'w') as cfile:
					json.dump(self.config, cfile)
				self.dirty = False
			except:
				print _("Error: configuration file “{}” could not be saved") \
					.format(self.filename)

class GrammalecteConfig(DictConfig):
	"""
		A Grammalecte configuration for a given document.

		This configuration inherits from user and system configuration, if
		available.

		:Example:

		>>> config = GrammalecteConfig()

		>>> config.get_value("grammalecte-analyze-timer")
		500

		>>> config.set_value("top/sub", ["zero", {"1st": "1", "other": "yes"}])

		>>> config.get_value("top/sub/1/other")
		'yes'
	"""

	############
	# ALL CONFIGURATION CONSTANTS ARE HERE
	############
	__DEFAULT_CONFIG = {
		"grammalecte-python-exe": "python3",
		"grammalecte-cli": "/opt/grammalecte/cli.py",
		"grammalecte-analyze-params": ["-j", "-cl", "-owe", "-ctx"],
		"grammalecte-analyze-timer": 500
	}

	__PLUMA_CONFIG_FILE = "/pluma/grammalecte.conf"
	__SYSTEM_CONFIG_FILE = "/etc" + __PLUMA_CONFIG_FILE
	__USER_CONFIG_FILE = glib.get_user_config_dir() + __PLUMA_CONFIG_FILE
	__LOCAL_CONFIG_FILE = "{}/.{}-grammalecte"

	__globalInstance = None

	def __init__(self, localFile = None):
		"""
			Initialize the plugin configuration.

			:param localFile: (optional) the path to the currently edited local
			file.
			:type localFile: str
		"""
		# Initialize global instance
		if GrammalecteConfig.__globalInstance == None:
			defaultConfig = DictConfig(GrammalecteConfig.__DEFAULT_CONFIG)
			systemConfig = DictConfig(GrammalecteConfig.__SYSTEM_CONFIG_FILE,
				defaultConfig)
			GrammalecteConfig.__globalInstance = \
				DictConfig(GrammalecteConfig.__USER_CONFIG_FILE, systemConfig)

		# Initialize local instance
		configFile = None if localFile == None \
			else GrammalecteConfig.__LOCAL_CONFIG_FILE.format(
				os.path.dirname(localFile), os.path.basename(localFile))
		DictConfig.__init__(
			self, configFile, GrammalecteConfig.__globalInstance)

	@staticmethod
	def terminate():
		"""
			Terminate usage of all configurations.

			This will save global configuration files if needed.
		"""
		if GrammalecteConfig.__globalInstance != None:
			GrammalecteConfig.__globalInstance.close()
			GrammalecteConfig.__globalInstance = None

import gettext
gettext.install("pluma-grammalecte",
	localedir = GrammalecteConfig().get_value("locale-dir"), unicode = True)

if __name__ == "__main__":
	import doctest
	doctest.testmod()

