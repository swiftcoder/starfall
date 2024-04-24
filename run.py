#! /usr/bin/env python -O

import sys

try:
	import psyco
	psyco.background()
except ImportError:
	print('psyco not installed.')

from src.main import run

run()
