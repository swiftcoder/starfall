
import ctypes
from pyglet.gl import *
from ctypes import *

from .euclid import Vector3, Point3, Matrix4
import math

import time, operator

from . import utility
from .utility import lerp, cube_to_sphere

from .planet_shaders import *

import os
# c support library
planet_c = CDLL(os.getcwd() + '/build/planet/Debug/planet_c.dll')

query_height = planet_c.query_height
query_height.argtypes = [c_double*3, c_double, c_double, c_void_p]
query_height.restype = c_double
#

class Tile:
	def __init__(self, v1, v2, v3, v4, planet, parent=None):
		self.parent = parent
		self.corners = [v1, v2, v3, v4]

		self.level = (1 if parent == None else parent.level + 1)

		self.center = cube_to_sphere(lerp(v1, v3, 0.5))
		self.center *= planet.get_height(self.center)

		arc_length =  math.pi*planet.radius / math.pow(2.0, self.level+1)
		self.radius = math.sqrt(2 * arc_length**2)

		self.lod = int(math.log(arc_length*2) / math.log(2))

		self.model = Matrix4.new_translate(*self.center)

		self.children = [None]*4
		self.edges = [None]*4

		self.visible = False

	def is_parent(self):
		return self.children[0] != None

	def is_grandparent(self):
		if not self.is_parent():
			return False
		for t in self.children:
			if t.is_parent():
				return True
		return False

