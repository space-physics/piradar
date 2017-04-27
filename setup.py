#!/usr/bin/env python
req=['nose','numpy','scipy','h5py','xarray','matplotlib','seaborn',]
pipreq=['pygame']
# %%
import pip
try:
    import conda.cli
    conda.cli.main('install', *req)
except Exception:
    pip.main(['install'] + req)
pip.main(['install'] + pipreq)
# %%
from setuptools import setup

setup(name='piradar',
      packages=['piradar'],
      author='Michael Hirsch, Ph.D.',
      version='0.5.0',
      description='HF radar for ionosphere using Red Pitaya for RF and Raspberry Pi coprocessor',
	  )

