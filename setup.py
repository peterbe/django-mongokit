# Copyright (c) 2010 FILL IN
from distutils.core import setup
#from setuptools import setup

from django-mongokitlib import meta

setup(name='django-mongokit',
      version=meta.__version__,
      author=meta.__author__,
      description='FILL IN',
      scripts=['bin/django-mongokit'],
      package_dir={'django-mongokitlib':'django-mongokitlib'},
      packages=['django-mongokitlib'],
)
