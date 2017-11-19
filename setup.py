#!/usr/bin/env python
req=['nose','numpy','scipy','h5py','xarray']
# %%
from setuptools import setup

setup(name='piradar',
      packages=['piradar'],
      author='Michael Hirsch, Ph.D.',
      version='0.5.0',
      description='HF radar for ionosphere using Red Pitaya for RF and Raspberry Pi coprocessor',
      classifiers=[
      'Intended Audience :: Science/Research',
      'Development Status :: 4 - Beta',
      'License :: OSI Approved :: MIT License',
      'Topic :: Scientific/Engineering :: Atmospheric Science',
      'Programming Language :: Python :: 3',
      ],
      install_requires=req,
      extras_requires={'plot':['matplotlib','seaborn',],
                       'io':['radioutils'],},
      python_requires='>=3.6',
	  )

