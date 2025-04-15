from distutils.core import setup
from setuptools import find_packages

setup(name='pyflot',
      version='0.2',
      description='pyflot scripts',
      author='Hugo Brunie',
      author_email='hbrunie0@gmail.com',
      packages=find_packages(exclude=[]),
      #install_requires=['networkx'],
      entry_points = {
              'console_scripts': [
                  'pyflot= pyflot.profiling:main_profiling',
              ],
          },
)
