#!/usr/bin/env python
from setuptools import setup
import subprocess,sys,os

ok = False
try:
    import conda.cli
    conda.cli.main('install','--file','requirements.txt')
except Exception: #system Python

    with open('requirements.txt', 'r') as f:
        req = f.read().split('\n')
        aptreq = [os.path.basename(sys.executable)+'-'+r for r in req if r]

    try:
        cmd = ['sudo','apt-get','install'] + aptreq
        print(' '.join(cmd))
        subprocess.check_call(cmd)
        ok=True
    except Exception:
        pass
#%%

setup(name='piradar',
      packages=['piradar']
	  )

if not ok:
    print('You will need {}'.format(req))