class LODSphere(object):
	def __init__(self, radius, scale, generator):
		self.radius = radius
		self.scale = scale

		self.max_lod = math.log(math.pi*self.radius/2) / math.log(2)

		self.gen = generator

		self.parent_list = []
		self.render_list = []

		v = [
			Vector3(-1, 1, 1), Vector3(-1,-1, 1), Vector3( 1,-1, 1), Vector3( 1, 1, 1),
			Vector3( 1, 1,-1), Vector3( 1,-1,-1), Vector3(-1,-1,-1), Vector3(-1, 1,-1)
			]

		self.root = [
			Tile(v[3], v[2], v[5], v[4], self), # right
			Tile(v[7], v[6], v[1], v[0], self), # left

			Tile(v[7], v[0], v[3], v[4], self), # top
			Tile(v[1], v[6], v[5], v[2], self), # bottom

			Tile(v[0], v[1], v[2], v[3], self), # front
			Tile(v[4], v[5], v[6], v[7], self) # back
		]

		for t in self.root:
			for i in range(4):
				for s in [r for r in self.root if r != t]:
					j = (i + 1) % 4
					for k in range(4):
						l = (k + 1) % 4

						if (s.corners[k] == t.corners[i] and s.corners[l] == t.corners[j]) or (s.corners[k] == t.corners[j] and s.corners[l] == t.corners[i]):
							t.edges[i] = s

		for t in self.root:
			self.render_list.append(t)

		self.factories = []

	def regenerate(self):
		for t in self.render_list:
			for f in self.factories:
				f.destroy_patch(t)
				f.build_patch(t)

	def add_factory(self, factory):
		self.factories.append(factory)

		for t in self.render_list:
			factory.build_patch(t)

	def remove_factory(self, factory):
		self.factories.remove(factory)

		for t in self.render_list:
			factory.destroy_patch(t)

	def arc_length(self, tile):
		return math.pi*self.radius / math.pow(2.0, tile.level)

	def check_horizon_visibility(self, pos, t):
		v1 = Vector3() - pos
		v2 = t.center - pos

		D1 = abs(v1)
		D2 = abs(v2)
		R1 = self.radius
		R2 = t.radius
		iD1 = 1.0 / D1
		iD2 = 1.0 / D2

		v1 *= iD1
		v2 *= iD2

		K = v1.dot(v2)
		K1 = R1 * iD2
		K2 = R2 * iD2

		status = True
		if K > K1 * K2:
			status = (-2.0 * K * K1*K2 + K1*K1 + K2*K2) < (1.0 - K*K)

		y = R1 * R1 * iD1
		P = Vector3() - y*v1
		N = -v1
		d = -N.dot(P)

		return status or (N.dot(t.center) + d > t.radius)

	def check_cone_visibility(self, camera, pos, view, t):
		depth = 1.0 / math.tan(camera.fovy*0.5)
		corner = math.sqrt((1.0*camera.aspect)**2 + 1.0**2)
		fov = math.atan(corner/depth)

		radius = self.arc_length(t)*0.75

		Kcos = math.cos(fov)
		Ksin = math.sin(fov)

		U = pos - (t.radius/Ksin)*view
		D = t.center - U

		Dsqr = D.dot(D)

		e = view.dot(D)
		if e > 0 and e*e >= Dsqr*Kcos*Kcos:
			D = t.center - pos
			Dsqr = D.dot(D)
			if -e > 0 and e*e >= Dsqr*Ksin*Ksin:
				return Dsqr <= t.radius*t.radius
			else:
				return True
		else:
			return False

	def recalculate_visibility(self, transform, camera):
		cam_pos = transform.inverse() * camera.transform * Point3()
		cam_dir = transform.inverse() * camera.transform * Vector3( 0, 0,-1)

		def recalculate_tile_visibility(tile, override=True):
			tile.visible = override and self.check_cone_visibility(camera, cam_pos, cam_dir, tile)

			for c in tile.children:
				if c != None:
					recalculate_tile_visibility(c, tile.visible)

		for t in self.root:
			recalculate_tile_visibility(t)

	def walk_visible(self, callback):
		def walk_tile(tile):
			callback(tile)

			for c in tile.children:
				if c != None and c.visible:
					walk_tile(c)

		for t in self.root:
			if t.visible:
				walk_tile(t)

	def walk_visible_active(self, callback):
		for t in self.render_list:
			if t.visible:
				callback(t)

	def get_visible_list(self, transform, camera):
		cam_pos = transform.inverse() * camera.transform * Point3()
		cam_dir = transform.inverse() * camera.transform * Vector3( 0, 0,-1)

		visible = []
		for t in self.render_list:
			if self.check_cone_visibility(camera, cam_pos, cam_dir, t):
				visible.append(t)

		return visible

	def update(self, transform, camera):
		viewer = transform.inverse() * (camera.transform * Point3())
		fovy = camera.fovy

		current = [t for t in self.render_list]
		parents = [t for t in self.parent_list]

		divides = []
		for t in current:
			size = 2.0*abs(t.center - viewer)*math.tan(0.5*fovy)
			factor = size/self.arc_length(t)

			if factor < 1.0 and t.level < self.max_lod:
				divides.append((factor, t))

		for f, t in sorted(divides)[:1]:
			self.subdivide(t)

		combines = []
		for t in parents:
			size = 2.0*abs(t.center - viewer)*math.tan(0.5*fovy)
			factor = size/self.arc_length(t)

			if factor > 1.0:
				combines.append((factor, t))

		for f, t in sorted(combines)[:4]:
			self.combine(t)

	def subdivide(self, tile):
		if tile.is_parent():
			return

		v = [
			tile.corners[0], lerp(tile.corners[0], tile.corners[3], 0.5), tile.corners[3],
			lerp(tile.corners[0], tile.corners[1], 0.5),
				lerp(tile.corners[0], tile.corners[2], 0.5),
					lerp(tile.corners[2], tile.corners[3], 0.5),
			tile.corners[1], lerp(tile.corners[1], tile.corners[2], 0.5), tile.corners[2]
			]

		tile.children[0] = Tile(v[0], v[3], v[4], v[1], self, tile)
		tile.children[1] = Tile(v[3], v[6], v[7], v[4], self, tile)
		tile.children[2] = Tile(v[4], v[7], v[8], v[5], self, tile)
		tile.children[3] = Tile(v[1], v[4], v[5], v[2], self, tile)

		for t, i in zip(tile.children, list(range(4))):
			j = (i + 1) % 4
			k = (i + 2) % 4
			l = (i + 3) % 4

			t.edges[j] = tile.children[j]
			t.edges[k] = tile.children[l]

			if tile.edges[i] != None and tile.edges[i].is_parent():
				for s in tile.edges[i].children:
					for o in range(4):
						p = (o + 1) % 4
						if (s.corners[o] == t.corners[i] and s.corners[p] == t.corners[j]):
							t.edges[i] = s
							s.edges[p] = t
						elif (s.corners[o] == t.corners[j] and s.corners[p] == t.corners[i]):
							t.edges[i] = s
							s.edges[o] = t

			if tile.edges[l] != None and tile.edges[l].is_parent():
				for s in tile.edges[l].children:
					for o in range(4):
						p = (o + 1) % 4
						if (s.corners[o] == t.corners[l] and s.corners[p] == t.corners[i]):
							t.edges[l] = s
							s.edges[p] = t
						elif (s.corners[o] == t.corners[i] and s.corners[p] == t.corners[l]):
							t.edges[l] = s
							s.edges[o] = t

			for f in self.factories:
				f.build_patch(t)

			self.render_list.append(t)

		self.render_list.remove(tile)
		self.parent_list.append(tile)

		if tile.parent != None and tile.parent in self.parent_list:
			self.parent_list.remove(tile.parent)

		for f in self.factories:
			f.divide_patch(tile)

		#STATS
		#self.stats.active_tiles = len(self.render_list)
		#self.stats.vbo_memory = len(self.render_list) * (self.terrain.tile_size)**2 * 3*4
		#self.stats.texture_memory = len(self.render_list) * (self.terrain.tex_size**2) * 4

	def combine(self, tile):
		if not tile.is_parent() or tile.is_grandparent():
			return

		for f in self.factories:
			f.combine_patch(tile)

		if tile.parent != None and not tile.parent in self.parent_list:
			self.parent_list.append(tile.parent)

		self.parent_list.remove(tile)
		self.render_list.append(tile)

		for t in tile.children:
			for i in range(4):
				if t.edges[i] != None and t in t.edges[i].edges:
					s = t.edges[i].edges.index(t)
					t.edges[i].edges[s] = None

			for f in self.factories:
				f.destroy_patch(t)

			self.render_list.remove(t)

		tile.children = [None]*4

		#STATS
		#self.stats.active_tiles = len(self.render_list)
		#self.stats.vbo_memory = len(self.render_list) * (self.terrain.tile_size)**2 * 3*4
		#self.stats.texture_memory = len(self.render_list) * (self.terrain.tex_size**2) * 4

	def get_height(self, v):
		return query_height((c_double*3)(*v), self.radius, self.scale, self.gen.c_generator())
