
from os import path
import platform


def native_library(directory, name):
    if platform.system() == 'Windows':
        return path.join(directory, 'Debug', '{name}.dll')
    elif platform.system() == 'Darwin':
        return path.join(directory, f'lib{name}.dylib')
    else:
        return path.join(directory, f'lib{name}.so')
