
from pyglet.gl import *
from ctypes import *

class VertexBuffer:
	def __init__(self, binding, usage, size, data=None):
		self.id = GLuint()
		self.binding = binding

		glGenBuffers(1, byref(self.id))

		glBindBuffer(binding, self.id)
		glBufferData(binding, size, data, usage)
		glBindBuffer(binding, 0)

	def delete(self):
		glDeleteBuffers(1, byref(self.id))

	def bind(self, binding=None):
		if not binding:
			binding = self.binding
		glBindBuffer(binding, self.id)

	def unbind(self, binding=None):
		if not binding:
			binding = self.binding
		glBindBuffer(binding, 0)
