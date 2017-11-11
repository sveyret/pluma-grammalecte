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

from g_error import GErrorDesc, GErrorStore

class _GJsonEntry:
	""" Entries of the Grammalecte JSON file """
	GRAMMAR = "lGrammarErrors"
	SPELLING = "lSpellingErrors"
	LINE_START = "nStartY"
	CHAR_START = "nStartX"
	LINE_END = "nEndY"
	CHAR_END = "nEndX"
	SPELL_WORD = "sValue"
	BEFORE = "sBefore"
	WORD = "sUnderlined"
	AFTER = "sAfter"
	MESSAGE = "sMessage"
	URL = "URL"
	SUGGESTIONS = "aSuggestions"
	OPTION = "sType"
	RULE = "sRuleId"

class GErrorConverter:
	"""
		Convert errors from JSON analyzer format to internal format.
	"""
	__SPELL_PARAM = GrammalecteConfig.ANALYZE_OPTIONS + "/" \
		+ GrammalecteConfig.GRAMMALECTE_OPTION_SPELLING

	def __init__(self, config):
		"""
			Create the converter.

			:param config: the configuration to use.
			:type config: GrammalecteConfig
		"""
		self.__config = config
		self.__checkSpell = \
			self.__config.get_value(GErrorConverter.__SPELL_PARAM) is True
		self.__spellDescription = _("Unknown word.")
		self.__ignoredErrors = []
		self.__usedIgnored = []
		for ignored in self.__config.get_all_values(
			GrammalecteConfig.IGNORED_ERRORS):
			self.__ignoredErrors.append(tuple(ignored))

	def convert(self, analyzerFormat):
		"""
			Convert the analyzer format to internal format.

			:param analyzerFormat: the analyzer result.
			:type analyzerFormat: dict
			:return: the internal format
			:rtype: GErrorStore
		"""
		errors = []
		for parErrors in analyzerFormat:
			for grammError in parErrors[_GJsonEntry.GRAMMAR]:
				errors.append(self.__buildGrammError(grammError))
			if self.__checkSpell:
				for spellError in parErrors[_GJsonEntry.SPELLING]:
					errors.append(self.__buildSpellError(spellError))

		store = GErrorStore()
		for error in errors:
			if not self.__ignoreError(error):
				store.add(error)

		for ignored in self.__ignoredErrors:
			if not ignored in self.__usedIgnored:
				self.__config.del_value(
					GrammalecteConfig.IGNORED_ERRORS, list(ignored))

		return store

	def __buildGrammError(self, gError):
		"""
			Build a formated error based on analyze result grammar error.

			:param gError: the grammar error.
			:type gError: dict
			:return: the formated error
			:rtype: dict
		"""
		error = self.__buildPositionsError(gError)
		error[GErrorDesc.CONTEXT] = (
			gError[_GJsonEntry.BEFORE],
			gError[_GJsonEntry.WORD],
			gError[_GJsonEntry.AFTER])
		error[GErrorDesc.DESCRIPTION] = gError[_GJsonEntry.MESSAGE]
		url = gError[_GJsonEntry.URL]
		error[GErrorDesc.URL] = None if url == "" else url
		error[GErrorDesc.SUGGESTIONS] = gError[_GJsonEntry.SUGGESTIONS]
		error[GErrorDesc.OPTION] = gError[_GJsonEntry.OPTION]
		error[GErrorDesc.RULE] = gError[_GJsonEntry.RULE]
		return error

	def __buildSpellError(self, gError):
		"""
			Build a formated error based on analyze result spelling error.

			:param gError: the spelling error.
			:type gError: dict
			:return: the formated error
			:rtype: dict
		"""
		error = self.__buildPositionsError(gError)
		error[GErrorDesc.CONTEXT] = ("", gError[_GJsonEntry.SPELL_WORD], "")
		error[GErrorDesc.DESCRIPTION] = self.__spellDescription
		error[GErrorDesc.URL] = None
		error[GErrorDesc.SUGGESTIONS] = []
		error[GErrorDesc.OPTION] = \
			GrammalecteConfig.GRAMMALECTE_OPTION_SPELLING
		error[GErrorDesc.RULE] = None
		return error

	def __buildPositionsError(self, gError):
		"""
			Build a formated error with only start and end positions.

			:param gError: the spelling error.
			:type gError: dict
			:return: the formated error
			:rtype: dict
		"""
		error = {}
		error[GErrorDesc.START] = (
			gError[_GJsonEntry.LINE_START] - 1,
			gError[_GJsonEntry.CHAR_START]
		)
		error[GErrorDesc.END] = (
			gError[_GJsonEntry.LINE_END] - 1,
			gError[_GJsonEntry.CHAR_END]
		)
		return error

	def __ignoreError(self, error):
		"""
			Check if the formated error should be ignored.

			:param error: the formatted error.
			:type error: dict
			:return: True if should be ignored, False otherwise.
			:rtype: bool
		"""
		context = error[GErrorDesc.CONTEXT]
		if context in self.__ignoredErrors:
			if context not in self.__usedIgnored:
				self.__usedIgnored.append(context)
			return True
		else:
			return False

