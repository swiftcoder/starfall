
from typing import Optional
from .patch_factory import PatchFactory

from pyglet.gl import *
from ctypes import *
import math

from .vertex_buffer import VertexBuffer
from .texture import Texture
from .frame_buffer import FrameBuffer
from .shader import Shader

from .planet_shaders import *

import os
# c support library
planet_c = CDLL(os.getcwd() + '/build/planet/Debug/planet_c.dll')

generate_vertices = planet_c.generate_vertices
generate_vertices.argtypes = [c_double*3, c_double*3, c_double*3, c_double*3, c_double*3, c_uint, POINTER(c_float), c_double, c_double, c_void_p]
generate_vertices.restype = None

query_height = planet_c.query_height
query_height.argtypes = [c_double*3, c_double, c_double, c_void_p]
query_height.restype = c_double
#

def lerp(a, b, f):
	return a + (b - a)*f

class TerrainPatch(object):
	def __init__(self):
		self.vertex_buffer : Optional[VertexBuffer] = None
		self.normal_map : Optional[Texture] = None
		self.va : GLuint = 0

	def delete(self):
		if self.va:
			glDeleteVertexArrays(1, byref(self.va))
		if self.vertex_buffer:
			self.vertex_buffer.delete()
		if self.normal_map:
			self.normal_map.delete()

