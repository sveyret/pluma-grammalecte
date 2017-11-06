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

import doctest
import unittest

import g_error
from g_error import AvlTree, GErrorDesc, GErrorStore

def load_tests(loader, tests, ignore):
	tests.addTests(doctest.DocTestSuite(g_error))
	return tests

class TestAvlTree(unittest.TestCase):
	def setUp(self):
		self.tree = AvlTree(self.compare, 51)
		self.tree.add(-12)
		self.tree.add(25)
		self.tree.add(69)
		self.tree.add(-2)
		self.tree.add(2)

	def compare(self, left, right):
		return left - right

	def test_order(self):
		prev = -127
		for element in self.tree:
			self.assertGreaterEqual(element, prev)
			prev = element

	def test_len(self):
		self.assertEqual(len(self.tree), 6)

class TestGErrorStore(unittest.TestCase):
	def setUp(self):
		self.store = GErrorStore()
		self.begin = self.buildError((1, 1), (1, 5))
		self.multi = self.buildError((2, 51), (4, 2))
		self.before = self.buildError((8, 4), (8, 15))
		self.after = self.buildError((8, 17), (8, 65))
		self.store.add(self.multi)
		self.store.add(self.begin)
		self.store.add(self.after)
		self.store.add(self.before)

	def buildError(self, start, end):
		return {
			GErrorDesc.START: start,
			GErrorDesc.END: end,
			GErrorDesc.DESCRIPTION: "(description)",
			GErrorDesc.URL: None,
			GErrorDesc.SUGGESTIONS: [],
			GErrorDesc.OPTION: "(option)",
			GErrorDesc.RULE: None
		}

	def test_order(self):
		prev = 0
		for error in self.store:
			line, offset = error[GErrorDesc.START]
			self.assertGreaterEqual(line, prev)
			prev = line

	def test_len(self):
		self.assertEqual(len(self.store), 4)

	def test_search_begin(self):
		self.assertEqual(self.store.search((1, 1)), self.begin)
		self.assertEqual(self.store.search((1, 3)), self.begin)
		self.assertEqual(self.store.search((1, 5)), self.begin)

	def test_search_multi_begin_fail(self):
		self.assertEqual(self.store.search((2, 12)), None)

	def test_search_multi_begin(self):
		self.assertEqual(self.store.search((2, 52)), self.multi)

	def test_search_multi_middle(self):
		self.assertEqual(self.store.search((3, 0)), self.multi)

	def test_search_multi_end(self):
		self.assertEqual(self.store.search((4, 1)), self.multi)

	def test_search_multi_end_fail(self):
		self.assertEqual(self.store.search((4, 5)), None)

	def test_search_before(self):
		self.assertEqual(self.store.search((8, 15)), self.before)

	def test_search_after(self):
		self.assertEqual(self.store.search((8, 17)), self.after)

	def test_search_between(self):
		self.assertEqual(self.store.search((8, 16)), None)

if __name__ == '__main__':
	unittest.main()

