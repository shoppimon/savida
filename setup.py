"""Savida Test HTTP Server - setup script
"""

from setuptools import setup, find_packages


setup(
    name='savida',
    version=open('VERSION').read(),
    description='Savida Test HTTP Server',
    author='Shahar Evron',
    author_email='shahar@shoppimon.com',
    url='https://bitbucket.org/shoppimon/savida',
    packages=find_packages(),
    install_requires=['Werkzeug'],
)
