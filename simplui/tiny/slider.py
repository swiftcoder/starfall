# ------------------------------------------------------------------------------
# Copyright (c) 2024 Tristam MacDonald
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

class Slider(Element):
	def __init__(self, min=0.0, max=1.0, value=0.5, w=100, continuous=True, action=None):
		Element.__init__(self)
		
		self.min = min
		self.max = max
		self.value = value
		self.w = 100
		self.continuous = continuous
		self.action = action
	
	def determine_size(self, state):
		self.pref_size = state.renderer.slider_metrics(self.w)
	
	def process(self, state, size):
		if state.mouse:
			p = state.renderer.world_to_local(state.mouse.x, state.mouse.y)
			x = (p[0] - self.pref_size.h//2) / float(size.w - self.pref_size.h)
			val = max(self.min, min(self.max, x))
			
			if not state.focus and state.mouse.type == Event.MouseDown and size.hit_test(*p):
					state.focus = self
					self.value = val
					state.mouse = None
			elif state.focus == self:
				if state.mouse.type == Event.MouseUp:
					state.focus = None
					self.value = val
					if self.action:
						self.action(self)
				elif state.mouse.type == Event.MouseMoved:
					self.value = val
					if self.continuous and self.action:
						self.action(self)
				state.mouse = None
		
		state.renderer.render_slider(size, self.pref_size, self.value/(self.max - self.min))
