#!/usr/bin/env python3
from distutils.core import setup, Extension

video = Extension(
	name='ardrone.video',
	libraries=['avcodec', 'avformat', 'avutil', 'swscale'],
	sources=['ardrone/video.c'],
)

setup(
	name='ardrone',
	version='0.1',
	description='A Python library for controlling the Parrot AR.Drone 2.0 over a network',
	license='MIT',
	author='Foster McLane',
	author_email='fkmclane@gmail.com',
	packages=['ardrone'],
	ext_modules=[video],
)
