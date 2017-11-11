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
import gobject
import pango

from g_config import GrammalecteConfig

from g_analyzer import GrammalecteRequester, GrammalecteAnalyzer
from g_converter import GErrorConverter
from g_error import GErrorDesc, GErrorStore
from g_popup import GPopupMenu

class _BufferData:
	""" The data for the current buffer """
	__TAG_GRAMMAR = "grammalecte_grammar"
	__TAG_SPELLING = "grammalecte_spelling"

	def __init__(self, vBuffer, callback):
		""" Initialize the buffer data """
		self.vBuffer = vBuffer
		if self.vBuffer is not None:
			self.grammarTag, self.spellingTag = self.__init_tag(
				[_BufferData.__TAG_GRAMMAR, _BufferData.__TAG_SPELLING])
			self.__eventChangedId = self.vBuffer.connect("changed", callback)

	def __init_tag(self, tagNames):
		""" Create error tags """
		tags = []
		for tagName in tagNames:
			tag = self.vBuffer.get_tag_table().lookup(tagName)
			if tag is None:
				tag = self.vBuffer.create_tag(
					tagName, underline = pango.UNDERLINE_ERROR)
			tags.append(tag)
		return tags

	def terminate(self):
		""" Terminate usage of this buffer data """
		if self.vBuffer is not None:
			self.vBuffer.disconnect(self.__eventChangedId)
			self.clear_tags([self.grammarTag, self.spellingTag])
			self.spellingTag = None
			self.grammarTag = None
			self.vBuffer = None

	def clear_tags(self, tags):
		""" Clear the tags from buffer """
		for tag in tags:
			if tag is not None:
				self.vBuffer.remove_tag(
					tag,
					self.vBuffer.get_start_iter(),
					self.vBuffer.get_end_iter())

