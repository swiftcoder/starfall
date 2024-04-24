
from .euclid import Vector3, Matrix4
from .node import Node
from .utility import model_to_view_ortho_matrix

from math import radians

class Camera(Node):
	def __init__(self, parent=None):
		Node.__init__(self, parent)
		
		self.proj = Matrix4()
		self.view = Matrix4()
		
		self.set_perspective(radians(45), 1.0, 1.0, 100.0)
	
	def set_perspective(self, fovy, aspect, near, far):
		self.fovy = fovy
		self.aspect = aspect
		self.near = near
		self.far = far
		self.proj = Matrix4.new_perspective(fovy, aspect, near, far)
	
	def _update_matrices(self, camera):
		Node._update_matrices(self, camera)
		self.view = model_to_view_ortho_matrix(self.transform)
