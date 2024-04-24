
from copy import copy
from .euclid import Matrix4, Point3

from pyglet.gl import *

from . import utility

class Node(object):
	def __init__(self, parent=None):
		self.model = Matrix4()
		self.transform = Matrix4()
		
		self.children = []
		self._parent = None
		
		self.parent = parent
		
		self.radius = 0.0
	
	def _set_parent(self, parent):
		if self._parent:
			self._parent.children.remove(self)
		
		self._parent = parent
		
		if self._parent:
			self._parent.children.append(self)
	
	def _get_parent(self):
		return self._parent
	
	parent = property(_get_parent, _set_parent)
	
	def update(self, camera):
		self._update_matrices(camera)
		self._update_children(camera)
		
	def _update_matrices(self, camera):
		if self.parent:
			self.transform = self.parent.transform * self.model
		else:
			self.transform = copy(self.model)
	
	def _update_children(self, camera):
		for c in self.children:
			c.update(camera)
	
	def _update_near_far(self, camera):
		loc = self.transform*Point3() - camera.transform*Point3()
		l = abs(loc)
		
		proj = utility.adjust_near_far(camera.proj, max(0.1, (l - self.radius)*0.5 - 1.0), l + self.radius + 1.0)
		
		glMatrixMode(GL_PROJECTION)
		glLoadMatrixf((GLfloat * 16)(*proj))
		glMatrixMode(GL_MODELVIEW)
	
	def draw(self, camera):
		self._update_near_far(camera)
		self.render(camera)
		
		for c in self.children:
			c.draw(camera)
	
	def render(self, camera):
		pass

class BillboardNode(Node):
	def _update_matrices(self, camera):
		Node._update_matrices(self, camera)
		
		m, v = copy(self.transform), camera.view
		m.a, m.b, m.c = v.a, v.e, v.i
		m.e, m.f, m.g = v.b, v.f, v.j
		m.i, m.j, m.k = v.c, v.g, v.k
		
		if self.parent:
			self.model = m * self.parent.transform.inverse()
