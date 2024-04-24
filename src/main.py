#! /usr/bin/env python -O

import sys

import pyglet
pyglet.options['debug_gl'] = False

from pyglet.gl import *

from pyglet.window import key
from pyglet.window.mouse import LEFT, MIDDLE, RIGHT

from .euclid import Matrix4, Vector3, Point3
from math import radians
import math

from .texture import Texture

from .noise_c import RidgedMultifractal, Simplex, Constant

from .node import Node
from .camera import Camera
from .planet import Planet
from .sprite import Sprite

from . import utility

from simplui.simple import *

width, height = 1280, 720

def create_window(config=None):
	return pyglet.window.Window(width, height, caption="Planets", visible=False, resizable=True, config=config)

#try:
#	config = pyglet.gl.Config(sample_buffers=1, samples=2, depth_size=24, double_buffer=True)
#	window = create_window(config)
#except pyglet.window.NoSuchConfigException:
#	print 'format unavailable, falling back to defaults'
window = create_window()

def make_noise():
	params = {
		'octaves': Constant(16),
		'lacunarity': Constant(2.0),
		'gain': Constant(2.0),
		'offset': Constant(1.0),
		'h': Constant(0.5),
		'weight': Constant(1.0),
		'freq': Constant(1.0),
	}

	gen = RidgedMultifractal(Simplex(), **params)

	print(gen.c_generator())

	f = open('gen.txt', 'w')
	f.write(gen.glsl_code()[0])
	f.close()

	return gen, params

generator, noise_params = make_noise()

root = Node()

camera = Camera(root)
camera.model.translate(5528968.0, 2195850.0, 149997561567.0)

sun = Sprite(1391000000.0, 1391000000.0, Texture.load('data/textures/sun.tga'), [1, 1, 1, 1], True, root)

planet = Planet(6378000.0, 8000.0, 120000.0, 33, 256, sun, generator, Constant(0.0), root)
planet.model.translate(0, 0, 150000000000.0)

root.update(camera)

wireframe = '-w' in sys.argv
auto_rotate = '-r' in sys.argv

theme = Theme('themes/macos')

frame = Frame(theme, w=width, h=height)
window.push_handlers(frame)

def make_action(key):
	def _action(slider):
		frame.get_element_by_name(key).text = '%s: %.2f' % (key.capitalize(), slider.value)
		noise_params[key].value = slider.value
		planet.regenerate()

	return _action

def wireframe_action(checkbox):
	global wireframe
	wireframe = checkbox.value

def auto_rotate_action(checkbox):
	global auto_rotate
	auto_rotate = checkbox.value

def atmosphere_action(checkbox):
	planet.draw_atmosphere = checkbox.value

inspector = Dialogue(x=1000, y=600, title='Inspector', content=
	VLayout(autosizex=True, hpadding=0, children=[
		FoldingBox(title='navigation', content=
			VLayout(children=[
				Label('', name='altitude_display'),
				Label('', name='elevation_display')
			])
		),
		FoldingBox(title='stats', content=
			VLayout(children=[
				Label('', name='fps_display'),
				Label('', name='active_display'),
				Label('', name='visible_display'),
				Label('', name='vbo_display'),
				Label('', name='texture_display')
			])
		),
		FoldingBox(title='noise', collapsed=True, content=
			VLayout(children=[
				Label('Octaves: 16', name='octaves'),
				Slider(w=160, min=1, max=32, value=16, continuous=False, action=make_action('octaves')),
				Label('Lacunarity: 2.0', name='lacunarity'),
				Slider(w=160, min=0.5, max=4.0, value=2.0, continuous=False, action=make_action('lacunarity')),
				Label('Gain: 2.0', name='gain'),
				Slider(w=160, min=0.5, max=10.0, value=2.0, continuous=False, action=make_action('gain')),
				Label('Offset: 1.0', name='offset'),
				Slider(w=160, min=0.25, max=2.0, value=1.0, continuous=False, action=make_action('offset')),
				Label('H: 0.5', name='h'),
				Slider(w=160, min=0.1, max=2.0, value=0.5, continuous=False, action=make_action('h')),
				Label('Weight: 1.0', name='weight'),
				Slider(w=160, min=0.25, max=2.0, value=1.0, continuous=False, action=make_action('weight')),
				Label('Freq: 1.0', name='freq'),
				Slider(w=160, min=0.25, max=2.0, value=1.0, continuous=False, action=make_action('freq')),
			])
		),
		FoldingBox(title='settings', content=
			VLayout(children=[
				Checkbox('Show wireframe', action=wireframe_action),
				Checkbox('Show atmosphere', value=True, action=atmosphere_action),
				Checkbox('Auto-rotate', action=auto_rotate_action),
			])
		)
	])
)
frame.add(inspector)

