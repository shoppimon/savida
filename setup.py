"""Savida Test HTTP Server - setup script
"""

from setuptools import setup, find_packages


setup(
    name='savida',
    version=open('VERSION').read(),
    description='Savida - Testing HTTP Server Fixture',
    keywords='http server testing fixture',
    author='Shahar Evron',
    author_email='shahar@shoppimon.com',
    license='Apache 2.0',
    url='https://github.com/shoppimon/savida',
    packages=find_packages(),
    install_requires=['Werkzeug'],
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
)
