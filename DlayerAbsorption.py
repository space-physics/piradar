#!/usr/bin/env python
"""
These results have not been validated.
"""
from dateutil.parser import parse
import numpy as np
from matplotlib.pyplot import show
import seaborn as sns
#
from piradar.plots import plotgas,plotloss
#
# https://github.com/scivision/pyiri90
from pyiri90 import runiri
#from pyiri90.plots import plotiono
# https://github.com/scivision/msise00
from msise00 import rungtd1d
#from msise00.plots import plotgtd
from igrf12py import runigrf12
#
theta = 0.01 # radians off parallel from B
#
kb_evK = 8.6173303e-5 # [eV K^-1]
q_e = 1.60217662e-19 # [C]
m_e = 9.10938356e-31 #[kg]

Fr = np.arange(1e6,10e6,0.05e6) # [Hz] radar frequency sweep

if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('--alt',help='START STOP STEP altitude [km]',type=float,nargs=3,default=(50,150,1.))
    p.add_argument('-t','--time',help='datetime of simulation',default='2012-07-21T12')
    p.add_argument('-c','--latlon',help='geodetic coordinates of simulation',default=(65,-147.5),type=float)
    p.add_argument('--f107',type=float,default=200.)
    p.add_argument('--f107a',type=float,default=200.)
    p.add_argument('--ap',type=int,default=4)
    p = p.parse_args()

    altkm = np.arange(p.alt[0], p.alt[1], p.alt[2])
    dtime = parse(p.time)
#%% IRI
    iono = runiri(dtime,altkm,p.latlon,p.f107, p.f107a, ap=p.ap)
#%% MSIS
    dens,temp = rungtd1d(dtime, altkm, p.latlon[0], p.latlon[1], p.f107a, p.f107, p.ap)
#%% IGRF
    Bx,By,Bz,B0 = runigrf12(dtime,isv=0,itype=1,
                        alt=altkm, glat=p.latlon[0], glon=p.latlon[1])[:4]
    B0 = B0/1e9 #[T]
#%% compute electron-neutral collison frequency
    """
    Thrane & Piggot, The collision frequency in the E- and D-regions of the ionosphere, 1966, JATP.
    vm essentially matches Fig. 1 of this paper.
    This paper argues that Tn~Te in the D and E region ionosphere.
    """
    T = iono.loc[:,'Te']
    T[np.isnan(T)] = temp.loc[:,'Tn']
    E = 3/2*kb_evK*T # [eV]

    # [Hz] monoenergetic electron-neutral collision freq
    vm = 2.5* (1.11e-7*dens.loc[:,'N2']/1e6 + 7.10e-8*dens.loc[:,'O2']/1e6) * E
#%%  compute D region absorption
    """
    A STUDY OF THE RELATION BETWEEN IONOSPHERIC ABSORPTION AND PREDICTED HF PROPAGATION PARAMETERS AT HIGH LATITUDES
    Jodalen and Thrane
    """
    phi = 0 # [radians] incidence angle (from local zenith)

    Ne = iono.loc[:,'ne']

    fH = q_e * B0/(2*np.pi* m_e)

    Li = np.empty(Fr.size)
    for i,f in enumerate(Fr):
        Li[i] = 2*4.6e-2 * 1/np.cos(phi) * np.trapz((Ne*vm)/(4*np.pi**2*(f+fH)**2 + vm**2),iono.alt_km)
#%% plots
    #z0 = 85.
    #print(iono.loc[z0,:])
    #print(dens.loc[z0,['N2','O2']])
    #print(temp.loc[z0,'Tn'])

    #plotgtd(dens,temp,dtime,altkm,p.ap,p.f107,p.latlon[0], p.latlon[1])

    plotgas(iono,dens,temp,vm,dtime,p.latlon,p.ap,p.f107)

    plotloss(Li,Fr,dtime)

    show()