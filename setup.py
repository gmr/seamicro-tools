from setuptools import setup
import sys

packages = ['seamicro_tools']
install_requires = ['paramiko']
tests_require = []

if sys.version_info < (2, 7, 0):
    install_requires.append('argparse')

console_scripts = ['seamicro-tools=seamicro_tools.controller:main']

from seamicro_tools import __version__


setup(name='seamicro_tools',
      version=__version__,
      description='Automation Tools for Interacting with the Seamicro Chassis '
                  'via SSH',
      url='https://github.com/gmr/seamicro_tools',
      packages=packages,
      author='Gavin M. Roy',
      author_email='gmr@meetme.com',
      license='BSD',
      install_requires=install_requires,
      entry_points={'console_scripts': console_scripts})
