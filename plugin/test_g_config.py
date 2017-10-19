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

import unittest

from g_config import DictConfig

class TestDictConfig(unittest.TestCase):
	def setUp(self):
		self.defaultConfig = DictConfig({"key0": "value0", "key1": "invisible"})
		self.config = DictConfig({"key1": "value1", "key2": {"key21": ["value21a", "value21b"], "key22": "value22"}, "key3": "value3"}, self.defaultConfig)

	def test_get_simple_value(self):
		self.assertEqual(self.config.get_value("key3"), "value3")

	def test_get_complex_value(self):
		self.assertEqual(self.config.get_value("key2/key21/1"), "value21b")

	def test_get_default_value(self):
		self.assertEqual(self.config.get_value("key0"), "value0")

	def test_set_simple_value(self):
		self.config.set_value("key1", "newValue1")
		self.assertEqual(self.config.get_value("key1"), "newValue1")
		self.assertEqual(self.defaultConfig.get_value("key1"), "invisible")

	def test_set_complex_value(self):
		self.config.set_value("key2/key21/0", {"a": "newValuea", "b": "newValueb"})
		self.assertEqual(self.config.get_value("key2/key21/0/b"), "newValueb")

	def test_set_default_value(self):
		self.config.set_value("key1", "newValue1", 1)
		self.assertEqual(self.config.get_value("key1"), "value1")
		self.assertEqual(self.defaultConfig.get_value("key1"), "newValue1")

	def test_create_value(self):
		self.config.set_value("key4/hello", "world")
		self.assertEqual(self.config.get_value("key4/hello"), "world")

if __name__ == '__main__':
	unittest.main()

