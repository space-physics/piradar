import numpy as np
from xarray import DataArray
"""
Forward modeling of ionospheric target
"""

e = 1.6021766208e-19 # electron charge, coulomb
me = 9.10938356e-31 # electron mass, kg
eps0 = 8.85418782e-12 # permittivity of free space m^-3 kg^-1 s^4 A^2

def plasmaprop(iono:DataArray,f:float,B0:float):
    Ne = iono.loc[:,'ne'].astype(float)
    w = 2*np.pi*f

    wp = np.sqrt(Ne*e**2/(eps0*me)) # electron plasma frequency [rad/sec]
    wH = B0*e/me               # electron gyrofrequency [rad/sec]


    if (w <= wp).any(): # else reflection doesn't occur, passes right through (radar freq > MUF)
        reflectionheight = iono.alt_km[abs(w-wp).argmin()]
    else:
        print(f'radar freq {f/1e6:.1f} MHz  >  max. plasma freq {wp.max()/(2*np.pi)/1e6:.1f} MHz: no reflection')
        reflectionheight = None

    return wp,wH,reflectionheight

def appleton(wp,w0,wH,theta):
    """
    Appleton-Hartree dispersion formula

    Assumptions:
    aligned with geomagnetic field B
    cold, collisionless plasma

    first order approximation: reflection occurs where w0 = wp  (radar frequency = plasma frequency)
    """
    assert np.isfinite(wp).all() # else whole calculation breaks down due to low altitude nan
    X = wp**2/w0
    Y = wH/w0

    print(f'electron gyrofreq {wH} rad/sec')
    print(wp)
    print(f'X {X}  Y {Y}')
    print(Y)
    print(X[:10])
    n2 = 1-( X / (1-Y*np.cos(theta)))
#    nr2 = 1-( X / (1 - 0.5*Y**2*np.sin(theta)**2/(1-X) + Y*np.cos(theta)))
#
#    print(n2[:10])
    n = np.sqrt(n2)
#    nr= np.sqrt(1 - X / (1 - 0.5*Y**2*np.sin(theta)**2/(1-X) - Y*np.cos(theta)))
    print(n[:10])
    R = np.zeros(n.size)
    for i in range(n.size-1):
        R[i] = (n[i]-n[i+1])**2 / (n[i] + n[i+1])**2
    print(R)

    return R