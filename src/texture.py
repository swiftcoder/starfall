
from typing import Optional, Any
from pyglet import image
from pyglet.gl import *
from ctypes import *

class Texture:
	def __init__(self, target, id, width, height=1, depth=1):
		self.target = target
		self.id = id

		self.width = width
		self.height = height
		self.depth = depth

		self.tex : Optional[Any] = None

	def delete(self):
		if self.tex:
			self.tex.delete()
		else:
			glDeleteTextures(1, byref(self.id))

	def bind(self, texUnit = 0):
		if self.id != 0:
			glActiveTexture(GL_TEXTURE0 + texUnit)
			glEnable(self.target)
			glBindTexture(self.target, self.id)

	def unbind(self, texUnit = 0):
		if self.id != 0:
			glActiveTexture(GL_TEXTURE0 + texUnit)
			glBindTexture(self.target, 0)
			glDisable(self.target)

	@classmethod
	def create1D(cls, width, format=GL_RGBA, internal_format=GL_RGBA, type=GL_UNSIGNED_BYTE, data=None, filter=GL_LINEAR, wrap=GL_CLAMP_TO_EDGE):
		id = GLuint()
		target = GL_TEXTURE_1D

		glGenTextures(1, pointer(id))
		glBindTexture(target, id)

		glTexImage1D(target, 0, internal_format, width, 0, format, type, data)

		glTexParameteri( target, GL_TEXTURE_MIN_FILTER, filter );
		glTexParameteri( target, GL_TEXTURE_MAG_FILTER, filter );

		glTexParameteri( target, GL_TEXTURE_WRAP_S, wrap );

		t = cls(target, id, width)

		return t

	@classmethod
	def create2D(cls, width, height, format=GL_RGBA, internal_format=GL_RGBA, type=GL_UNSIGNED_BYTE, data=None, filter=GL_LINEAR, wrap=GL_CLAMP_TO_EDGE, mipmap=False):
		id = GLuint()
		target = GL_TEXTURE_2D

		glGenTextures(1, pointer(id))
		glBindTexture(target, id)

		glTexImage2D(target, 0, internal_format, width, height, 0, format, type, data)

		if mipmap:
			glTexParameteri( target, GL_GENERATE_MIPMAP, GL_TRUE )

		glTexParameteri( target, GL_TEXTURE_MIN_FILTER, filter );
		glTexParameteri( target, GL_TEXTURE_MAG_FILTER, filter );

		glTexParameteri( target, GL_TEXTURE_WRAP_S, wrap );
		glTexParameteri( target, GL_TEXTURE_WRAP_T, wrap );

		if __debug__:
			nformat = GLint()
			glGetTexLevelParameteriv(target, 0, GL_TEXTURE_INTERNAL_FORMAT, byref(nformat))

			if nformat.value != internal_format:
				print('requested format not available, falling back to', nformat.value)

		t = cls(target, id, width, height)

		return t

	@classmethod
	def create3D(cls, width, height, depth, format=GL_RGBA, data=None):
		id = GLuint()
		target = GL_TEXTURE_3D

		glGenTextures(1, pointer(id))
		glBindTexture(target, id)

		glTexImage3D(target, 0, GL_RGBA, width, height, depth, 0, format, GL_FLOAT, data)

		glTexParameteri( target, GL_TEXTURE_MIN_FILTER, GL_LINEAR );
		glTexParameteri( target, GL_TEXTURE_MAG_FILTER, GL_LINEAR );

		glTexParameteri( target, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE );
		glTexParameteri( target, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE );
		glTexParameteri( target, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE );

		t = cls(target, id, width, height, depth)

		return t

	@classmethod
	def load(cls, file, filter=GL_LINEAR, wrap=GL_CLAMP_TO_EDGE):
		image = pyglet.resource.texture(file)

		t = cls(image.target, image.id, image.width, image.height)
		t.tex = image

		t.bind()
		glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, wrap );
		glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, wrap );

		glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, filter );
		glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, filter );
		t.unbind()

		return t
