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

from pyglet.window import key as KEY

from .element import *
from .state import Event

color = (1, 1, 1)
alt_color = (1, 0, 0)

class Textbox(Element):
	def __init__(self, text='', w=100, action=None):
		Element.__init__(self)
		
		self.text = text
		self.action = action
		self.caret = len(text)
		self.w = 100
	
	def determine_size(self, state):
		self.pref_size = state.renderer.textbox_metrics(self.w, state.key_focus==self)
	
	def process(self, state, size):
		if state.mouse:
			if state.mouse.type == Event.MouseDown:
					p = state.renderer.world_to_local(state.mouse.x, state.mouse.y)
					hit = size.hit_test(*p)
					
					if hit and not state.key_focus:
						state.key_focus = self
						state.mouse = None
						self.caret = len(self.text)
					elif state.key_focus == self:
						if not hit:
							state.key_focus = None
							if self.action:
								self.action(self)
							self.caret = 0
						else:
							self.caret = state.renderer.string_point_to_offset(self.text, p[0])
						state.mouse = None
		
		if state.key and state.key_focus == self:
			if state.key.type == Event.Text:
				if state.key.text in ('\r', '\n'):
					state.key_focus = None
					if self.action:
						self.action(self)
					self.caret = 0
				else:	
					self.text = self.text[0:self.caret] + state.key.text + self.text[self.caret:]
					self.caret += len(state.key.text)
				state.key = None
			elif state.key.type == Event.TextMotion:
				if state.key.motion == KEY.MOTION_BACKSPACE:
					if len(self.text) > 0:
						self.caret -= 1
						self.text = self.text[0:self.caret] + self.text[self.caret+1:]
				elif state.key.motion == KEY.DELETE:
					if len(self.text) > 0:
						self.text = self.text[0:self.caret+1] + self.text[self.caret+2:]
				elif state.key.motion == KEY.MOTION_LEFT:
					if self.caret > 0:
						self.caret -= 1
				elif state.key.motion == KEY.MOTION_RIGHT:
					if self.caret < len(self.text):
						self.caret += 1
				state.key = None
			elif state.key.type == Event.KeyDown:
				if state.key.key in (KEY.TAB, KEY.ESCAPE):
					state.key_focus = None
					if self.action:
						self.action(self)
					self.caret = 0
					state.key = None
		
		state.renderer.render_textbox(size, self.pref_size, self.text, state.key_focus==self, self.caret)
