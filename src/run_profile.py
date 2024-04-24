#! /usr/bin/env python -O

import profile as P
from .main import run

P.run('run()', sort='time')
