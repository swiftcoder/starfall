
from .node import BillboardNode, Node

import math

import pyglet
from pyglet.gl import *

class Sprite(BillboardNode):
	def __init__(self, sx, sy, texture, tint=[1,1,1,1], alpha=True, parent=None):
		Node.__init__(self, parent)
		
		self.texture = texture
		self.tint = tint
		self.alpha = alpha
		
		verts = [-sx,-sy, sx,-sy, sx,sy, -sx,sy]
		texcoords0 = [0,0, 1,0, 1,1, 0,1]
		
		indices = [0,1,2, 0,2,3]
		# self.vlist = pyglet.graphics.vertex_list_indexed( len(verts)/2, indices, ('v2f', verts), ('0t2f', texcoords0) )
		
		self.radius = math.sqrt(sx**2 + sy**2)
	
	def render(self, camera):		
		glLoadMatrixf((GLfloat * 16)(*camera.view * self.transform))
		
		glDepthMask(GL_FALSE)
		glEnable(GL_BLEND)
		if self.alpha:
			glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
		else:
			glBlendFunc(GL_ONE, GL_ONE)
		
		glColor4f(*self.tint)
		
		self.texture.bind()
		# self.vlist.draw(pyglet.gl.GL_TRIANGLES)
		self.texture.unbind()
		
		glDisable(GL_BLEND)
		glDepthMask(GL_TRUE)
