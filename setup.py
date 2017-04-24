#!/usr/bin/env python
req=['nose','numpy','scipy','h5py','xarray','matplotlib','seaborn']
# %%
import pip
try:
    import conda.cli
    conda.cli.main('install',*req)
except Exception as e:
    pip.main(['install'] +req)
# %%

from setuptools import setup

setup(name='piradar',
      packages=['piradar'],
      author='Michael Hirsch, Ph.D.',
      version='0.5.0',
      description='HF radar for ionosphere using Red Pitaya for RF and Raspberry Pi coprocessor',
	  )

