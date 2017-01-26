#!/usr/bin/env python
from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    version='0.1',
    description='Monitor WebServer',
    url='https://github.com/jaimemachado/MonitorWebServer',
    author='Jaime Machado',
    license='MIT',
    packages=['monitorwebserver'],
    install_requires=requirements
)