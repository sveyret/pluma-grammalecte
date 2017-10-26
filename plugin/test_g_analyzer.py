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
import gobject
import os

from g_config import GrammalecteConfig
from g_analyzer import GrammalecteRequester, GrammalecteAnalyzer

class MockRequester(GrammalecteRequester):
	""" Mock for the requester """
	def __init__(self, result_action):
		self.config = GrammalecteConfig()
		self.example = "Quoi ? Racontes ! Racontes-moi ! Bon sangg, parles !" \
			" Oui. Il y a des menteur partout. Je suit sidéré par la" \
			" brutales arrogance de cette homme-là. Quelle salopard ! Un" \
			" escrocs de la pire espece. Quant sera t’il châtiés pour ses" \
			" mensonge ?             Merde ! J’en aie marre."
		self.result_action = result_action
		self.grammar_errors = 0
		self.spelling_errors = 0

	def get_text(self):
		""" Get the text of the requester """
		return self.example

	def get_config(self):
		""" Get the configuration for the requester """
		return self.config

	def cb_result(self, result):
		""" Set the result of the request """
		for err_in_paragraph in result:
			for grammar_error in err_in_paragraph["lGrammarErrors"]:
				print grammar_error["sBefore"], "[", \
					grammar_error["sUnderlined"], "]", grammar_error["sAfter"]
				print "Règle :", grammar_error["sMessage"]
				print "Suggestions :", grammar_error["aSuggestions"]
				self.grammar_errors += 1
			for spelling_error in err_in_paragraph["lSpellingErrors"]:
				print "Orthographe :", spelling_error["sValue"]
				self.spelling_errors += 1
		self.result_action()

class TestGrammalecteAnalyzer(unittest.TestCase):
	def setUp(self):
		self.mainloop = gobject.MainLoop()
		self.analyzer = GrammalecteAnalyzer()
		self.requester = MockRequester(lambda : self.mainloop.quit())

	def tearDown(self):
		self.analyzer.terminate()

	def test_analyze(self):
		config = GrammalecteConfig()
		if os.path.exists(config.get_value("grammalecte-cli")):
			self.analyzer.add_request(self.requester)
			self.mainloop.run()
			self.assertEqual(self.requester.grammar_errors, 16)
			self.assertEqual(self.requester.spelling_errors, 2)
		else:
			print "WARNING: Grammalecte not found, tests skipped"

if __name__ == '__main__':
	unittest.main()

