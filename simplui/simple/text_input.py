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

import pyglet

from .shape import Rectangle
from .widget import Widget

class TextInput(Widget):
	"""Text input field"""
	def __init__(self, **kwargs):
		'''Create a text input control
		
		Keyword arguments:
		name -- unique widget identifier
		text -- intitial value
		action -- callback to be invoked when text is entered
		'''
		Widget.__init__(self, **kwargs)
		
		self.document = pyglet.text.document.UnformattedDocument(kwargs.get('text', ''))
		self.layout = pyglet.text.layout.IncrementalTextLayout(self.document, 1, 1, multiline=False)
		
		font = self.document.get_font()
		height = font.ascent - font.descent
		
		self.layout.x, self.layout.y = 2, 2
		self.caret = pyglet.text.caret.Caret(self.layout)
		
		self.elements['layout'] = self.layout
		self.shapes['frame'] = Rectangle()
		
		self.action = kwargs.get('action', None)
		self._focused = False
		self.caret.visible = False
	
	def _get_text(self):
		return self.document.text
	def _set_text(self, text):
		self.document.text = text
	text = property(_get_text, _set_text)
	
	def update_theme(self, theme):
		Widget.update_theme(self, theme)
		
		if theme:
			patch = theme['textbox']['image']
			
			self.shapes['frame'].patch = patch
			self.document.set_style(0, len(self.document.text), {'font_size': theme['font_size'], 'color': theme['font_color']})
			
			font = self.document.get_font()
			height = font.ascent - font.descent
			
			self._pref_size = (self.w, patch.padding_bottom + height + patch.padding_top)
			
			self.elements['layout'].width = self.w - patch.padding_left - patch.padding_right
			self.elements['layout'].height = height
	
	def update_elements(self):		
		if self._dirty and self.theme:
			patch = self.theme['textbox']['image']
			
			font = self.document.get_font()
			height = font.ascent - font.descent
			
			bottom = 0
			if self.valign == 'center':
				bottom = self.h/2 - self._pref_size[1]/2
			elif self.valign == 'top':
				bottom = self.h - self._pref_size[1]
			
			self.elements['layout'].x = self._gx + patch.padding_left
			self.elements['layout'].y = self._gy + bottom + patch.padding_bottom
			self.elements['layout'].width = self.w - patch.padding_left - patch.padding_right
			
			self.shapes['frame'].update(self._gx + patch.padding_left, self._gy + bottom + patch.padding_bottom, self.w - patch.padding_left - patch.padding_right, height)
		
		Widget.update_elements(self)
	
	def on_mouse_press(self, x, y, button, modifiers):
		if button == pyglet.window.mouse.LEFT and self.hit_test(x, y) and not self._focused:
			self._focused = True
			self.find_root().focus.append(self)
			self.caret.visible = True
			self.caret.on_mouse_press(x - self._gx - 2, y - self._gy - 2, button, modifiers)
			return pyglet.event.EVENT_HANDLED
		if button == pyglet.window.mouse.LEFT and self._focused:
			if self.hit_test(x, y):
				self.caret.on_mouse_press(x - self._gx - 2, y - self._gy - 2, button, modifiers)
			else:
				self.caret.visible = False
				self.find_root().focus.pop()
				self._focused = False
				if self.action:
					self.action(self)
			return pyglet.event.EVENT_HANDLED
		
		Widget.on_mouse_press(self, x, y, button, modifiers)
		return pyglet.event.EVENT_UNHANDLED
	
	def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
		if self._focused:
			self.caret.on_mouse_drag(x - self._gx - 2, y - self._gy - 2, dx, dy, button, modifiers)
			return pyglet.event.EVENT_HANDLED
				
		Widget.on_mouse_drag(self, x, y, dx, dy, button, modifiers)
		return pyglet.event.EVENT_UNHANDLED
	
	def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
		if self._focused:
			self.caret.on_mouse_scroll(x - self._gx - 2, y - self._gy - 2, scroll_x, scroll_y)
			return pyglet.event.EVENT_HANDLED
		
		Widget.on_mouse_scroll(self, x, y, scroll_x, scroll_y)
		return pyglet.event.EVENT_UNHANDLED
	
	def on_key_press(self, symbol, modifiers):
		from pyglet.window import key
		
		if self._focused and symbol in (key.ENTER, key.TAB):
			self.caret.visible = False
			self.find_root().focus.pop()
			self._focused = False
			if self.action:
				self.action(self)
			return pyglet.event.EVENT_HANDLED
		
		Widget.on_key_press(self, symbol, modifiers)
		return pyglet.event.EVENT_UNHANDLED
	
	def on_text(self, text):
		if self._focused:
			self.caret.on_text(text)
			return pyglet.event.EVENT_HANDLED
		
		Widget.on_text(self, text)
		return pyglet.event.EVENT_UNHANDLED
	
	def on_text_motion(self, motion, select=False):
		if self._focused:
			self.caret.on_text_motion(motion, select)
			return pyglet.event.EVENT_HANDLED
		
		Widget.on_text_motion(self, motion, select)
		return pyglet.event.EVENT_UNHANDLED
