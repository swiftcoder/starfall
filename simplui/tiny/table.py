# ------------------------------------------------------------------------------
# Copyright (c) 2009 Tristam MacDonald
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions 
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright 
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of DarkCoda nor the names of its
#    contributors may be used to endorse or promote products
#    derived from this software without specific prior written
#    permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# -----------------------------------------------------------------------------

from .element import *

default_padding = 4

def _mk_tuple(elem):
	if isinstance(elem, tuple):
		return elem
	return (elem,)

class Table(Element):
	def __init__(self, axis, fields, padding=default_padding, children=[]):
		Element.__init__(self)
		
		self.axis = axis
		self.fields = fields
		self.padding = padding
		
		self.children = children
	
	def determine_size(self, state):
		length = 0
		self.breadths = [0] * self.fields
		
		for c in self.children:
			max_l = 0
			
			for f, i in zip(_mk_tuple(c), list(range(self.fields))):
				f.determine_size(state)
				p = f.pref_size
			
				if p[1-self.axis] > self.breadths[i]:
					self.breadths[i] = p[1-self.axis]
				
				if p[self.axis] > max_l:
					max_l = p[self.axis]
			
			length += max_l
		
		breadth = sum(self.breadths) + (self.fields + 1)*self.padding
		length += (len(self.children) + 1)*self.padding
		
		if self.axis == 1:
			self.pref_size = Size(breadth, length)
		else:
			self.pref_size = Size(length, breadth)
	
	def process(self, state, size):
		if len(self.children) == 0:
			return
		
		if self.axis == 1:
			extra = (size.h - self.pref_size.h) // len(self.children)
			extra_b = (size.w - self.pref_size.w) // self.fields
		else:
			extra = (size.w - self.pref_size.w) // len(self.children)
			extra_b = (size.h - self.pref_size.h) // self.fields
		
		state.renderer.push_transform()
		state.renderer.translate_transform(self.padding, self.padding)
		
		step = (1, -1)[self.axis]
		alt_step = (1, -1)[1-self.axis]
		
		for c in self.children[::step]:
			max_l = max([f.pref_size[self.axis] for f in _mk_tuple(c)])
			
			state.renderer.push_transform()
			
			for f, b in zip(_mk_tuple(c)[::alt_step], self.breadths):
				if self.axis == 1:
					s = Size(b + extra_b, max_l + extra)
				else:
					s = Size(max_l + extra, b + extra_b)
				
				f.process(state, s)
				
				if self.axis == 1:
					state.renderer.translate_transform(b + self.padding, 0)
				else:
					state.renderer.translate_transform(0, b + self.padding)
			
			state.renderer.pop_transform()
			
			if self.axis == 1:
				state.renderer.translate_transform(0, max_l + self.padding)
			else:
				state.renderer.translate_transform(max_l + self.padding, 0)
		
		state.renderer.pop_transform()

class HTable(Table):
	def __init__(self, columns, padding=default_padding, children=[]):
		Table.__init__(self, 0, columns, padding, children)

class VTable(Table):
	def __init__(self, rows, padding=default_padding, children=[]):
		Table.__init__(self, 1, rows, padding, children)

class HBox(Table):
	def __init__(self, padding=default_padding, children=[]):
		Table.__init__(self, 0, 1, padding, children)

class VBox(Table):
	def __init__(self, padding=default_padding, children=[]):
		Table.__init__(self, 1, 1, padding, children)
