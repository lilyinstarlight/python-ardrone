#!/usr/bin/env python
import os.path

from setuptools import setup, find_packages, Extension


with open(os.path.join(os.path.dirname(__file__), 'README.md'), 'r') as rfile:
    readme = rfile.read()


video = Extension(
    name='ardrone.video',
    libraries=['avcodec', 'avformat', 'avutil', 'swscale'],
    sources=['ardrone/video.c'],
)

setup(
    name='ardrone',
    version='0.3.0',
    description='A Python library for controlling the Parrot AR.Drone 2.0 over a network',
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://github.com/lilyinstarlight/python-ardrone',
    project_urls={
        'Source': 'https://github.com/lilyinstarlight/python-ardrone',
        'Tracker': 'https://github.com/lilyinstarlight/python-ardrone/issues',
    },
    license='MIT',
    author='Lily Foster',
    author_email='lily@lily.flowers',
    install_requires=['Pillow'],
    packages=find_packages(),
    ext_modules=[video],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Programming Language :: C',
        'Topic :: Scientific/Engineering',
        'Topic :: System :: Hardware :: Hardware Drivers',
    ],
)
