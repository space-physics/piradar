#!/usr/bin/env python
from setuptools import setup

req=['nose','numpy','scipy']

setup(name='piradar',
      packages=['piradar'],
      author='Michael Hirsch, Ph.D.',
      description='HF radar for ionosphere using Red Pitaya for RF and Raspberry Pi coprocessor',
      install_requires=req,
	  )

