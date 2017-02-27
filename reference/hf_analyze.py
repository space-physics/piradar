#!/usr/bin/env python
# (c) Juha Vierinen
import stuffr
import matplotlib.pyplot as plt
import matplotlib
import numpy
import digital_rf_hdf5 as drf
import os
import math
import glob
from matplotlib import dates
import datetime
import time
import scipy.signal

import h5py
import traceback
from optparse import OptionParser

#
# Analyze pseudorandom code transmission for a block of data.
# idx0 = start idx
# an_len = analysis length
# clen = code length
# station = random seed for pseudorandom code
# cache = Do we cache (\conj(A^T)\*A)^{-1}\conj{A}^T for linear least squares solution (significant speedup)
#
def analyze_prc(dirn="",channel="hfrx",idx0=0,an_len=1000000,clen=10000,station=0,Nranges=1000,cache=True):
    g = []
    if type(dirn) is str:
        g = drf.read_hdf5(dirn)
    else:
        g = dirn

    code = stuffr.create_pseudo_random_code(len=clen,seed=station)
    N = an_len/clen
    res = numpy.zeros([N,Nranges],dtype=numpy.complex64)
    r = stuffr.create_estimation_matrix(code=code,cache=cache,rmax=Nranges)
    B = r['B']
    spec = numpy.zeros([N,Nranges],dtype=numpy.complex64)
    
    zspec = numpy.zeros(clen,dtype=numpy.float64)

    for i in numpy.arange(N):
        z = g.read_vector_c81d(idx0+i*clen,clen,channel)
        z = z-numpy.median(z) # remove dc
        res[i,:] = numpy.dot(B,z)
    for i in numpy.arange(Nranges):
        spec[:,i] = numpy.fft.fftshift(numpy.fft.fft(scipy.signal.blackmanharris(N)*res[:,i]))

    ret = {}
    ret['res'] = res
    ret['spec'] = spec
    return(ret)

if __name__ == '__main__':
    parser = OptionParser(usage="%prog: [options]")

    parser.add_option("-d", "--dir",
                      dest="datadir",
                      type="string",
                      action="store",
                      default="/data0",
                      help="Data directory to analyze (default /data0).")

    parser.add_option("-b", "--channel",
                      dest="channel",
                      type="string",
                      action="store",
                      default="ch000",
                      help="Channel name (default %default).")

    parser.add_option("-x", "--delete_old",
                      dest="delete_old",
                      action="store_true",
                      default=False,
                      help="Delete processed files.")
    parser.add_option("-a", "--analysis_length",
                      dest="anlen",
                      action="store",
                      default=6000000,
                      type="int",
                      help="An length (%default)")
    parser.add_option("-c", "--code_length",
                      dest="codelen",
                      action="store",
                      default=10000,
                      type="int",
                      help="Code length (%default)")

    matplotlib.use('Agg')

    (op, args) = parser.parse_args()
    os.system("mkdir -p %s/hfradar"%(op.datadir))
    
    d = drf.read_hdf5(op.datadir)
    sr = 100e3#d.get_metadata("hfrx")["sample_rate"].value
    b = d.get_bounds(op.channel)
    print(b)
    idx = numpy.array(b[0])
    if os.path.isfile("%s/hfradar/last.dat"%(op.datadir)):
        idx = numpy.fromfile("%s/hfradar/last.dat"%(op.datadir),dtype=numpy.int)
    while True:
        d = drf.read_hdf5(op.datadir)
        b = d.get_bounds(op.channel)
        if b[0] > idx:
            idx = numpy.array(b[0])

        while idx+op.anlen > b[1]:
            d = drf.read_hdf5(op.datadir)
            b = d.get_bounds(op.channel)
            print("not enough data yet, sleeping.")
            time.sleep(op.anlen/sr)
        
        try:
            res = None
            res = analyze_prc(d,idx0=idx,an_len=op.anlen, clen=op.codelen, cache=True)
            plt.clf()
    
            M = 10.0*numpy.log10((numpy.abs(res["spec"])))
            plt.pcolormesh(numpy.transpose(M),vmin=(numpy.median(M)-1.0))

            plt.colorbar()
            plt.title(stuffr.unix2datestr(idx/sr))
            plt.savefig("%s/hfradar/spec-%06d.png"%(op.datadir,idx/sr))
            print("%d"%(idx))
        except Exception:
            print("no data, skipping.")
        idx = idx + op.anlen
        idx.tofile("%s/hfradar/last.dat"%(op.datadir))

        if idx > b[1]:
            print "Done processing. Sleeping 60 seconds"
            time.sleep(op.anlen/sr)
