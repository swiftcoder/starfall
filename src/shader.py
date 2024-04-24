
from pyglet.gl import *
# from pyglet.gl.glxext_arb import *
# from pyglet.gl.glext_nv import *
from ctypes import *

import pyglet

from . import euclid

class Shader:
	def __init__(self, vert = [], frag = [], geom = []):
		self.Handle = glCreateProgram()
	#	print 'program: ', self.Handle
		self.Linked = False
		self.uniforms = {}

		self.createShader(vert, GL_VERTEX_SHADER)
		self.createShader(frag, GL_FRAGMENT_SHADER)
		self.createShader(geom, GL_GEOMETRY_SHADER)

		if len(geom) > 0:
			glProgramParameteri(self.Handle, GL_GEOMETRY_INPUT_TYPE, GL_TRIANGLES)
			glProgramParameteri(self.Handle, GL_GEOMETRY_OUTPUT_TYPE, GL_TRIANGLE_STRIP)
			glProgramParameteri(self.Handle, GL_GEOMETRY_VERTICES_OUT, 4)

		self.link()
		self.query_uniforms()

	def createShader(self, strings, type):
		count = len(strings)
		if count < 1:
			return

		shader = glCreateShader(type)
	#	print 'shader: ', shader

		src = (c_char_p * count)(*[s.encode() for s in strings])
		glShaderSource(shader, count, cast(pointer(src), POINTER(POINTER(c_char))), None)

		glCompileShader(shader)

		temp = c_int(0)
		glGetShaderiv(shader, GL_COMPILE_STATUS, byref(temp))
		if not temp:
			glGetShaderiv(shader, GL_INFO_LOG_LENGTH, byref(temp))
			buffer = create_string_buffer(temp.value)
			glGetShaderInfoLog(shader, temp, None, buffer)

			print(buffer.value)

		glAttachShader(self.Handle, shader);

	def link(self):
		glLinkProgram(self.Handle)

		temp = c_int(0)
		glGetProgramiv(self.Handle, GL_LINK_STATUS, byref(temp))
		if not temp:
			glGetProgramiv(self.Handle, GL_INFO_LOG_LENGTH, byref(temp))
			buffer = create_string_buffer(temp.value)
			glGetProgramInfoLog(self.Handle, temp, None, buffer)

			print(buffer.value)
		else:
			self.Linked = True

	def query_uniforms(self):
		count = GLint()
		glGetProgramiv(self.Handle, GL_ACTIVE_UNIFORMS, byref(count))

		length = GLint()
		glGetProgramiv(self.Handle, GL_ACTIVE_UNIFORM_MAX_LENGTH, byref(length))

		l = GLint()
		size = GLint()
		_type = GLenum()
		buf = create_string_buffer(length.value)

		for i in range(count.value):
			glGetActiveUniform(self.Handle, i, length, byref(l), byref(size), byref(_type), buf)
			loc = glGetUniformLocation(self.Handle, buf.value)
			self.uniforms[buf.value.decode()] = loc

		del buf

		# print(self.uniforms)

	def bind(self):
		glUseProgram(self.Handle)

	def unbind(self):
		glUseProgram(0)

	def uniform(self, name, vals):
		try:
			loc = self.uniforms[name]

			if len(vals) in range(1, 5):
				{ 1 : glUniform1f,
					2 : glUniform2f,
					3 : glUniform3f,
					4 : glUniform4f
				}[len(vals)](loc, *vals)
		except KeyError:
			if pyglet.options['debug_gl']:
				print('no such uniform: %s' % name)

	def uniform_matrix_3x3(self, name, mat):
		loc = self.uniforms[name]

		glUniformMatrix3fv(loc, 1, False, (c_float * 9)(*mat))

	def uniform_matrix_4x4(self, name, mat):
		try:
			loc = self.uniforms[name]

			glUniformMatrix4fv(loc, 1, False, (c_float * 16)(*mat))
		except KeyError:
			if pyglet.options['debug_gl']:
				print('no such uniform: %s' % name)

	def uniformi(self, name, val):
		try:
			loc = self.uniforms[name]

			glUniform1i(loc, val)
		except KeyError:
			if pyglet.options['debug_gl']:
				print('no such uniform: %s' % name)

	@classmethod
	def load(Class, name):
		import demjson

		f = pyglet.resource.file(name)
		data = demjson.decode(f.read())
		f.close()

		if (data['version'] == 1):
			p = Class([data['vertex']['source']], [data['fragment']['source']])
			return p

		return None
