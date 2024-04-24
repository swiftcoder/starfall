
from pyglet.gl import *
from ctypes import *

from .texture import Texture

import os
# c support library
noise_c = CDLL(os.getcwd() + '/build/noise/Debug/noise_c.dll')

class noise_generator(Structure):
	pass

noise_destroy = noise_c.noise_generator_destroy
noise_destroy.argtypes = [POINTER(noise_generator)]
noise_destroy.restype = None

constant_create = noise_c.noise_generator_constant_create
constant_create.argtypes = [c_double]
constant_create.restype = POINTER(noise_generator)

simplex_create = noise_c.noise_generator_simplex_create
simplex_create.argtypes = []
simplex_create.restype = POINTER(noise_generator)

ridged_multifractal_create = noise_c.noise_generator_ridged_multifractal_create
ridged_multifractal_create.argtypes = [POINTER(noise_generator), POINTER(noise_generator), POINTER(noise_generator), POINTER(noise_generator), POINTER(noise_generator), POINTER(noise_generator), POINTER(noise_generator), POINTER(noise_generator)]
ridged_multifractal_create.restype = POINTER(noise_generator)

constant_value_get = noise_c.noise_generator_constant_value_get
constant_value_get.argtypes = [POINTER(noise_generator)]
constant_value_get.restype = c_double

constant_value_set = noise_c.noise_generator_constant_value_set
constant_value_set.argtypes = [POINTER(noise_generator), c_double]
constant_value_set.restype = None

class Generator(object):
	def c_generator(self):
		raise NotImplementedError()

	def glsl_code(self):
		raise NotImplementedError()
	def glsl_variables(self):
		raise NotImplementedError()

class Constant(Generator):
	def __init__(self, value):
		self._value = value
		self.c_gen = constant_create(value)

		self._name = 'constant%d' % id(self)
		self._code = '\nuniform float %s;\n' % self._name

	def __del__(self):
		noise_destroy(self.c_gen)

	def _get_value(self):
		return self._value
	def _set_value(self, value):
		self._value = value
		constant_value_set(self.c_gen, value)
	value = property(_get_value, _set_value)

	def c_generator(self):
		return self.c_gen

	def glsl_code(self):
		return (
			self._code,
			self._name
			)
	def glsl_variables(self):
		return (
			{self._name: [self._value]},
			{}
			)

def _simplex_texture():
		table = [0,64,128,192,0,64,192,128,0,0,0,0,
		  0,128,192,64,0,0,0,0,0,0,0,0,0,0,0,0,64,128,192,0,
		  0,128,64,192,0,0,0,0,0,192,64,128,0,192,128,64,
		  0,0,0,0,0,0,0,0,0,0,0,0,64,192,128,0,
		  0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
		  0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
		  64,128,0,192,0,0,0,0,64,192,0,128,0,0,0,0,
		  0,0,0,0,0,0,0,0,128,192,0,64,128,192,64,0,
		  64,0,128,192,64,0,192,128,0,0,0,0,0,0,0,0,
		  0,0,0,0,128,0,192,64,0,0,0,0,128,64,192,0,
		  0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
		  0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
		  128,0,64,192,0,0,0,0,0,0,0,0,0,0,0,0,
		  192,0,64,128,192,0,128,64,0,0,0,0,192,64,128,0,
		  128,64,0,192,0,0,0,0,0,0,0,0,0,0,0,0,
		  192,64,0,128,0,0,0,0,192,128,0,64,192,128,64,0]

		return Texture.create1D(64, GL_RGBA, GL_RGBA, GL_UNSIGNED_BYTE, (GLubyte * 256)(*table), GL_NEAREST, GL_REPEAT)
simplex_simplex = _simplex_texture()

