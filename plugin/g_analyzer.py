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

""" Manage the grammar analyzis """

import os
import subprocess
import tempfile
import json
import gobject
import Queue

from g_config import GrammalecteConfig

class GrammalecteRequester:
	"""
		An object which can request an analyzis.

		Any object calling the analyzer must override all these methods.
	"""

	def get_config(self):
		"""
			Get the configuration for the requester.

			:return: the requester configuration.
			:rtype: GrammalecteConfig
		"""
		pass

	def get_text(self):
		"""
			Get the text of the requester.

			:return: the text to be analyzed.
			:rtype: str
		"""
		pass

	def cb_result(self, result):
		"""
			Give the result of the request.

			:param result: the result of the request.
			:type result: dict
		"""
		pass

class _TempFile():
	""" A temporary file """

	def __init__(self):
		""" Create the file """
		self.__descriptor, self.__path = tempfile.mkstemp()
		self.close()

	def read(self):
		""" Read the file and return text """
		self.open_read()
		result = self.__descriptor.read()
		self.close()
		return result

	def write(self, text):
		""" Write the content of text to the file """
		self.open_write()
		self.__descriptor.write(text)
		self.close()

	def open_read(self):
		""" Open file for reading """
		self.close()
		self.__descriptor = open(self.__path, 'r')
		return self.__descriptor

	def open_write(self):
		""" Open file for writing """
		self.close()
		self.__descriptor = open(self.__path, 'w')
		return self.__descriptor

	def get_path(self):
		""" Get the path to the file """
		return self.__path

	def close(self):
		""" Close the descriptor if open """
		if self.__descriptor != None:
			if type(self.__descriptor) is int:
				os.close(self.__descriptor)
			else:
				self.__descriptor.close()
			self.__descriptor = None

	def terminate(self):
		""" Close and remove the file, the file cannot be used anymore """
		self.close()
		os.remove(self.__path)

class _State:
	""" A state of the state machine """
	def __init__(self, analyzer):
		""" Initialize the state """
		self._analyzer = analyzer

	def execute(self):
		"""
			Execute the current state.

			This will execute the actions for the current state. Calculate
			and return the next state.

			:return: the next state to execute, may be self.
			:rtype: _State
		"""
		if self._is_transition_open():
			return self._start_next_state()
		else:
			return self

	def _is_transition_open(self):
		"""
			Test if transition is open.

			:return: True if the transition is open and next state can be
			started, False otherwise
			:rtype: boolean
		"""
		pass

	def _start_next_state(self):
		"""
			Initialize the next state.

			After execution of this method, the next state must be started,
			waiting for its own transition to be open.

			:return: The next state.
			:rtype: _State
		"""
		pass

class _StateWaiting(_State):
	"""
		The waiting state.

		In this state, the analyzer is waiting for a requester to ask for
		an analyzis.
	"""

	def __init__(self, analyzer):
		""" Initialize the state """
		_State.__init__(self, analyzer)

	def _is_transition_open(self):
		""" Test if transition is open """
		return not self._analyzer._queue.empty()

	def _start_next_state(self):
		""" Initialize the next state """
		requester = self._analyzer._queue.get()
		config = requester.get_config()
		self._analyzer._input.write(requester.get_text())
		processArgs = []
		processArgs.append(config.get_value(
			GrammalecteConfig.GRAMMALECTE_PYTHON_EXE))
		processArgs.append(config.get_value(GrammalecteConfig.GRAMMALECTE_CLI))
		for arg in config.get_value(
			GrammalecteConfig.GRAMMALECTE_ANALYZE_PARAMS):
			processArgs.append(arg)
		processArgs.append("-f")
		processArgs.append(self._analyzer._input.get_path())
		process = subprocess.Popen(
			processArgs,
			stdout = self._analyzer._output.open_write(),
			stderr = self._analyzer._error.open_write())
		return _StateAnalyzing(self._analyzer, requester, process)

class _StateAnalyzing(_State):
	"""
		The analyzing state.

		In this state, the analyzer has launched an analyzis and is waiting
		for process to complete.
	"""

	def __init__(self, analyzer, requester, process):
		""" Initialize the state """
		_State.__init__(self, analyzer)
		self.__requester = requester
		self.__process = process

	def _is_transition_open(self):
		""" Test if transition is open """
		return self.__process.poll() != None

	def _start_next_state(self):
		""" Initialize the next state """
		result = []
		if self.__process.returncode == 0:
			result = json.loads(self._analyzer._output.read())["data"]
		else:
			print _("Error: Grammalecte process did not terminate" \
				" properly:\n{}").format(self._analyzer._error.read())
		self._analyzer._output.close()
		self._analyzer._error.close()
		self.__requester.cb_result(result)
		return _StateWaiting(self._analyzer)

class GrammalecteAnalyzer(object):
	"""
		Class managing grammar analyzis.

		There should not be many instances of the analyzer. A good choice is to
		create one instance per window. Each instance will treat all recieved
		requests one by one. Requests are enqueued in a FIFO.
		This class is managed as a state machine.
	"""

	def __init__(self):
		""" Initialize the analyzer """
		# Define instance data
		self._queue = Queue.Queue()
		self._input = _TempFile()
		self._output = _TempFile()
		self._error = _TempFile()
		self.__state = _StateWaiting(self)

		# Define timer
		config = GrammalecteConfig()
		gobject.timeout_add(
			config.get_value(GrammalecteConfig.AUTO_ANALYZE_TIMER),
			self.__run)

	def __run(self):
		if self.__state == None or self._queue == None:
			return False
		else:
			try:
				self.__state = self.__state.execute()
				return True
			except Exception as e:
				print _("Exception: {}").format(e)
				self.terminate()

	def add_request(self, requester):
		"""
			Request analyzis for the given requester.

			:param requester: The view requesting analyzis.
			:type requester: GrammalecteRequester
		"""
		self._queue.put(requester)

	def terminate(self):
		""" Terminate the analyzer, which will not be usable anymore """
		self.__state = None
		self._error.terminate()
		self._output.terminate()
		self._input.terminate()
		self._queue = None

