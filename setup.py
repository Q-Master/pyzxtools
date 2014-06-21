#!/usr/bin/env python

from distutils.core import setup, Command
import os

setup(name='pyZXTools',
      version='1.0',
      description='ZX-Spectrum file formats tools',
      scripts=['bin/tap.py', 'bin/trdos.py', 'bin/validate_local_iface.py'],
      packages=['pyZXTools'],
      author="Vladimir Berezenko",
      author_email="qmaster@rambler.ru",
    )
