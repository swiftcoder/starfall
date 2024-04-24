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

import pyglet
from pyglet.gl import *

from simplui.uicommon.geometry import Size, Rect

class Renderer(object):
	def __init__(self):
		self.transforms = [(0, 0)]
		self.clips = [Rect()]
	
	def begin_frame(self):
		view = (GLint * 4)()
		glGetIntegerv(GL_VIEWPORT, view)
		
		self.clips = [Rect(view[0], view[1], view[2], view[3])]
		
		glScissor(*self.clips[0])
		
		glEnable(GL_SCISSOR_TEST)
		glDisable(GL_DEPTH_TEST)

	def end_frame(self):
		glEnable(GL_DEPTH_TEST)
		glDisable(GL_SCISSOR_TEST)
	
	def push_transform(self):
		t = self.transforms[-1]
		self.transforms.append( t )
	
	def translate_transform(self, x, y):
		t = self.transforms[-1]
		self.transforms[-1] = (t[0] + x, t[1] + y)
		
		glLoadIdentity()
		glTranslatef(t[0] + x, t[1] + y, 0)
	
	def pop_transform(self):
		self.transforms.pop()
		t = self.transforms[-1]
		
		glLoadIdentity()
		glTranslatef(t[0], t[1], 0)
	
	def world_to_local(self, x, y):
		t = self.transforms[-1]
		return (x - t[0], y - t[1])
	
	def local_to_world(self, x, y):
		t = self.transforms[-1]
		return (x - t[0], y - t[1])
	
	def push_clip(self):
		c = self.clips[-1]
		self.clips.append( c)
	
	def set_clip(self, x, y, w, h):
		t = self.transforms[-1]
		
		r = Rect(t[0] + x, t[1] + y, w, h).intersect( self.clips[-2] )
		
		self.clips[-1] = r
		
		glScissor(*[int(i) for i in self.clips[-1]])
	
	def pop_clip(self):
		self.clips.pop()
		glScissor(*self.clips[-1])
	
	def string_metrics(self, font, text):
		str = pyglet.font.GlyphString( text, font.get_glyphs(text) )
		return Size(str.get_subwidth(0, len(text)), font.ascent - font.descent)
	
	def string_offset_to_point(self, text, offset):
		pass
	def string_point_to_offset(self, text, point):
		pass
	
	def _string_offset_to_point(self, font, text, offset):
		str = pyglet.font.GlyphString(text, font.get_glyphs(text))
		return str.get_subwidth(0, offset)
	
	def _string_point_to_offset(self, font, text, point):
		glyphs = font.get_glyphs(text)
		for g, i in zip(glyphs, list(range(len(text)))):
			point -= g.advance
			if point <= 0:
				return i
		return len(text)

	def button_metrics(self, title, state):
		pass
	def checkbox_metrics(self, title, state):
		pass
	def slider_metrics(self, w):
		pass
	def label_metrics(self, text):
		pass
	def textbox_metrics(self, w, active):
		pass
	def window_title_bar_metrics(self, title):
		pass
	def window_background_metrics(self, content_size):
		pass
	
	def render_button(self, size, pref_size, title, state):
		pass
	def render_checkbox(self, size, pref_size, title, state):
		pass
	def render_slider(self, size, pref_size, value):
		pass
	def render_label(self, size, pref_size, text):
		pass
	def render_textbox(self, size, pref_size, text, active, caret):
		pass
	def render_window_title_bar(self, size, pref_size, title):
		pass
	def render_window_background(self, size, pref_size):
		pass
