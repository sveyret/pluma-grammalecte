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

import pango

from g_config import GrammalecteConfig

from g_analyzer import GrammalecteRequester, GrammalecteAnalyzer

class _GJsonEntry:
	""" Entries of the Grammalecte JSON file """
	GRAMMAR = "lGrammarErrors"
	SPELLING = "lSpellingErrors"
	LINE_START = "nStartY"
	CHAR_START = "nStartX"
	LINE_END = "nEndY"
	CHAR_END = "nEndX"

class _BufferData:
	""" The data for the current buffer """
	__TAG_GRAMMAR = "grammalecte_grammar"
	__TAG_SPELLING = "grammalecte_spelling"

	def __init__(self, vBuffer, callback):
		""" Initialize the buffer data """
		self.vBuffer = vBuffer
		if self.vBuffer != None:
			self.grammarTag, self.spellingTag = self.__init_tag(
				[_BufferData.__TAG_GRAMMAR, _BufferData.__TAG_SPELLING])
			self.__eventChangedId = self.vBuffer.connect("changed", callback)

	def __init_tag(self, tagNames):
		""" Create error tags """
		tags = []
		for tagName in tagNames:
			tag = self.vBuffer.get_tag_table().lookup(tagName)
			if tag == None:
				tag = self.vBuffer.create_tag(
					tagName, underline = pango.UNDERLINE_ERROR)
			tags.append(tag)
		return tags

	def terminate(self):
		""" Terminate usage of this buffer data """
		if self.vBuffer != None:
			self.vBuffer.disconnect(self.__eventChangedId)
			self.clear_tags([self.grammarTag, self.spellingTag])
			self.spellingTag = None
			self.grammarTag = None
			self.vBuffer = None

	def clear_tags(self, tags):
		""" Clear the tags from buffer """
		for tag in tags:
			if tag != None:
				self.vBuffer.remove_tag(
					tag,
					self.vBuffer.get_start_iter(),
					self.vBuffer.get_end_iter())

class GrammalecteAutoCorrector(GrammalecteRequester):
	""" The automatic corrector """

	__SPELL_PARAM = GrammalecteConfig.ANALYZE_OPTIONS + "/" \
		+ GrammalecteConfig.GRAMMALECTE_OPTION_SPELLING

	def __init__(self, viewHelper):
		""" Initialize the corrector """
		self.__viewHelper = viewHelper
		self.__requested = False
		self.__curBuffer = None
		view = self.__viewHelper.get_view()
		self.__bufferData = _BufferData(
			view.get_buffer(), self.on_content_changed)
		self.__eventBufferId = view.connect(
			"notify::buffer", self.on_buffer_changed)
		analyzer = self.__viewHelper.get_analyzer()
		self.__eventAnalStartId = analyzer.connect(
			"analyze-started", self.on_analyze_started)
		self.__eventAnalFinishId = analyzer.connect(
			"analyze-finished", self.on_analyze_finished)
		self.ask_request()

	def deactivate(self):
		""" Disconnect the corrector from the view """
		analyzer = self.__viewHelper.get_analyzer()
		analyzer.disconnect(self.__eventAnalFinishId)
		analyzer.disconnect(self.__eventAnalStartId)
		view = self.__viewHelper.get_view()
		view.disconnect(self.__eventBufferId)
		self.__bufferData.terminate()
		self.__bufferData = None
		self.__viewHelper = None

	def on_content_changed(self, *ignored):
		""" Called when buffer content changed """
		self.ask_request()

	def on_buffer_changed(self, *ignored):
		""" Called when the buffer was changed """
		self.__bufferData.terminate()
		self.__bufferData = _BufferData(
			self.__viewHelper.get_view().get_buffer(), self.on_content_changed)
		self.ask_request()

	def ask_request(self):
		""" Called when request is needed """
		if not self.__requested:
			self.__requested = True
			self.__viewHelper.get_analyzer().add_request(self)

	def get_config(self):
		""" Get the configuration for the requester """
		return None if self.__viewHelper == None else \
			self.__viewHelper.get_config()

	def get_text(self):
		""" Get the text of the requester """
		if self.__bufferData == None:
			return ""
		self.__curBuffer = self.__bufferData.vBuffer
		return self.__curBuffer.get_slice(
			self.__curBuffer.get_start_iter(), self.__curBuffer.get_end_iter())

	def on_analyze_started(self, analyzer, requester):
		""" Indicate that analyze has started """
		if requester != self:
			return
		self.__requested = False

	def on_analyze_finished(self, analyzer, requester, result):
		""" Set the result of the request """
		if requester != self or self.__curBuffer != self.__bufferData.vBuffer:
			return
		self.__bufferData.clear_tags(
			[self.__bufferData.grammarTag, self.__bufferData.spellingTag])
		for parErrors in result:
			for grammError in parErrors[_GJsonEntry.GRAMMAR]:
				start, end = self.__extract_limits(grammError)
				self.__curBuffer.apply_tag(
					self.__bufferData.grammarTag, start, end)
			checkSpell = self.get_config().get_value(
				GrammalecteAutoCorrector.__SPELL_PARAM)
			if checkSpell != False:
				for spellError in parErrors[_GJsonEntry.SPELLING]:
					start, end = self.__extract_limits(spellError)
					self.__curBuffer.apply_tag(
						self.__bufferData.spellingTag, start, end)
		self.__curBuffer = None

	def __extract_limits(self, errorDesc):
		""" Extract the limits from error description """
		limits = []
		for limitDesc in [
			(_GJsonEntry.LINE_START, _GJsonEntry.CHAR_START),
			(_GJsonEntry.LINE_END, _GJsonEntry.CHAR_END)]:
			line, offset = limitDesc
			iterator = self.__curBuffer.get_iter_at_line(errorDesc[line] - 1)
			iterator.set_line_offset(errorDesc[offset])
			limits.append(iterator)
		return limits