class Simplex(Generator):
	def __init__(self):
		self.c_gen = simplex_create()

		self._name = 'simplex%d' % id(self)
		self._call = '%s(v)' % self._name

		self._textures = {self._name + '_perm': self._perm_texture(), 'simplex_simplex': simplex_simplex}

		self._code = '''
uniform sampler2D %(name)s_perm;
uniform sampler1D simplex_simplex;

/*
 * To create offsets of one texel and one half texel in the
 * texture lookup, we need to know the texture image size.
 */
const float ONE = 0.00390625;
const float ONEHALF = 0.001953125;
// The numbers above are 1/256 and 0.5/256, change accordingly
// if you change the code to use another texture size.

/*
 * 3D simplex noise. Comparable in speed to classic noise, better looking.
 */
float %(name)s(vec3 P) {

	// The skewing and unskewing factors are much simpler for the 3D case
	const float F3 = 0.333333333333;
	const float G3 = 0.166666666667;

	// Skew the (x,y,z) space to determine which cell of 6 simplices we're in
	float s = (P.x + P.y + P.z) * F3; // Factor for 3D skewing
	vec3 Pi = floor(P + s);
	float t = (Pi.x + Pi.y + Pi.z) * G3;
	vec3 P0 = Pi - t; // Unskew the cell origin back to (x,y,z) space
	Pi = Pi * ONE + ONEHALF; // Integer part, scaled and offset for texture lookup

	vec3 Pf0 = P - P0;  // The x,y distances from the cell origin

	// For the 3D case, the simplex shape is a slightly irregular tetrahedron.
	// To find out which of the six possible tetrahedra we're in, we need to
	// determine the magnitude ordering of x, y and z components of Pf0.
	// The method below is explained briefly in the C code. It uses a small
	// 1D texture as a lookup table. The table is designed to work for both
	// 3D and 4D noise, so only 8 (only 6, actually) of the 64 indices are
	// used here.
	float c1 = (Pf0.x > Pf0.y) ? 0.5078125 : 0.0078125; // 1/2 + 1/128
	float c2 = (Pf0.x > Pf0.z) ? 0.25 : 0.0;
	float c3 = (Pf0.y > Pf0.z) ? 0.125 : 0.0;
	float sindex = c1 + c2 + c3;
	vec3 offsets = texture1D(simplex_simplex, sindex).rgb;
	vec3 o1 = step(0.375, offsets);
	vec3 o2 = step(0.125, offsets);

	// Noise contribution from simplex origin
	float perm0 = texture2D(%(name)s_perm, Pi.xy).a;
	vec3  grad0 = texture2D(%(name)s_perm, vec2(perm0, Pi.z)).rgb * 4.0 - 1.0;
	float t0 = 0.6 - dot(Pf0, Pf0);
	float n0;
	if (t0 < 0.0) n0 = 0.0;
	else {
		t0 *= t0;
		n0 = t0 * t0 * dot(grad0, Pf0);
	}

	// Noise contribution from second corner
	vec3 Pf1 = Pf0 - o1 + G3;
	float perm1 = texture2D(%(name)s_perm, Pi.xy + o1.xy*ONE).a;
	vec3  grad1 = texture2D(%(name)s_perm, vec2(perm1, Pi.z + o1.z*ONE)).rgb * 4.0 - 1.0;
	float t1 = 0.6 - dot(Pf1, Pf1);
	float n1;
	if (t1 < 0.0) n1 = 0.0;
	else {
		t1 *= t1;
		n1 = t1 * t1 * dot(grad1, Pf1);
	}

	// Noise contribution from third corner
	vec3 Pf2 = Pf0 - o2 + 2.0 * G3;
	float perm2 = texture2D(%(name)s_perm, Pi.xy + o2.xy*ONE).a;
	vec3  grad2 = texture2D(%(name)s_perm, vec2(perm2, Pi.z + o2.z*ONE)).rgb * 4.0 - 1.0;
	float t2 = 0.6 - dot(Pf2, Pf2);
	float n2;
	if (t2 < 0.0) n2 = 0.0;
	else {
		t2 *= t2;
		n2 = t2 * t2 * dot(grad2, Pf2);
	}

	// Noise contribution from last corner
	vec3 Pf3 = Pf0 - vec3(1.0-3.0*G3);
	float perm3 = texture2D(%(name)s_perm, Pi.xy + vec2(ONE, ONE)).a;
	vec3  grad3 = texture2D(%(name)s_perm, vec2(perm3, Pi.z + ONE)).rgb * 4.0 - 1.0;
	float t3 = 0.6 - dot(Pf3, Pf3);
	float n3;
	if(t3 < 0.0) n3 = 0.0;
	else {
		t3 *= t3;
		n3 = t3 * t3 * dot(grad3, Pf3);
	}

	// Sum up and scale the result to cover the range [-1,1]
	return 32.0 * (n0 + n1 + n2 + n3);
}
		''' % {'name': self._name}

	def __del__(self):
		noise_destroy(self.c_gen)

	def _perm_texture(self):
		perm = [151,160,137,91,90,15,
		  131,13,201,95,96,53,194,233,7,225,140,36,103,30,69,142,8,99,37,240,21,10,23,
		  190, 6,148,247,120,234,75,0,26,197,62,94,252,219,203,117,35,11,32,57,177,33,
		  88,237,149,56,87,174,20,125,136,171,168, 68,175,74,165,71,134,139,48,27,166,
		  77,146,158,231,83,111,229,122,60,211,133,230,220,105,92,41,55,46,245,40,244,
		  102,143,54, 65,25,63,161, 1,216,80,73,209,76,132,187,208, 89,18,169,200,196,
		  135,130,116,188,159,86,164,100,109,198,173,186, 3,64,52,217,226,250,124,123,
		  5,202,38,147,118,126,255,82,85,212,207,206,59,227,47,16,58,17,182,189,28,42,
		  223,183,170,213,119,248,152, 2,44,154,163, 70,221,153,101,155,167, 43,172,9,
		  129,22,39,253, 19,98,108,110,79,113,224,232,178,185, 112,104,218,246,97,228,
		  251,34,242,193,238,210,144,12,191,179,162,241, 81,51,145,235,249,14,239,107,
		  49,192,214, 31,181,199,106,157,184, 84,204,176,115,121,50,45,127, 4,150,254,
		  138,236,205,93,222,114,67,29,24,72,243,141,128,195,78,66,215,61,156,180]

		grad = [[0,1,1],[0,1,-1],[0,-1,1],[0,-1,-1],
			   [1,0,1],[1,0,-1],[-1,0,1],[-1,0,-1],
			   [1,1,0],[1,-1,0],[-1,1,0],[-1,-1,0], # 12 cube edges
			   [1,0,-1],[-1,0,-1],[0,-1,1],[0,1,1]] # 4 more to make 16

		buffer = cast(create_string_buffer(256*256*4), POINTER(c_ubyte))

		for i in range(256):
			for j in range(256):
				offset = (i*256 + j)*4
				value = perm[(j+perm[i]) & 0xFF]
				buffer[offset+0] = grad[value % 12][0] * 64 + 64
				buffer[offset+1] = grad[value % 12][1] * 64 + 64
				buffer[offset+2] = grad[value % 12][2] * 64 + 64
				buffer[offset+3] = value

		return Texture.create2D(256, 256, GL_RGBA, GL_RGBA, GL_UNSIGNED_BYTE, buffer, GL_NEAREST, GL_REPEAT)

	def c_generator(self):
		return self.c_gen

	def glsl_code(self):
		return (
			self._code,
			self._call
			)
	def glsl_variables(self):
		return (
			{},
			self._textures,
			)

