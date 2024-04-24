
import ctypes
from pyglet.gl import *
from ctypes import *

from .euclid import Vector3, Point3, Matrix4
import math

from .node import Node

from .vertex_buffer import VertexBuffer
from .texture import Texture
from .frame_buffer import FrameBuffer
from .shader import Shader

from .sphere import Sphere

import time, operator

from . import utility

from .planet_shaders import *

from .lod_sphere import LODSphere
from .terrain_factory import TerrainFactory
from .tree_factory import TreeFactory

import os
# c support library
planet_c = CDLL(os.getcwd() + '/build/planet/Debug/planet_c.dll')

query_height = planet_c.query_height
query_height.argtypes = [c_double*3, c_double, c_double, c_void_p]
query_height.restype = c_double
#

class Stats:
	def __init__(self):
		self.active_tiles = 0
		self.visible_tiles = 0
		self.vbo_memory = 0
		self.texture_memory = 0

class Planet(Node):
	def __init__(self, radius, scale, atmosphereHeight, tileSize, texSize, sun, terrain_generator, water_generator, parent=None):
		Node.__init__(self, parent)

		self.radius = radius
		self.scale = scale
		self.atmosphereHeight = atmosphereHeight

		self.sun = sun
		self.gen = terrain_generator

		self.terrain = LODSphere(radius, scale, terrain_generator)

		self.terrain_factory = TerrainFactory(tileSize, texSize, terrain_generator, radius, scale)
		self.terrain.add_factory(self.terrain_factory)
		self.tree_factory = TreeFactory(radius, scale, tileSize, terrain_generator)
		self.terrain.add_factory(self.tree_factory)

		self.water = LODSphere(radius, 10.0, water_generator)
		self.water_factory = TerrainFactory(tileSize, texSize/4, water_generator, radius, scale)
		self.water.add_factory(self.water_factory)

		self.lut = Texture.load('data/textures/lut-terrain.png')
		self.detail = Texture.load('data/textures/detail.jpg', GL_LINEAR, GL_REPEAT)
		self.spruce = Texture.load('data/textures/trees/spruce.png', GL_LINEAR, GL_REPEAT)

		self.atmosphere = Sphere(self.radius + self.atmosphereHeight, 256)

		self.draw_atmosphere = True

		self.stats = Stats()

	def regenerate(self):
		self.terrain.regenerate()
		self.water.regenerate()

	def _update_near_far(self, camera):
		loc = self.transform.inverse() * camera.transform * Point3()
		l = abs(loc)

		dist_atmos = abs(l - self.radius - self.atmosphereHeight)
		dist_ground = l - self.get_height(loc)

		near = max(0.1, min(dist_atmos, dist_ground)*0.75 - 1.0)
		if l > self.radius + self.atmosphereHeight:
			far = l + self.radius*0.5
		else:
			far = l - self.radius*0.5

		proj = utility.adjust_near_far(camera.proj, near, far)

		glMatrixMode(GL_PROJECTION)
		glLoadMatrixf((GLfloat * 16)(*proj))
		glMatrixMode(GL_MODELVIEW)

	def render(self, camera):
		sunPos = self.transform.inverse() * self.sun.transform * Point3()
		sunDir = sunPos.normalized()

		cam_pos = self.transform.inverse() * camera.transform * Point3()
		cam_dir = self.transform.inverse() * camera.transform * Vector3( 0, 0,-1)
		cam_height = abs(cam_pos)

		if cam_height - self.radius > self.atmosphereHeight:
			terrain_shader = terrain_shader_space
			water_shader = water_shader_space
			atmos_shader = atmos_shader_space
		else:
			terrain_shader = terrain_shader_atmos
			water_shader = water_shader_atmos
			atmos_shader = atmos_shader_atmos

		self.terrain.recalculate_visibility(self.transform, camera)
		self.water.recalculate_visibility(self.transform, camera)

		# draw planet
		for shader, sphere, factory in [(terrain_shader, self.terrain, self.terrain_factory), (water_shader, self.water, self.water_factory)]:
			shader.bind()
			shader.uniformi('lut', 1)
			shader.uniformi('normalMap', 0)
			shader.uniformi('detail', 2)
			shader.uniform('sun', sunDir)

			shader.uniform('exposure', [2.0])

			shader.uniform('waterRadius', [self.radius])
			shader.uniform('atmosphereRadius', [self.radius + self.atmosphereHeight])
			shader.uniform('atmosphereScale', [1.0/self.atmosphereHeight])
			shader.uniform('invWavelength', [1.0/math.pow(0.650, 4), 1.0/math.pow(0.570, 4), 1.0/math.pow(0.475, 4)])

			shader.uniform('viewer', cam_pos)
			shader.uniform('cameraHeight', [cam_height])

			self.lut.bind(1)
			self.detail.bind(2)

			factory.render_patches(sphere.walk_visible_active, shader, self.transform, camera)

			#STATS
			self.detail.unbind(2)
			self.lut.unbind(1)

			shader.unbind()

		tree_shader.bind()
		tree_shader.uniform('viewer', cam_pos)
		tree_shader.uniformi('tree', 0)
		self.spruce.bind(0)

		glEnable(GL_ALPHA_TEST)
		glAlphaFunc(GL_GEQUAL, 0.5)

		#self.tree_factory.render_patches(self.terrain.walk_visible, tree_shader, self.transform, camera)

		glDisable(GL_ALPHA_TEST)

		self.spruce.unbind(0)
		tree_shader.unbind()

		# draw atmosphere
		if self.draw_atmosphere:
			atmos_shader.bind()
			atmos_shader.uniform('sun', sunDir)

			atmos_shader.uniform('exposure', [2.0])

			atmos_shader.uniform('waterRadius', [self.radius])
			atmos_shader.uniform('atmosphereRadius', [self.radius + self.atmosphereHeight])
			atmos_shader.uniform('atmosphereScale', [1.0/self.atmosphereHeight])
			atmos_shader.uniform('invWavelength', [1.0/math.pow(0.650, 4), 1.0/math.pow(0.570, 4), 1.0/math.pow(0.475, 4)])

			atmos_shader.uniform('viewer', cam_pos)
			atmos_shader.uniform('cameraHeight', [cam_height])

			glLoadMatrixf((GLfloat * 16)(*camera.view * self.transform))

			glEnable(GL_BLEND)
			glBlendFunc(GL_ONE, GL_ONE)
			glFrontFace(GL_CW)

			self.atmosphere.draw()

			glFrontFace(GL_CCW)
			glDisable(GL_BLEND)

			atmos_shader.unbind()

	def update(self, camera):
		Node.update(self, camera)

		self.terrain.update(self.transform, camera)
		self.water.update(self.transform, camera)

	def get_height(self, v):
		return query_height((c_double*3)(*v), self.radius, self.scale, self.gen.c_generator())