@window.event
def on_resize(w, h):
	global width, height
	width, height = w, h
	frame.w, frame.h = w, h

	glViewport(0, 0, w, h)

	camera.set_perspective(radians(45), w/float(h), 0.01, 100000.0)

	glMatrixMode(GL_PROJECTION)
	glLoadMatrixf((GLfloat * 16)(*camera.proj))
	glMatrixMode(GL_MODELVIEW)

	return pyglet.event.EVENT_HANDLED

@window.event
def on_draw():
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

	glPolygonMode(GL_FRONT, (GL_LINE if wireframe else GL_FILL))

	root.draw(camera)

	glPolygonMode(GL_FRONT, GL_FILL)

	glMatrixMode(GL_PROJECTION)
	glPushMatrix()
	glLoadIdentity()
	glOrtho(0, width, 0, height, -1, 1)
	glMatrixMode(GL_MODELVIEW)
	glLoadIdentity()

	glDisable(GL_DEPTH_TEST)
	glEnable(GL_BLEND)
	glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

	glActiveTexture(GL_TEXTURE0)

	frame.draw()

	glDisable(GL_BLEND)
	glEnable(GL_DEPTH_TEST)

	glMatrixMode(GL_PROJECTION)
	glPopMatrix()
	glMatrixMode(GL_MODELVIEW)

alt = key.MOD_OPTION if sys.platform == 'darwin' else key.MOD_ALT

speed = 1.0

def on_mouse_drag(x, y, dx, dy, buttons, mod):
	if (buttons & RIGHT and buttons & LEFT) or (buttons & LEFT and mod & alt and mod & key.MOD_SHIFT):
		camera.model.translate(0, 0, -dy*0.5*speed)
	elif (buttons & RIGHT and buttons & MIDDLE) or (buttons & LEFT and mod & alt and mod & key.MOD_CTRL):
		camera.model.translate(dx*0.5*speed, dy*0.5*speed, 0)
	elif buttons & RIGHT or (buttons & LEFT and mod & alt):
		camera.model.rotate_euler(radians(-dx*0.25), 0, radians(dy*0.25))
	elif buttons & LEFT:
		pass

def on_key_press(k, mods):
	global wireframe, auto_rotate, refine

	if k == key.I:
		if inspector.parent:
			frame.remove(inspector)
		else:
			frame.add(inspector)
	elif k == key.W:
		wireframe = not wireframe
	elif k == key.R:
		auto_rotate = not auto_rotate
	elif k == key.A:
		planet.draw_atmosphere = not planet.draw_atmosphere
	elif k == key.P:
		camera_loc = planet.transform.inverse() * camera.transform * Point3()
		print('altitude:', abs(camera_loc) - planet.get_height(camera_loc), 'm')
		print(camera.transform * Point3())

window.push_handlers(on_mouse_drag, on_key_press)

def update(dt):
	root.update(camera)

	if auto_rotate:
		planet.model.rotatey(radians(0.01)*dt)

	camera_world = camera.transform * Point3()
	camera_loc = planet.transform.inverse() * camera.transform * Point3()
	height = planet.get_height(camera_loc) + 1.0

	if abs(camera_loc) < height:
		camera_loc2 = Point3(*camera_loc.normalized()*height)
		camera_world2 = planet.transform * camera_loc2
		diff = camera_world2 - camera_world

		#print camera_loc, camera_loc2, camera_world, camera_world2, diff

		camera.model.translate(*diff)

	global speed
	speed = (abs(camera_loc) - height + 10.0)*0.01

def update_stats(dt):
	if inspector.parent:
		camera_loc = planet.transform.inverse() * camera.transform * Point3()
		height = planet.get_height(camera_loc)

		frame.get_element_by_name('fps_display').text = '%.1f fps' % pyglet.clock.get_fps()
		frame.get_element_by_name('altitude_display').text = 'Altitude %.1f m' % (abs(camera_loc) - height)
		frame.get_element_by_name('elevation_display').text = 'Elevation %.1f m' % (height - planet.radius)
		frame.get_element_by_name('active_display').text = 'Active tiles: %d' % planet.stats.active_tiles
		frame.get_element_by_name('visible_display').text = 'Visible tiles: %d' % planet.stats.visible_tiles
		frame.get_element_by_name('vbo_display').text = 'VBO usage: %.1f MB' % (planet.stats.vbo_memory / (1024.0*1024.0))
		frame.get_element_by_name('texture_display').text = 'Texture usage: %.1f MB' % (planet.stats.texture_memory / (1024.0*1024.0))

def run():
	glEnable(GL_CULL_FACE)
	glFrontFace(GL_CCW)

	glEnable(GL_DEPTH_TEST)
	glDepthFunc(GL_LEQUAL)

	window.clear()
	window.flip()

	window.set_visible(True)

	pyglet.clock.schedule(update)
	pyglet.clock.schedule_interval(update_stats, 0.5)

	pyglet.app.run()
