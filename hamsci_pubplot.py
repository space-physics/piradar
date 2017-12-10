#!/usr/bin/env python
"""simple manual plot of HamSci publication count by year"""
import pandas as pd
import numpy as np
from matplotlib.pyplot import figure,show
from matplotlib.ticker import MaxNLocator
import re
import seaborn as sns
sns.set_context('talk',font_scale=1.)


fn = 'Biblio-Bibtex.bib'
pat = r'.*year.*=.*{\d{4}(?=}.*)'

years = []
with open(fn,'r') as f:
    for line in f:
        m = re.match(pat,line)
        if not m:
            continue
        years.append(int(m.string.split('}')[-2][-4:]))
# %% Publication histogram, bounded by year start/stop
ax = figure().gca()
pc = pd.Series(years)
bins = pc.unique()
bins.sort()
bins = np.append(bins,bins[-1]+1)
pc.hist(bins=bins, ax=ax)

ax.xaxis.set_major_locator(MaxNLocator(integer=True))

ax.set_title('HamSci Publications')
ax.set_xlabel('Year')
ax.set_ylabel('Publications')

show()