
from pyglet.gl import *
from ctypes import *

class FrameBuffer:
	def __init__(self):
		self.id = GLuint()
		self.rbuf = None

		glGenFramebuffersEXT(1, byref(self.id))

	def __del__(self):
		glDeleteFramebuffersEXT(1, byref(self.id))

	def bind(self):
		glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, self.id)

	def unbind(self):
		glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, 0)

	def attach_texture(self, attachment, texture_id, mipmap_level=0):
		#glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, self.id)
		glFramebufferTexture2DEXT(GL_FRAMEBUFFER_EXT, attachment, GL_TEXTURE_2D, texture_id, mipmap_level)
		#glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, 0)

	def attach_render_buffer(self, attachment, format, width, height):
		id = GLuint()
		glGenRenderbuffersEXT(1, byref(id))
		glBindRenderbufferEXT(GL_RENDERBUFFER_EXT, id)
		glRenderbufferStorageEXT(GL_RENDERBUFFER_EXT, format, width, height)
		glBindRenderbufferEXT(GL_RENDERBUFFER_EXT, 0)

		#glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, self.id)
		glFramebufferRenderbufferEXT(GL_FRAMEBUFFER_EXT, attachment, GL_RENDERBUFFER_EXT, id)
		#glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, 0)

		self.rbuf = id

	def detach(self):
		if self.rbuf:
			glDeleteRenderbuffersEXT(1, byref(self.rbuf))
			self.rbuf = None
