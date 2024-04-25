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
from pyglet.gl import *

from .renderer import Renderer

from simplui.uicommon.geometry import *
from simplui.uicommon.theme import Theme


class ThemeRenderer(Renderer):
    def __init__(self, theme):
        Renderer.__init__(self)

        self.theme = Theme(theme)

        self.colour = self.theme['font_color']

        self.font = pyglet.font.load(
            name=self.theme['font'], size=self.theme['font_size'])
        self.small_font = pyglet.font.load(
            name=self.theme['font'], size=self.theme['font_size_small'])

    def begin_frame(self):
        Renderer.begin_frame(self)

        glColor3f(1, 1, 1)
        glEnable(GL_TEXTURE_2D)

    def end_frame(self):
        Renderer.end_frame(self)

        glDisable(GL_TEXTURE_2D)

    def string_offset_to_point(self, text, offset):
        return self._string_offset_to_point(self.font, text, offset)

    def string_point_to_offset(self, text, point):
        return self._string_point_to_offset(self.font, text, point)

    def button_metrics(self, title, state):
        p = self.theme['button'][('image_down' if state else 'image_up')]
        s = self.string_metrics(self.font, title)
        return s + Size(p.padding_x, p.padding_y)

    def checkbox_metrics(self, title, state):
        p = self.theme['checkbox'][(
            'image_checked' if state else 'image_unchecked')]
        s = self.string_metrics(self.font, title)
        return s + Size(p.padding_x, p.padding_y)

    def slider_metrics(self, w):
        knob = self.theme['slider']['image_knob']
        return Size(w + 1 + knob.padding_x, 1 + knob.padding_y)

    def label_metrics(self, text):
        return self.string_metrics(self.font, text) + Size(4, 4)

    def textbox_metrics(self, w, active):
        p = self.theme['textbox']['image']
        s = self.string_metrics(self.font, '')
        return s + Size(w + p.padding_x, p.padding_y)

    def window_title_bar_metrics(self, title):
        p = self.theme['window']['image_title_bar']
        s = self.string_metrics(self.small_font, title)
        return s + Size(p.padding_x, p.padding_y)

    def window_background_metrics(self, content_size):
        return content_size

    def render_button(self, size, pref_size, title, state):
        p = self.theme['button'][('image_down' if state else 'image_up')]

        y = (size.h - pref_size.h)//2
        p.draw(0, y, size.w, pref_size.h)

        x = p.padding_left + (size.w - pref_size.w)//2
        y += p.padding_bottom - self.font.descent
        self._draw_string(title, x, y)

    def render_checkbox(self, size, pref_size, title, state):
        p = self.theme['checkbox'][(
            'image_checked' if state else 'image_unchecked')]

        y = (size.h - pref_size.h)//2
        p.draw(0, y, size.w, pref_size.h)

        x = p.padding_left + (size.w - pref_size.w)//2
        y += p.padding_bottom - self.font.descent
        self._draw_string(title, x, y)

    def render_slider(self, size, pref_size, value):
        t = self.theme['slider']['image_slider']
        k = self.theme['slider']['image_knob']

        t.draw_around(t.padding_left, t.padding_bottom,
                      size.w - t.padding_x, 1)

        x = pref_size.h//2 + (size.w - pref_size.h)*value
        k.draw_around(int(x), t.padding_bottom, 1, 1)

    def render_label(self, size, pref_size, text):
        x, y = size.w//2 - pref_size.w//2 + 4, size.h//2 - \
            pref_size.h//2 + 4 - self.font.descent
        self._draw_string(text, x, y)

    def render_textbox(self, size, pref_size, text, active, caret):
        p = self.theme['textbox']['image']

        y = (size.h - pref_size.h)//2
        p.draw(0, y, size.w, pref_size.h)

        x = p.padding_left
        y += p.padding_bottom - self.font.descent

        self.push_clip()
        self.set_clip(p.padding_left, p.padding_bottom,
                      size.w-p.padding_x, size.h-p.padding_y)

        offset = self.string_offset_to_point(text, caret)

        if offset > size.w - p.padding_x - 4:
            x -= offset - size.w + p.padding_x + 4

        if active:
            h = self.font.ascent - self.font.descent
            glColor3ub(*self.colour)
            self._stroke_line(
                [(x + offset + 1, y-2), (x + offset + 1, y-2 + h)])
            glColor3f(1, 1, 1)

        self._draw_string(text, x, y)

        self.pop_clip()

    def render_window_title_bar(self, size, pref_size, title):
        p = self.theme['window']['image_title_bar']
        b = self.theme['window']['image_background']

        p.draw(-b.padding_left, 0, size.w + b.padding_x, size.h)

        x = p.padding_left + (size.w - pref_size.w)//2
        y = p.padding_bottom + (size.h - pref_size.h)//2 - self.font.descent
        self._draw_string_small(title, x, y)

    def render_window_background(self, size, pref_size):
        p = self.theme['window']['image_background']

        p.draw_around(0, 0, size.w, size.h)

    def _stroke_line(self, points):
        glBegin(GL_LINES)
        for p in points:
            glVertex2f(*p)
        glEnd()

    def _draw_string(self, text, x, y):
        str = pyglet.font.GlyphString(
            text, self.font.get_glyphs(text), int(x), int(y))
        glColor3ub(*self.colour)
        str.draw()
        glColor3f(1, 1, 1)

    def _draw_string_small(self, text, x, y):
        str = pyglet.font.GlyphString(
            text, self.small_font.get_glyphs(text), int(x), int(y))
        glColor3ub(*self.colour)
        str.draw()
        glColor3f(1, 1, 1)
