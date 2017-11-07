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
	Manage the errors of pluma-grammalecte.

	Errors are simple dictionnaries containing the following values:
	start: a tuple containing line, offset of the start of error,
	end: a tuple containing line, offset of the end of error,
	description: a string in pango markup containing error description,
	url: a string containing an URL to a web site giving explainations on the
		error, this may be None if no URL for the given error,
	suggestions: a list containing the replacement suggestions, this may be an
		empty list, but never None,
	option: the name of the option activated to detect this kind of error,
	rule: the name of the rule detecting this kind of error, this may be None
		as all options do not have rules (spelling case).

	In order to speed up the search of an error for a given position in the
	text, errors are stored in an AVL tree, also defined in this module.
"""

class _BNode:
	"""
		A node of a binary tree.

		A node contains a value, a parent, a left and an right child. The
		parent node may be null (root node).

		Note that node removal is not implemented.
	"""

	def __init__(self, element):
		"""
			Create the node under the given parent.

			:param element: the element to store in this node.
			:type element: any
		"""
		self.__element = element
		self.__parent = None
		self.__left = None
		self.__right = None
		self.__height = None

	def __iter__(self):
		"""
			Iterate on the tree for which this node is root.

			This will create a generator to iterate on all elements.
		"""
		if self.__left is not None:
			for element in self.__left:
				yield element
		yield self.__element
		if self.__right is not None:
			for element in self.__right:
				yield element

	def __len__(self):
		"""
			Count the elements in the tree for which this node is root.

			:return: the count of elements in this tree.
			:rtype: int
		"""
		count = 1
		if self.__left is not None:
			count += len(self.__left)
		if self.__right is not None:
			count += len(self.__right)
		return count

	def __str__(self):
		"""
			Create a string representing the tree for which this node is root.

			:return: the string representing the node.
			:rtype: str
		"""
		result = ""
		if self.__left is not None:
			result += str(self.__left) + ", "
		result += str(self.__element)
		if self.__right is not None:
			result += ", " + str(self.__right)
		return result

	def add(self, node, comparator):
		"""
			Add a node in the tree for which this node is root.

			After addition, the tree may not be balanced.
			The comparator is a fuction taking two parameters (the compared
			node elements) and returning either a negative value if the left
			element is smaller than the right one, a positive value if the left
			node element is bigger than the right one or 0 if the node elements
			are of same weight.

			:param node: the node to insert.
			:param comparator: the comparator to use for sorting elements.
			:type node: _BNode
			:type comparator: function
		"""
		result = comparator(node.__element, self.__element)
		if result < 0:
			if self.__left is None:
				self.__left = node
				node.__parent = self
				self.__invalidate_height()
			else:
				self.__left.add(node, comparator)
		else:
			if self.__right is None:
				self.__right = node
				node.__parent = self
				self.__invalidate_height()
			else:
				self.__right.add(node, comparator)

	def balance(self):
		"""
			Balance the tree starting at this node.

			This will balance up to the root of the tree. This method should be
			called after each tree insertion for an AVL tree. Balancing the
			tree may require to change the tree root.

			:return: the new tree root.
			:rtype: _BNode
		"""
		leftHeight = _BNode.__height(self.__left)
		rightHeight = _BNode.__height(self.__right)
		if leftHeight - rightHeight > 1:
			if _BNode.__height(self.__left.__left) >= \
				_BNode.__height(self.__left.__right):
				self.__right_rotate()
			else:
				self.__left.__left_rotate()
				self.__right_rotate()
		elif rightHeight - leftHeight > 1:
			if _BNode.__height(self.__right.__right) >= \
				_BNode.__height(self.__right.__left):
				self.__left_rotate()
			else:
				self.__right.__right_rotate()
				self.__left_rotate()
		if self.__parent is not None:
			return self.__parent.balance()
		else:
			return self

	def __left_rotate(self):
		"""
			Rotate this node to the left of its right child.

			The right child must exist, but not the parent.
		"""
		rotated = self.__right
		rotated.__parent = self.__parent
		if rotated.__parent is not None:
			if rotated.__parent.__left is self:
				rotated.__parent.__left = rotated
			elif rotated.__parent.__right is self:
				rotated.__parent.__right = rotated
		self.__right = rotated.__left
		if self.__right is not None:
			self.__right.__parent = self
		rotated.__left = self
		self.__parent = rotated
		self.__invalidate_height()

	def __right_rotate(self):
		"""
			Rotate this node to the right of its left child.

			The left child must exist, but not the parent.
		"""
		rotated = self.__left
		rotated.__parent = self.__parent
		if rotated.__parent is not None:
			if rotated.__parent.__left is self:
				rotated.__parent.__left = rotated
			elif rotated.__parent.__right is self:
				rotated.__parent.__right = rotated
		self.__left = rotated.__right
		if self.__left is not None:
			self.__left.__parent = self
		rotated.__right = self
		self.__parent = rotated
		self.__invalidate_height()

	def search(self, comparator):
		"""
			Find a node matching the given comparator.

			The comparator is a fuction taking one parameter (the node element)
			and returning either a negative value (if the node element is too
			small), a positive value (if the node element is too big) or 0 if
			the node element is matching.

			:param comparator: the comparator used for searching.
			:type comparator: function
			:return: the found node or None if none found.
			:rtype: _BNode
		"""
		result = comparator(self.__element)
		if result == 0:
			return self
		elif result < 0 and self.__right is not None:
			return self.__right.search(comparator)
		elif result > 0 and self.__left is not None:
			return self.__left.search(comparator)
		else:
			return None

	def get_element(self):
		"""
			Get the element inside this node.

			:return: the element inside this node.
			:rtype: any
		"""
		return self.__element

	def __invalidate_height(self):
		"""
			Invalidate the height of this node.

			The previously calculated height may be obsolete, it will have to
			be recalculated if needed.
		"""
		self.__height = None
		if self.__parent is not None:
			self.__parent.__invalidate_height()

	def get_height(self):
		"""
			Get the heigh of the tree for which this node is root.

			If the height is unknown, it will be calculated.
		"""
		if self.__height is None:
			leftHeight = _BNode.__height(self.__left)
			rightHeight = _BNode.__height(self.__right)
			self.__height = max(leftHeight, rightHeight) + 1
		return self.__height

	@staticmethod
	def __height(node):
		"""
			Get the heigh of the tree for which given node is root.

			:param node: the node for which to get the height.
			:type node: _BNode
		"""
		return -1 if node is None else node.get_height()

class AvlTree:
	"""
		An AVL binary tree.

		The tree is always balanced. It contains arbitrary elements. Methods
		must be provided to the tree in order to sort elements and can also be
		provided to search elements.
		An AvlTree is iterable. Elements will then be given in ascending order.

		Note that element removal is not implemented.

		:Example:

		>>> tree = AvlTree(lambda a, b: a["value"] - b["value"])
		>>> len(tree)
		0
		>>> tree.get_height()
		-1
		>>> print tree
		<empty>

		>>> tree.add({"value": 5})
		>>> tree.add({"value": 12})
		>>> tree.add({"value": 1})
		>>> tree.add({"value": 9})
		>>> tree.add({"value": 48})
		>>> tree.add({"value": 27})
		>>> tree.add({"value": 6})

		>>> len(tree)
		7
		>>> tree.get_height()
		3
		>>> print tree
		{'value': 1}, {'value': 5}, {'value': 6}, {'value': 9}, {'value': 12}, \
{'value': 27}, {'value': 48}
		>>> tree.search({"value": 12})
		{'value': 12}
		>>> tree.search(lambda e: e["value"] - 27)
		{'value': 27}
		>>> tree.search({"value": 128})
	"""

	def __init__(self, comparator, element = None):
		"""
			Create the tree.

			The tree can contain a first element, or be empty if no element
			provided.
			The comparator is a fuction taking two parameters (the compared
			node elements) and returning either a negative value if the left
			element is smaller than the right one, a positive value if the left
			node element is bigger than the right one or 0 if the node elements
			are of same weight.

			:param comparator: the comparator used to sort elements.
			:param element: the element to insert in the tree (optional).
			:type comparator: function
			:type element: any
		"""
		self.__comparator = comparator
		self.__root = None if element is None else _BNode(element)

	def __iter__(self):
		"""
			Iterate on the tree.

			This will create a generator to iterate on all elements.
		"""
		if self.__root is not None:
			for element in self.__root:
				yield element

	def __len__(self):
		"""
			Return the count of elements in this tree.

			:return: the count of elements in the tree.
			:rtype: int
		"""
		return 0 if self.__root is None else len(self.__root)

	def __str__(self):
		"""
			Create a string representing the tree.

			:return: the string representing the tree.
			:rtype: str
		"""
		if self.__root is None:
			return "<empty>"
		else:
			return str(self.__root)

	def add(self, element):
		"""
			Add an element to the tree.

			The tree will be automatically balanced after addition.

			:param element: the element to add to the tree.
			:type element: any
		"""
		node = _BNode(element)
		if self.__root is None:
			self.__root = node
		else:
			self.__root.add(node, self.__comparator)
			self.__root = node.balance()

	def search(self, data):
		"""
			Search an element in the tree.

			The search can either be done by comparing a given element to the
			ones in the tree, or by providing a comparator function.
			The comparator is a fuction taking one parameter (the node element)
			and returning either a negative value (if the node element is too
			small), a positive value (if the node element is too big) or 0 if
			the node element is matching.

			:param data: either an element to search in the tree or a
				comparison function.
			:type data: any or function
		"""
		if self.__root is None:
			result = None
		elif callable(data):
			result = self.__root.search(data)
		else:
			result = self.__root.search(lambda e: self.__comparator(e, data))
		if result is None:
			return None
		else:
			return result.get_element()

	def get_height(self):
		return -1 if self.__root is None else self.__root.get_height()

class GErrorDesc:
	""" Entries which must be in error object """
	START = "start"
	END = "end"
	DESCRIPTION = "description"
	URL = "url"
	SUGGESTIONS = "suggestions"
	OPTION = "option"
	RULE = "rule"

class GErrorStore(AvlTree):
	"""
		An AVL tree storing the errors.

		Errors are sorted on their line and offset numbers.

		:Example:

		>>> store = GErrorStore()
		>>> store.add({"start": (12,1)})
		>>> store.add({"start": (2,1)})
		>>> store.add({"start": (1,2)})
		>>> store.add({"start": (5,16)})
		>>> store.add({"start": (5,1)})

		>>> len(store)
		5
		>>> store.get_height()
		2
		>>> print store
		{'start': (1, 2)}, {'start': (2, 1)}, {'start': (5, 1)}, \
{'start': (5, 16)}, {'start': (12, 1)}
	"""

	__DESCR = "{}<span foreground=\"red\" style=\"italic\">{}</span>{}\n{}"

	def __init__(self):
		"""
			Create the store.
		"""
		AvlTree.__init__(self, self.__compare)

	def search(self, data):
		"""
			Search the error at given position if data is tuple. Otherwise,
			simply call super function.

			:param data: the position of the error to search.
			:type data: tuple
			:return: the found error or None if none found.
			:rtype: dict (error)
		"""
		if type(data) is tuple:
			return AvlTree.search(self, lambda e: self.__searchComp(e, data))
		else:
			return AvlTree.search(self, data)

	def __compare(self, lerror, rerror):
		"""
			Compare two errors.

			The comparison is made on start line and offset numbers.

			:param lerror: the left error.
			:param rerror: the right error.
			:type lerror: dict (error)
			:type rerror: dict (error)
			:return: negative value if lerror is lower, positive if lerror is
				bigger, 0 if errors are equal.
			:rtype: int
		"""
		lline, loffset = lerror[GErrorDesc.START]
		rline, roffset = rerror[GErrorDesc.START]
		diff = lline - rline
		return diff if diff != 0 else loffset - roffset

	def __searchComp(self, error, position):
		"""
			Test if the error is at the given position.

			This will be true if the position is between start and end
			positions of the error. If so, the function will return 0,
			otherwise, it will return the difference between error start
			coordinates and given position.

			:param error: the error to test.
			:param position: the position to test.
			:type error: dict (error)
			:type position: tuple
			:return: negative value if error is too low, positive if too big, 0
				if error matchs.
			:rtype: int
		"""
		sline, soffset = error[GErrorDesc.START]
		eline, eoffset = error[GErrorDesc.END]
		pline, poffset = position
		if (sline < pline and pline < eline) or \
			(sline != eline and sline == pline and soffset <= poffset) or \
			(sline != eline and pline == eline and poffset <= eoffset) or \
			(sline == eline and sline == pline and \
			soffset <= poffset and poffset <= eoffset):
			return 0
		else:
			diff = sline - pline
			return diff if diff != 0 else soffset - poffset

if __name__ == "__main__":
	import doctest
	doctest.testmod()

