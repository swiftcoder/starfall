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

from .renderer import Renderer

from simplui.uicommon.geometry import *

class LineRenderer(Renderer):
	def __init__(self):
		Renderer.__init__(self)
		
		self.font = pyglet.font.load(size=10)
	
	def begin_frame(self):
		Renderer.begin_frame(self)
	
	def end_frame(self):
		Renderer.end_frame(self)
	
	def string_offset_to_point(self, text, offset):
		return self._string_offset_to_point(self.font, text, offset)
	def string_point_to_offset(self, text, point):
		return self._string_point_to_offset(self.font, text, point)
	
	def button_metrics(self, title, state):
		return self.string_metrics(self.font, title) + Size(8, 8)
	def checkbox_metrics(self, title, state):
		s = self.string_metrics(self.font, title)
		return Size(s.w + 12 + s.h, s.h + 8)
	def slider_metrics(self, w):
		return Size(w + 16, 16)
	def label_metrics(self, text):
		return self.string_metrics(self.font, text) + Size(8, 8)
	def textbox_metrics(self, w, active):
		return self.string_metrics(self.font, '') + Size(w + 8, 8)
	def window_title_bar_metrics(self, title):
		return self.string_metrics(self.font, title) + Size(8, 8)
	def window_background_metrics(self, content_size):
		return content_size
	
	def render_button(self, size, pref_size, title, state):
		if state:
			self._set_colour(1, 0, 0)
		else:
			self._set_colour(1, 1, 1)
		
		self._stroke_box(size)
		
		x, y = size.w//2 - pref_size.w//2 + 4, size.h//2 - pref_size.h//2 + 4 - self.font.descent
		self._draw_string(title, x, y)
	
	def render_checkbox(self, size, pref_size, title, state):
		self._set_colour(1, 1, 1)
		
		x, y = pref_size.h, size.h//2 - pref_size.h//2 + 4 - self.font.descent
		self._draw_string(title, x, y)
		
		s = pref_size.h - 8
		
		self._stroke_box( Size(s, s), 4, 4 )
		
		if state:
			self._set_colour(1, 0, 0)
			self._fill_box( Size(s-2, s-2), 5, 5 )
	
	def render_slider(self, size, pref_size, value):
		cy = size.h//2
		
		self._set_colour(1, 1, 1)
		self._stroke_box( Size(size.w, 4), 0, cy - 2 )
		
		x = 1 + (size.w - pref_size.h)*value
		self._set_colour(0, 0, 1)
		self._fill_box( Size(13, 13), x, cy - 5 )
	
	def render_label(self, size, pref_size, text):
		self._set_colour(1, 1, 1)
		
		x, y = size.w//2 - pref_size.w//2 + 4, size.h//2 - pref_size.h//2 + 4 - self.font.descent
		self._draw_string(text, x, y)
	
	def render_textbox(self, size, pref_size, text, active, caret):		
		self._set_colour(1, 1, 1)
		self._stroke_box(size)
		
		x, y = 4, size.h//2 - pref_size.h//2 + 4 - self.font.descent
		
		self.push_clip()
		self.set_clip(4, 4, size.w-8, size.h-8)
		
		offset = self.string_offset_to_point(text, caret)
		
		if offset > size.w - 12:
			x -= offset - size.w + 12
		
		if active:
			h = self.font.ascent - self.font.descent
			self._stroke_line([(x + offset + 1, y-2), (x + offset + 1, y-2 + h)])
		
		self._draw_string(text, x, y)
		
		self.pop_clip()
	
	def render_window_title_bar(self, size, pref_size, title):
		self._set_colour(1, 1, 1)
		self._stroke_box(size)
		
		x, y = size.w//2 - pref_size.w//2 + 4, size.h//2 - pref_size.h//2 + 4 - self.font.descent
		self._draw_string(title, x, y)
	
	def render_window_background(self, size, pref_size):
		self._set_colour(0, 0, 1)
		self._stroke_box(size)
	
	def _set_colour(self, r, g, b, a=1.0):
		glColor4f(r, g, b, a)
	
	def _stroke_line(self, points):
		glBegin(GL_LINES)
		for p in points:
			glVertex2f(*p)
		glEnd()
	
	def _stroke_box(self, s, x=0, y=0):
		glBegin(GL_LINE_LOOP)
		glVertex2f(x, y)
		glVertex2f(x + s.w, y)
		glVertex2f(x + s.w, y + s.h)
		glVertex2f(x, y + s.h)
		glEnd()
	
	def _fill_box(self, s, x=0, y=0):
		glBegin(GL_QUADS)
		glVertex2f(x, y)
		glVertex2f(x + s.w, y)
		glVertex2f(x + s.w, y + s.h)
		glVertex2f(x, y + s.h)
		glEnd()
	
	def _draw_string(self, text, x, y):
		str = pyglet.font.GlyphString(text, self.font.get_glyphs(text), int(x), int(y))
		glEnable(GL_TEXTURE_2D)
		str.draw()
		glDisable(GL_TEXTURE_2D)
