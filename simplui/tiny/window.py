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
from .state import Event

class _TitleBar(Element):
	def __init__(self, title, window):
		self.title = title
		self.window = window
	
	def determine_size(self, state):
		self.pref_size = state.renderer.window_title_bar_metrics(self.title)
	
	def process(self, state, size):
		if state.mouse:			
			if not state.focus and state.mouse.type == Event.MouseDown:
					p = state.renderer.world_to_local(state.mouse.x, state.mouse.y)
					if size.hit_test(*p):
						state.focus = self
						state.mouse = None
			elif state.focus == self:
				if state.mouse.type == Event.MouseUp:
					state.focus = None
				elif state.mouse.type == Event.MouseMoved:
					self.window.x += state.mouse.dx
					self.window.y += state.mouse.dy
				state.mouse = None
		
		state.renderer.render_window_title_bar(size, self.pref_size, self.title)

class _Background(Element):
	def __init__(self):
		self.content = None
	
	def determine_size(self, state):
		if self.content:
			self.content.determine_size(state)
			size = self.content.pref_size
		else:
			size = Size()
		self.pref_size = state.renderer.window_background_metrics(size)
	
	def process(self, state, size):
		state.renderer.render_window_background(size, self.pref_size)
		
		if self.content:
			self.content.process( state, Size(size.w, size.h) )

class Window(object):
	def __init__(self, x, y, title='untitled', content=None):
		self.x, self.y = x, y
		
		from .table import VBox
		
		self._title_bar = _TitleBar(title, self)
		self._background = _Background()
		self._frame = VBox(padding=0, children=[ self._title_bar, self._background ])
		
		self.content = content
	
	def get_title(self):
		return self._title_bar.title
	def set_title(self, title):
		self._title_bar.title = title
	title = property(get_title, set_title)
	
	def get_content(self):
		return self._background.content
	def set_content(self, content):
		self._background.content = content
	content = property(get_content, set_content)
	
	def realise(self, state):
		self._frame.determine_size(state)
		s = self._frame.pref_size
		
		state.renderer.push_transform()
		state.renderer.translate_transform(self.x, self.y - s.h)
		
		self._frame.process(state, s)
		
		state.renderer.pop_transform()
