import os
from setuptools import setup, find_packages

__version__= '0.0.1'

setup(
  name = 'snippet-compiler',
  packages = ['snippetcompiler'],
  version = __version__,
  description = "A command line tool for compiling snippets of code (i.e. C and C++).",
  license='MIT',
  author = 'CD Clark III',
  author_email = 'clifton.clark@gmail.com',
  url = 'https://github.com/CD3/snippet-compiler',
  download_url = f'https://github.com/CD3/snippet-compiler/archive/{__version__}.tar.gz',
  install_requires = ['click','pyparsing'],
  entry_points='''
  [console_scripts]
  snippet-compiler=snippetcompiler.cli:main
  ''',
)
