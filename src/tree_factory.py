from .patch_factory import PatchFactory

import pyglet
from pyglet.gl import *
from ctypes import *
import math

from .vertex_buffer import VertexBuffer
from .texture import Texture

from .utility import lerp, cube_to_sphere
from .native_library import native_library

import os

# c support library
planet_c = CDLL(os.getcwd() + native_library('/build/planet', 'planet_c'))

query_height = planet_c.query_height
query_height.argtypes = [c_double * 3, c_double, c_double, c_void_p]
query_height.restype = c_double
#


class TreePatch(object):
    def __init__(self):
        self.vertices = None

    def delete(self):
        if self.vertices:
            self.vertices.delete()


class TreeFactory(PatchFactory):
    def __init__(self, radius, scale, grid_size, generator):
        self.radius = radius
        self.scale = scale
        self.grid_size = grid_size

        self.gen = generator

        self.tree_lod = int(math.log(10) / math.log(2))

        self.patches = {}

    def build_patch(self, tile):
        diff = self.tree_lod - tile.lod + 8
        if diff >= 0:
            verts = []
            normals = []
            texcoords = []

            for i in range(0, self.grid_size, 1 << diff):
                hi = lerp(tile.corners[0], tile.corners[3], i / float(self.grid_size))
                lo = lerp(tile.corners[1], tile.corners[2], i / float(self.grid_size))
                for j in range(0, self.grid_size, 1 << diff):
                    v = cube_to_sphere(lerp(lo, hi, i / float(self.grid_size)))

                    h = self.get_height(v)

                    if h - self.radius > 1.0 and h - self.radius < self.scale * 0.8:
                        b = v * h - tile.center
                        t = v * (h + 10.0) - tile.center

                        # print b, t

                        verts.extend([b.x, b.y, b.z])
                        verts.extend([t.x, t.y, t.z])
                        verts.extend([t.x, t.y, t.z])
                        verts.extend([b.x, b.y, b.z])
                        normals.extend(v)
                        normals.extend(v)
                        normals.extend(-v)
                        normals.extend(-v)
                        texcoords.extend([1, 0, 1, 1, 0, 1, 0, 0])

            patch = TreePatch()
            patch.vertices = pyglet.graphics.vertex_list(
                len(verts) // 3, ("v3f", verts), ("n3f", normals), ("t2f", texcoords)
            )
            self.patches[tile] = patch

    def destroy_patch(self, tile):
        patch = self.patches.get(tile)
        if patch:
            patch.delete()

            del self.patches[tile]

    def divide_patch(self, tile):
        pass

    def combine_patch(self, tile):
        pass

    def render_patches(self, walk, shader, transform, camera):
        glDisable(GL_CULL_FACE)
        glFrontFace(GL_CW)

        def render_patch(tile):
            patch = self.patches.get(tile)

            if patch and patch.vertices:
                # print 'drawing'
                shader.uniform_matrix_4x4("model_matrix", tile.model)
                glLoadMatrixf((GLfloat * 16)(*camera.view * transform * tile.model))

                patch.vertices.draw(GL_QUADS)
                # print 'drawn'

        walk(render_patch)

        glFrontFace(GL_CCW)
        glEnable(GL_CULL_FACE)

    def get_height(self, v):
        return query_height(
            (c_double * 3)(*v), self.radius, self.scale, self.gen.c_generator()
        )
