"""Savida Test HTTP Server - setup script
"""
from setuptools import setup, find_packages


with open('VERSION') as f:
    version = f.read().strip()

with open('README.md') as f:
    readme = f.read()

setup(
    name='savida',
    version=version,
    description='Savida - Testing HTTP Server Fixture',
    keywords='http server testing fixture',
    author='Shahar Evron',
    author_email='shahar@shoppimon.com',
    license='Apache 2.0',
    url='https://github.com/shoppimon/savida',
    packages=find_packages(),
    install_requires=['Werkzeug'],
    long_description=readme,
    long_description_content_type='text/markdown',
)