class GrammalecteAutoCorrector(GrammalecteRequester):
	""" The automatic corrector """
	__TICK_DURATION = 100
	__TOOLTIP = "{1}<span foreground=\"red\" style=\"italic\">{2}</span>{3}" \
		+ "\n<span foreground=\"blue\" weight=\"bold\">{0}</span>"

	def __init__(self, viewHelper):
		""" Initialize the corrector """
		self.__viewHelper = viewHelper
		self.__requested = False
		self.__curBuffer = None
		self.__store = GErrorStore()
		analyzer = self.__viewHelper.get_analyzer()
		self.__eventAnalStartId = analyzer.connect(
			"analyze-started", self.on_analyze_started)
		self.__eventAnalFinishId = analyzer.connect(
			"analyze-finished", self.on_analyze_finished)
		view = self.__viewHelper.get_view()
		view.set_property("has_tooltip", True)
		self.__eventTooltipId = view.connect(
			"query-tooltip", self.on_query_tooltip)
		self.__menuPosition = view.get_buffer().get_start_iter()
		self.__eventMouseClicked = view.connect(
			"button-press-event", self.on_mouse_clicked)
		self.__eventPopupMenu = view.connect("popup-menu", self.on_popup_menu)
		self.__eventPopulatePopup = view.connect(
			"populate-popup", self.on_populate_popup)
		self.__bufferData = _BufferData(
			view.get_buffer(), self.on_content_changed)
		self.__eventBufferId = view.connect(
			"notify::buffer", self.on_buffer_changed)
		self.__eventConfigUpdated = self.get_config().connect(
			"updated", self.on_conf_updated)
		self.__eventConfigCleared = self.get_config().connect(
			"cleared", self.on_conf_cleared)
		self.__tick_count = 1
		self.__ask_request()
		gobject.timeout_add(
			GrammalecteAutoCorrector.__TICK_DURATION, self.__add_request)

	def deactivate(self):
		""" Disconnect the corrector from the view """
		self.get_config().disconnect(self.__eventConfigUpdated)
		self.get_config().disconnect(self.__eventConfigCleared)
		view = self.__viewHelper.get_view()
		view.disconnect(self.__eventBufferId)
		self.__bufferData.terminate()
		self.__bufferData = None
		view.disconnect(self.__eventPopulatePopup)
		view.disconnect(self.__eventPopupMenu)
		view.disconnect(self.__eventMouseClicked)
		self.__menuPosition = None
		view.disconnect(self.__eventTooltipId)
		analyzer = self.__viewHelper.get_analyzer()
		analyzer.disconnect(self.__eventAnalFinishId)
		analyzer.disconnect(self.__eventAnalStartId)
		self.__store = None
		self.__curBuffer = None
		self.__viewHelper = None

	def on_analyze_started(self, analyzer, requester):
		""" Indicate that analyze has started """
		if requester is not self:
			return
		self.__requested = False

	def on_analyze_finished(self, analyzer, requester, result):
		""" Set the result of the request """
		if requester is not self or \
			self.__curBuffer is not self.get_buffer():
			return
		self.__bufferData.clear_tags(
			[self.__bufferData.grammarTag, self.__bufferData.spellingTag])
		self.__store = GErrorConverter(self.get_config()).convert(result)
		for error in self.__store:
			start, end = self.convert_limits(error, self.__curBuffer)
			tag = self.__bufferData.spellingTag if error[GErrorDesc.OPTION] \
				== GrammalecteConfig.GRAMMALECTE_OPTION_SPELLING \
				else self.__bufferData.grammarTag
			self.__curBuffer.apply_tag(tag, start, end)
		self.__curBuffer = None

	def convert_limits(self, error, vBuffer):
		""" Convert the limits from error to iterator """
		limits = []
		for limitDesc in [GErrorDesc.START, GErrorDesc.END]:
			line, offset = error[limitDesc]
			iterator = vBuffer.get_iter_at_line(line)
			iterator.set_line_offset(offset)
			limits.append(iterator)
		return limits

	def on_query_tooltip(self, view, x, y, keyboard, tooltip):
		""" Manage tooltip query event """
		if keyboard:
			buff = view.get_buffer()
			pos = buff.get_iter_at_mark(buff.get_insert())
		else:
			buffPos = view.window_to_buffer_coords(gtk.TEXT_WINDOW_TEXT, x, y)
			pos = view.get_iter_at_location(*buffPos)
		line = pos.get_line()
		offset = pos.get_line_offset()
		error = self.__store.search((line, offset))
		if error is not None:
			tooltip.set_markup(GrammalecteAutoCorrector.__TOOLTIP.format(
				error[GErrorDesc.DESCRIPTION], *error[GErrorDesc.CONTEXT]))
			return True
		else:
			return False

	def on_mouse_clicked(self, view, event):
		""" Manage the mouse clicked event """
		if event.button == 3:
			coords = view.window_to_buffer_coords(
				gtk.TEXT_WINDOW_TEXT, int(event.x), int(event.y))
			self.__menuPosition = view.get_iter_at_location(*coords)
		return False

	def on_popup_menu(self, view):
		""" Manage the popup menu event """
		buff = view.get_buffer()
		self.__menuPosition = buff.get_iter_at_mark(buff.get_insert())
		return False

	def on_populate_popup(self, view, menu):
		""" Manage the populate popup event """
		line = self.__menuPosition.get_line()
		offset = self.__menuPosition.get_line_offset()
		error = self.__store.search((line, offset))
		if error is not None:
			GPopupMenu(menu, error, self)

	def on_content_changed(self, *ignored):
		""" Called when buffer content changed """
		self.__ask_request()

	def on_buffer_changed(self, *ignored):
		""" Called when the buffer was changed """
		self.__bufferData.terminate()
		self.__bufferData = _BufferData(
			self.__viewHelper.get_view().get_buffer(), self.on_content_changed)
		self.__ask_request()

	def on_conf_updated(self, config, level, xPath, *ignored):
		""" Manage the configuration updated event """
		if xPath in (
			GrammalecteConfig.AUTO_ANALYZE_ACTIVE,
			GrammalecteConfig.AUTO_ANALYZE_TIMER,
			GrammalecteConfig.GRAMMALECTE_OPTIONS_PARAMS,
			GrammalecteConfig.GRAMMALECTE_OPTIONS_REGEX):
			return
		self.__ask_request()

	def on_conf_cleared(self, *ignored):
		""" Manage the configuration cleared event """
		self.__ask_request()

	def __ask_request(self):
		""" Called when request is needed """
		if not self.__requested:
			self.__tick_count = self.get_config().get_value(
				GrammalecteConfig.ANALYZE_WAIT_TICKS)

	def __add_request(self):
		""" If idle time is enough, execute the request """
		if self.__store is None:
			return False
		if self.__tick_count >= 0:
			self.__tick_count -= 1
		if self.__tick_count == 0:
			self.__requested = True
			self.__viewHelper.get_analyzer().add_request(self)
		return True

	def get_config(self):
		""" Get the configuration for the requester """
		return None if self.__viewHelper is None else \
			self.__viewHelper.get_config()

	def get_text(self):
		""" Get the text of the requester """
		if self.__bufferData is None:
			return ""
		self.__curBuffer = self.get_buffer()
		return self.__curBuffer.get_slice(
			self.__curBuffer.get_start_iter(), self.__curBuffer.get_end_iter())

	def get_buffer(self):
		""" Get the current buffer """
		return self.__bufferData.vBuffer

