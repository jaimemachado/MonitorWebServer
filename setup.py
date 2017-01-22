#!/usr/bin/env python
from setuptools import setup
setup(
    version='0.1',
    description='Monitor WebServer',
    url='https://github.com/jaimemachado/MonitorWebServer',
    author='Jaime Machado',
    license='MIT',
    packages=['monitorwebserver'],
    install_requires=['pynma', 'attrdict']
)