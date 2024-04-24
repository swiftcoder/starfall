#! /usr/bin/env python -O

import cProfile as P

from src.main import run

P.run('run()', 'profile.prof')
