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

class Event:
	MouseDown = 1
	MouseUp = 2
	MouseMoved = 3
	MouseScrolled = 4
	
	KeyDown = 1
	KeyUp = 2
	Text = 3
	TextMotion = 4

class MouseEvent(object):
	def __init__(self, x=0, y=0, dx=0, dy=0, scrollx=0, scrolly=0, button=0, type=0):
		self.x, self.y = x, y
		self.dx, self.dy = dx, dy
		self.scrollx, self.scrolly = scrollx, scrolly
		self.button = button
		self.type = type

class KeyEvent(object):
	def __init__(self, key=0, text='', motion=0, select=False, type=0):
		self.key = key
		self.text = text
		self.motion = motion
		self.select = select
		self.type = type

class State(object):
	def __init__(self, renderer):
		self.mouse = None
		self.key = None
		
		self.focus = None
		self.key_focus = None
		
		self.renderer = renderer
