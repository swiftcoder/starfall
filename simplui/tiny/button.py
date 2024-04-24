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

color = (1, 1, 1)
alt_color = (1, 0, 0)

class BaseButton(Element):
	def __init__(self, title='', behaviour='push', state=False, action=None):
		Element.__init__(self)
		
		self.title = title
		self.action = action
		self.behaviour = behaviour
		self.state = state
		self._render_state = state
	
	def process(self, state, size):
		if self.behaviour == 'push':
			self._push_behaviour(state, size)
		elif self.behaviour == 'toggle':
			self._toggle_behaviour(state, size)
		
		self._render(state, size)
	
	def _render(self, state, size):
		pass
	
	def _push_behaviour(self, state, size):
		if state.mouse:
			p = state.renderer.world_to_local(state.mouse.x, state.mouse.y)
			hit = size.hit_test(*p)
			
			if not state.focus and state.mouse.type == Event.MouseDown and hit:
					state.focus = self
					self.state = True
					state.mouse = None
			elif state.focus == self:
				if state.mouse.type == Event.MouseUp:
					self.state = False
					state.focus = None
					if hit and self.action:
						self.action(self)
				elif state.mouse.type == Event.MouseMoved:
					if hit:
						self.state = True
					else:
						self.state = False
				state.mouse = None
			
			self._render_state = self.state
	
	def _toggle_behaviour(self, state, size):
		if state.mouse:
			p = state.renderer.world_to_local(state.mouse.x, state.mouse.y)
			hit = size.hit_test(*p)
			
			if not state.focus and state.mouse.type == Event.MouseDown and hit:
					state.focus = self
					self._render_state = not self.state
					state.mouse = None
			elif state.focus == self:
				if state.mouse.type == Event.MouseUp:
					state.focus = None
					if hit:
						self.state = not self.state
						if self.action:
							self.action(self)
				elif state.mouse.type == Event.MouseMoved:
					if hit:
						self._render_state = not self.state
					else:
						self._render_state = self.state						
				state.mouse = None

class Button(BaseButton):
	def determine_size(self, state):
		self.pref_size = state.renderer.button_metrics(self.title, self.state)
	
	def _render(self, state, size):
		state.renderer.render_button(size, self.pref_size, self.title, self._render_state)

class Checkbox(BaseButton):
	def __init__(self, title='', state=False, action=None):
		BaseButton.__init__(self, title=title, state=state, behaviour='toggle', action=action)
	
	def determine_size(self, state):
		self.pref_size = state.renderer.checkbox_metrics(self.title, self.state)
	
	def _render(self, state, size):
		state.renderer.render_checkbox(size, self.pref_size, self.title, self._render_state)
