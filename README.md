# Resurrecting Starfall

Starfall was a procedural planet rendering project I worked on in the late 2000's, and was the subject of a [blog post in 2009](https://www.trist.am/blog/2009/starfall-planet-rendering/).

The project was originally stored in an SVN repo (the repo and it's history have been lost to time). I recently found a copy of the source code in DropBox, and I've endeavoured to get it running again so that I can archive it here for posterity.

_Fair warning: this codebase was not written with public distribution in mind. It has minimal comments, and jumped through some extremely weird late-2000's hoops to adapt pyglet 1.x to the task at hand._

Computer performance being what it was 15 years ago, the codebase was an unholy combination of python2 and a native C++ plugin module to handle the heavy lifting of procedure generation. I've updated the source code from python2 to python3, and modernised the CMake files, to get it running on contemporary toolchains.

![screenshot of planet rendering](screenshot.jpg?sanitize=true)

# Building
First you'll need to use CMake to configure the native plugin
```
mkdir build
cd build
cmake ..
```
And then build it with whichever toolchain you have chosen

Next you'll need to make sure there is a python3 interpreter available, with the requisite dependencies. I suggest using a virtual env
```
python -m venv .venv
./venv/bin/activate
pip install -r requirements.txt
```

# Running
At this point you can launch the software using your python interpreter
```
python run.py
```

# Control Scheme
This uses an ancient single-mouse button + keyboard control scheme that was popular for 3D software targetting MacBook users in the mid 2000's
- Alt + Left Mouse to rotate
- Alt + Shift + Left Mouse to dolly
- Alt + Ctrl + Left Mouse to pan

There is no control to roll, but the camera controller also isn't roll-stabilised, so rotating in small circles can be used to roll the camera.

# Rendering on MacOS

The terrain rendering is completely broken on Mac's implementation of OpenGL. That's not entirely surprising - this was originally written back when Apple shipped native OpenGL drivers, rather than the legacy emulation that exists today.

I don't have the interest to refactor all the rendering code for pyglet 2.0 and OpenGL 4+, so if you want to try this out, I'd advise finding a Windows computer.