class RidgedMultifractal(Generator):
	def __init__(self, basis, octaves, lacunarity, gain, offset, h, weight, freq):
		self._nodes = [basis, octaves, lacunarity, gain, offset, h, weight, freq]

		self.c_gen = ridged_multifractal_create(basis.c_generator(), octaves.c_generator(), lacunarity.c_generator(), gain.c_generator(), offset.c_generator(), h.c_generator(), weight.c_generator(), freq.c_generator())

		self._name = 'ridged_multifractal%d' % id(self)
		self._call = '%s(v)' % self._name

	def __del__(self):
		noise_destroy(self.c_gen)

	def c_generator(self):
		return self.c_gen

	def glsl_code(self):
		glsl = [n.glsl_code() for n in self._nodes]

		code = ''

		for g in glsl:
			code += g[0]

		code = code + '''
float %(name)s(vec3 v) {
	float lacunarity = %(lacunarity)s;
	float gain = %(gain)s;
	float offset = %(offset)s;
	float h = %(h)s;
	float weight = %(weight)s;
	float freq = %(freq)s;

	float signal = 0.0;
	float value = 0.0;

	for (int i = 0; i < int(%(octaves)s); i++) {
		signal = (offset - abs( %(basis)s ));

		signal *= signal * weight;

		weight = clamp(signal*gain, 0.0, 1.0);

		value += signal * pow(freq, -h);

		freq *= lacunarity;
		v *= lacunarity;
	}

	return value - 1.0;
}
		''' % {'name': self._name, 'basis': glsl[0][1], 'octaves': glsl[1][1], 'lacunarity': glsl[2][1], 'gain': glsl[3][1], 'offset': glsl[4][1], 'h': glsl[5][1], 'weight': glsl[6][1], 'freq': glsl[7][1]}

		return (
			code,
			self._call
			)
	def glsl_variables(self):
		glsl = [n.glsl_variables() for n in self._nodes]

		uniforms = dict()
		textures = dict()

		for g in glsl:
			uniforms.update(g[0])
			textures.update(g[1])

		return (
			uniforms,
			textures
			)
