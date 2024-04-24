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

from .state import State, Event, MouseEvent, KeyEvent

class GUI(object):
	def __init__(self, renderer, windows=[]):
		self.renderer = renderer
		self.state = State(renderer)
		
		self.windows = windows
	
	def on_mouse_press(self, x, y, button, modifiers):
		self.state.mouse = MouseEvent(x=x, y=y, button=button, type=Event.MouseDown)
	
	def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
		self.state.mouse = MouseEvent(x=x, y=y, dx=dx, dy=dy, type=Event.MouseMoved)
	
	def on_mouse_motion(self, x, y, dx, dy):
		self.state.mouse = MouseEvent(x=x, y=y, dx=dx, dy=dy, type=Event.MouseMoved)
	
	def on_mouse_release(self, x, y, button, modifiers):
		self.state.mouse = MouseEvent(x=x, y=y, button=button, type=Event.MouseUp)
	
	def on_mouse_scroll(self, x, y, scrollx, scrolly):
		self.state.mouse = MouseEvent(x=x, y=y, scrollx=scrollx, scrolly=scrolly, type=Event.MouseScrolled)
	
	def on_key_press(self, symbol, modifiers):
		self.state.key = KeyEvent(key=symbol, type=Event.KeyDown)
	
	def on_key_release(self, symbol, modifiers):
		self.state.key = KeyEvent(key=symbol, type=Event.KeyUp)
	
	def on_text(self, text):
		self.state.key = KeyEvent(text=text, type=Event.Text)
	
	def on_text_motion(self, motion):
		self.state.key = KeyEvent(motion=motion, type=Event.TextMotion)
	
	def on_text_motion_select(self, motion):
		self.state.key = KeyEvent(motion=motion, select=True, type=Event.TextMotion)
	
	def realise(self):
		self.state.renderer = self.renderer
		
		self.renderer.begin_frame()
		
		for w in self.windows:
			w.realise(self.state)
		
		self.renderer.end_frame()
