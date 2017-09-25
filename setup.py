#!/usr/bin/env python
from setuptools import setup, Extension

video = Extension(
	name='ardrone.video',
	libraries=['avcodec', 'avformat', 'avutil', 'swscale'],
	sources=['ardrone/video.c'],
)

setup(
	name='ardrone',
	version='0.2.1',
	description='A Python library for controlling the Parrot AR.Drone 2.0 over a network',
	url='https://github.com/fkmclane/python-ardrone',
	license='MIT',
	author='Foster McLane',
	author_email='fkmclane@gmail.com',
	packages=['ardrone'],
	ext_modules=[video],
)