class TerrainFactory(PatchFactory):
	def __init__(self, tile_size, tex_size, height_gen, radius, scale):
		self.tile_size = tile_size
		self.tex_size = int(tex_size)

		self.gen = height_gen

		self.radius = radius
		self.scale = scale

		self.build_index_buffer()
		self.build_tex_coord_buffer()

		if self.tex_size > 0:
			self.map_size = int(tex_size + 2)
			self.build_buffer_fb = FrameBuffer()

			code = self.gen.glsl_code()
			self.build_vertices_shader = Shader([build_vertices_vs],
				[code[0], build_vertices_fs % {'noise':code[1]}])
			self.build_height_map_shader = Shader([build_height_map_vs],
				[code[0], build_height_map_fs % {'noise':code[1]}])

		self.patches = {}

	def build_index_buffer(self):
		self.indices = [[[[[], []], [[], []]], [[[], []], [[], []]]], [[[[], []], [[], []]], [[[], []], [[], []]]]]

		indices = []
		start = 0

		for e0 in [False, True]:
			for e1 in [False, True]:
				for e2 in [False, True]:
					for e3 in [False, True]:

						for i in range(1, self.tile_size-2):
							for j in range(1, self.tile_size-2):
								indices.append(j*self.tile_size + i)
								indices.append((j+1)*self.tile_size + i+1)
								indices.append(j*self.tile_size + i+1)

								indices.append(j*self.tile_size + i)
								indices.append((j+1)*self.tile_size + i)
								indices.append((j+1)*self.tile_size + i+1)

						if e0:
							for j in range(1, self.tile_size-2):
								indices.append(j*self.tile_size)
								indices.append((j+1)*self.tile_size + 1)
								indices.append(j*self.tile_size + 1)

								indices.append(j*self.tile_size)
								indices.append((j+1)*self.tile_size)
								indices.append((j+1)*self.tile_size + 1)

							indices.append(0*self.tile_size + 0)
							indices.append(1*self.tile_size + 0)
							indices.append(1*self.tile_size + 1)

							indices.append((self.tile_size-2)*self.tile_size + 0)
							indices.append((self.tile_size-1)*self.tile_size + 0)
							indices.append((self.tile_size-2)*self.tile_size + 1)
						else:
							for j in range(1, self.tile_size-1, 2):
								indices.append((j-1)*self.tile_size)
								indices.append((j+1)*self.tile_size)
								indices.append(j*self.tile_size + 1)

							for j in range(1, self.tile_size-2, 2):
								indices.append(j*self.tile_size + 1)
								indices.append((j+1)*self.tile_size)
								indices.append((j+1)*self.tile_size + 1)

								indices.append((j+1)*self.tile_size + 1)
								indices.append((j+1)*self.tile_size)
								indices.append((j+2)*self.tile_size + 1)

						if e1:
							for i in range(1, self.tile_size-2):
								indices.append((self.tile_size-2)*self.tile_size + i)
								indices.append((self.tile_size-1)*self.tile_size + i+1)
								indices.append((self.tile_size-2)*self.tile_size + i+1)

								indices.append((self.tile_size-2)*self.tile_size + i)
								indices.append((self.tile_size-1)*self.tile_size + i)
								indices.append((self.tile_size-1)*self.tile_size + i+1)

							indices.append((self.tile_size-1)*self.tile_size + 0)
							indices.append((self.tile_size-1)*self.tile_size + 1)
							indices.append((self.tile_size-2)*self.tile_size + 1)

							indices.append((self.tile_size-2)*self.tile_size + self.tile_size-2)
							indices.append((self.tile_size-1)*self.tile_size + self.tile_size-2)
							indices.append((self.tile_size-1)*self.tile_size + self.tile_size-1)
						else:
							for i in range(1, self.tile_size-1, 2):
								indices.append((self.tile_size-1)*self.tile_size + i-1)
								indices.append((self.tile_size-1)*self.tile_size + i+1)
								indices.append((self.tile_size-2)*self.tile_size + i)

							for i in range(1, self.tile_size-2, 2):
								indices.append((self.tile_size-2)*self.tile_size + i)
								indices.append((self.tile_size-1)*self.tile_size + i+1)
								indices.append((self.tile_size-2)*self.tile_size + i+1)

								indices.append((self.tile_size-2)*self.tile_size + i+1)
								indices.append((self.tile_size-1)*self.tile_size + i+1)
								indices.append((self.tile_size-2)*self.tile_size + i+2)

						if e2:
							for j in range(1, self.tile_size-2):
								indices.append(j*self.tile_size + self.tile_size-2)
								indices.append((j+1)*self.tile_size + self.tile_size-1)
								indices.append(j*self.tile_size + self.tile_size-1)

								indices.append(j*self.tile_size + self.tile_size-2)
								indices.append((j+1)*self.tile_size + self.tile_size-2)
								indices.append((j+1)*self.tile_size + self.tile_size-1)

							indices.append(0*self.tile_size + self.tile_size-1)
							indices.append(1*self.tile_size + self.tile_size-2)
							indices.append(1*self.tile_size + self.tile_size-1)

							indices.append((self.tile_size-2)*self.tile_size + self.tile_size-2)
							indices.append((self.tile_size-1)*self.tile_size + self.tile_size-1)
							indices.append((self.tile_size-2)*self.tile_size + self.tile_size-1)
						else:
							for j in range(1, self.tile_size-1, 2):
								indices.append((j-1)*self.tile_size + self.tile_size-1)
								indices.append(j*self.tile_size + self.tile_size-2)
								indices.append((j+1)*self.tile_size + self.tile_size-1)

							for j in range(1, self.tile_size-2, 2):
								indices.append(j*self.tile_size + self.tile_size-2)
								indices.append((j+1)*self.tile_size + self.tile_size-2)
								indices.append((j+1)*self.tile_size + self.tile_size-1)

								indices.append((j+1)*self.tile_size + self.tile_size-1)
								indices.append((j+1)*self.tile_size + self.tile_size-2)
								indices.append((j+2)*self.tile_size + self.tile_size-2)

						if e3:
							for i in range(1, self.tile_size-2):
								indices.append(0*self.tile_size + i)
								indices.append(1*self.tile_size + i+1)
								indices.append(0*self.tile_size + i+1)

								indices.append(0*self.tile_size + i)
								indices.append(1*self.tile_size + i)
								indices.append(1*self.tile_size + i+1)

							indices.append(0*self.tile_size + 0)
							indices.append(1*self.tile_size + 1)
							indices.append(0*self.tile_size + 1)

							indices.append(0*self.tile_size + self.tile_size-2)
							indices.append(1*self.tile_size + self.tile_size-2)
							indices.append(0*self.tile_size + self.tile_size-1)
						else:
							for i in range(1, self.tile_size-1, 2):
								indices.append(0*self.tile_size + i-1)
								indices.append(1*self.tile_size + i)
								indices.append(0*self.tile_size + i+1)

							for i in range(1, self.tile_size-2, 2):
								indices.append(1*self.tile_size + i)
								indices.append(1*self.tile_size + i+1)
								indices.append(0*self.tile_size + i+1)

								indices.append(0*self.tile_size + i+1)
								indices.append(1*self.tile_size + i+1)
								indices.append(1*self.tile_size + i+2)

						self.indices[e0][e1][e2][e3] = [start, len(indices) - start]
						start = len(indices)

		self.index_buffer = VertexBuffer(GL_ELEMENT_ARRAY_BUFFER, GL_STATIC_DRAW, len(indices)*2, (GLushort * len(indices))(*indices))

	def build_tex_coord_buffer(self):
		tex_coords = []

		for i in range(self.tile_size):
			for j in range(self.tile_size):
				tex_coords.append(i/float(self.tile_size-1))
				tex_coords.append(j/float(self.tile_size-1))

		self.tex_coord_buffer = VertexBuffer(GL_ARRAY_BUFFER, GL_STATIC_DRAW, len(tex_coords)*4, (GLfloat * len(tex_coords))(*tex_coords))

	def build_vertex_buffer(self, patch, tile):
		size = self.tile_size

		buffer = create_string_buffer((size**2)*3*4)
		vertices = cast(buffer, POINTER(c_float))

		generate_vertices((c_double*3)(*tile.center), (c_double*3)(*tile.corners[0]), (c_double*3)(*tile.corners[1]), (c_double*3)(*tile.corners[2]), (c_double*3)(*tile.corners[3]), size, vertices, self.radius, self.scale, self.gen.c_generator())

		patch.vertex_buffer = VertexBuffer(GL_ARRAY_BUFFER, GL_STATIC_DRAW, (size**2)*3*4, vertices)

	def build_normal_map(self, patch, tile):
		def drawQuad(tile):
			glBegin(GL_QUADS)
			glTexCoord3f(*tile.corners[0])
			glVertex2f(0, 1)
			glTexCoord3f(*tile.corners[1])
			glVertex2f(1, 1)
			glTexCoord3f(*tile.corners[2])
			glVertex2f(1, 0)
			glTexCoord3f(*tile.corners[3])
			glVertex2f(0, 0)
			glEnd()

		glLoadIdentity()
		glMatrixMode(GL_PROJECTION)
		glPushMatrix()
		glLoadIdentity()
		glOrtho(0, 1, 1, 0, -1, 1)

		glDisable(GL_DEPTH_TEST)

		glPushAttrib(GL_VIEWPORT_BIT | GL_POLYGON_BIT)
		glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

		self.build_buffer_fb.bind()

		# build vertex buffer
		'''patch.vertex_buffer = VertexBuffer(GL_ARRAY_BUFFER, GL_STATIC_COPY, (self.tile_size**2)*4*4)
		self.build_buffer_fb.attach_render_buffer(GL_COLOR_ATTACHMENT0_EXT, GL_RGBA32F_ARB, self.tile_size, self.tile_size)

		glViewport(0, 0, self.tile_size, self.tile_size)

		glClampColorARB(GL_CLAMP_READ_COLOR_ARB, GL_FALSE)
		glClampColorARB(GL_CLAMP_FRAGMENT_COLOR_ARB, GL_FALSE)

		glClear(GL_COLOR_BUFFER_BIT)

		self.build_vertices_shader.bind()

		glsl = self.gen.glsl_variables()

		for k, v in glsl[0].iteritems():
			self.build_vertices_shader.uniform(k, v)

		i = 0
		for k, v in glsl[1].iteritems():
			v.bind(i)
			self.build_vertices_shader.uniformi(k, i)
			i += 1

		self.build_vertices_shader.uniform('center', tile.center)
		self.build_vertices_shader.uniform('radius', [self.radius])
		self.build_vertices_shader.uniform('scale', [self.scale])

		drawQuad(tile)

		i = 0
		for k, v in glsl[1].iteritems():
			v.unbind(i)
			i += 1

		self.build_vertices_shader.unbind()

		glPushMatrix()
		glLoadIdentity()
		glOrtho(0, self.tile_size, 0, self.tile_size, -1, 1)

		glReadBuffer(GL_COLOR_ATTACHMENT0_EXT)
		patch.vertex_buffer.bind(GL_PIXEL_PACK_BUFFER_EXT)
		glReadPixels(0, 0, self.tile_size, self.tile_size, GL_RGBA, GL_FLOAT, 0)
		patch.vertex_buffer.unbind(GL_PIXEL_PACK_BUFFER_EXT)
		glReadBuffer(GL_NONE)

		glPopMatrix()

		self.build_buffer_fb.detach()'''

		# build height map
		height_map = Texture.create2D(self.map_size, self.map_size, GL_LUMINANCE, GL_LUMINANCE32F_ARB)
		self.build_buffer_fb.attach_texture(GL_COLOR_ATTACHMENT0_EXT, height_map.id)

		glViewport(0, 0, self.map_size, self.map_size)

		glClear(GL_COLOR_BUFFER_BIT)

		self.build_height_map_shader.bind()

		glsl = self.gen.glsl_variables()

		for k, v in glsl[0].items():
			self.build_height_map_shader.uniform(k, v)

		i = 0
		for k, v in glsl[1].items():
			v.bind(i)
			self.build_height_map_shader.uniformi(k, i)
			i += 1

		#offset = math.sqrt(2 * (1.0/(self.map_size+4))**2)
		offset = 1.0/(self.map_size-2)

		glBegin(GL_QUADS)
		glTexCoord3f(*lerp(tile.corners[0], tile.corners[2], -offset))
		glVertex2f(0, 0)
		glTexCoord3f(*lerp(tile.corners[3], tile.corners[1], -offset))
		glVertex2f(0, 1)
		glTexCoord3f(*lerp(tile.corners[2], tile.corners[0], -offset))
		glVertex2f(1, 1)
		glTexCoord3f(*lerp(tile.corners[1], tile.corners[3], -offset))
		glVertex2f(1, 0)
		glEnd()

		i = 0
		for k, v in glsl[1].items():
			v.unbind(i)
			i += 1

		self.build_height_map_shader.unbind()

		# build normal map
		patch.normal_map = Texture.create2D(self.tex_size, self.tex_size, GL_RGBA, GL_RGBA32F_ARB)
		self.build_buffer_fb.attach_texture(GL_COLOR_ATTACHMENT0_EXT, patch.normal_map.id)

		glViewport(0, 0, self.tex_size, self.tex_size)

		glClear(GL_COLOR_BUFFER_BIT)

		build_normal_map_shader.bind()
		build_normal_map_shader.uniform('scale', [2.0 / math.pow(2, tile.level)])
		build_normal_map_shader.uniform('pixel', [1.0/float(self.tex_size)])
		build_normal_map_shader.uniform('offset', [1.0/float(self.map_size)]*2)
		build_normal_map_shader.uniform('bias', [self.tex_size/float(self.map_size)]*2)
		build_normal_map_shader.uniformi('heightMap', 0)

		height_map.bind()

		drawQuad(tile)

		height_map.unbind()

		self.build_buffer_fb.attach_texture(GL_COLOR_ATTACHMENT0_EXT, 0)
		build_normal_map_shader.unbind()

		self.build_buffer_fb.unbind()

		glEnable(GL_DEPTH_TEST)

		glPopMatrix()
		glMatrixMode(GL_MODELVIEW)

		glPopAttrib()

	def build_patch(self, tile):
		patch = TerrainPatch()

		self.build_vertex_buffer(patch, tile)

		patch.va = GLuint()
		glGenVertexArrays(1, byref(patch.va))
		glBindVertexArray(patch.va)

		self.index_buffer.bind()

		glEnableClientState(GL_VERTEX_ARRAY)
		glEnableClientState(GL_TEXTURE_COORD_ARRAY)

		self.tex_coord_buffer.bind()
		glTexCoordPointer(2, GL_FLOAT, 0, None)
		self.tex_coord_buffer.unbind()

		patch.vertex_buffer.bind()
		glVertexPointer(3, GL_FLOAT, 0, None)
		patch.vertex_buffer.unbind()

		if self.tex_size > 0:
			self.build_normal_map(patch, tile)

		glBindVertexArray(0)

		self.patches[tile] = patch

	def destroy_patch(self, tile):
		patch = self.patches[tile]

		patch.delete()

		del self.patches[tile]

	def divide_patch(self, tile):
		self.destroy_patch(tile)

	def combine_patch(self, tile):
		self.build_patch(tile)

	def render_patches(self, walk, shader, transform, camera):

		def render_patch(tile):
			patch = self.patches.get(tile)

			if not patch:
				return

			shader.uniform_matrix_4x4('model_matrix', tile.model)
			glLoadMatrixf((GLfloat * 16)(*camera.view * transform * tile.model))

			glBindVertexArray(patch.va)

			if self.tex_size > 0:
				patch.normal_map.bind(0)

			indices = self.indices[tile.edges[0] != None][tile.edges[1] != None][tile.edges[2] != None][tile.edges[3] != None]

			glDrawElements(GL_TRIANGLES, indices[1], GL_UNSIGNED_SHORT, indices[0]*2)

			if self.tex_size > 0:
				patch.normal_map.unbind(0)

		walk(render_patch)

		glBindVertexArray(0)

		glDisableClientState(GL_TEXTURE_COORD_ARRAY)
		glDisableClientState(GL_VERTEX_ARRAY)

		self.index_buffer.unbind()
