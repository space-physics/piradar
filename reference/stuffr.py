#
# An attempt to translate the main functionality my main
# R radio signal packages gursipr and stuffr to python.
# Nothing extremely complicated, just conveniece functions
#
#
import numpy
import math
import matplotlib
import matplotlib.cbook
import matplotlib.pyplot as plt
import datetime
import time, re
import pickle
import h5py

# fit_velocity
import scipy.constants
import scipy.optimize

# xpath-like access to nested dictionaries
# @d ditct
# @q query (eg., /data/stuff)
def qd(d, q):
    keys = q.split('/')
    nd = d
    for k in keys:
        if k == '':
            continue
        if k in nd:
            nd = nd[k]
        else:
            return None
    return nd

# seed is a way of reproducing the random code without
# having to store all actual codes. the seed can then
# act as a sort of station_id.
def create_pseudo_random_code(len=10000,seed=0):
    numpy.random.seed(seed)
    phases = numpy.array(numpy.exp(1.0j*2.0*math.pi*numpy.random.random(len)),
                         dtype=numpy.complex64)
    return(phases)

def periodic_convolution_matrix(envelope,rmin=0,rmax=100):
    # we imply that the number of measurements is equal to the number of elements in code
    L = len(envelope)
    ridx = numpy.arange(rmin,rmax)
    A = numpy.zeros([L,rmax-rmin],dtype=numpy.complex64)
    for i in numpy.arange(L):
        A[i,:] = envelope[(i-ridx)%L]
    result = {}
    result['A'] = A
    result['ridx'] = ridx
    return(result)

def analyze_prc_file(fname="data-000001.gdf",clen=10000,station=0,Nranges=1000):
    z = numpy.fromfile(fname,dtype=numpy.complex64)
    code = create_pseudo_random_code(len=clen,seed=station)
    N = len(z)/clen
    res = numpy.zeros([N,Nranges],dtype=numpy.complex64)
    idx = numpy.arange(clen)
    r = create_estimation_matrix(code=code,cache=True)
    B = r['B']
    spec = numpy.zeros([N,Nranges],dtype=numpy.float32)

    for i in numpy.arange(N):
        res[i,:] = numpy.dot(B,z[idx + i*clen])
    for i in numpy.arange(Nranges):
        spec[:,i] = numpy.abs(numpy.fft.fft(res[:,i]))
    r['res'] = res
    r['spec'] = spec
    return(r)

B_cache = 0
r_cache = 0
B_cached = False
def create_estimation_matrix(code,rmin=0,rmax=1000,cache=True):
    global B_cache
    global r_cache
    global B_cached

    if cache == False or B_cached == False:
        r_cache = periodic_convolution_matrix(envelope=code,rmin=rmin,rmax=rmax)
        A = r_cache['A']
        Ah = numpy.transpose(numpy.conjugate(A))
        B_cache = numpy.dot(numpy.linalg.inv(numpy.dot(Ah,A)),Ah)
        r_cache['B'] = B_cache
        B_cached = True
        return(r_cache)
    else:
#        print("using cache")
        return(r_cache)

def grid_search1d(fun,xmin,xmax,nstep=100):
    vals = numpy.linspace(xmin,xmax,num=nstep)
    min_val=fun(vals[0])
    best_idx = 0
    for i in range(nstep):
        try_val = fun(vals[i])
        if try_val < min_val:
            min_val = try_val
            best_idx = i
    return(vals[best_idx])

def fit_velocity(z,t,var,frad=440.2e6):
    zz = numpy.exp(1.0j*numpy.angle(z))
    def ssfun(x):
        freq = 2.0*frad*x/scipy.constants.c
        model = numpy.exp(1.0j*2.0*scipy.constants.pi*freq*t)
        ss = numpy.sum((1.0/var)*numpy.abs(model-zz)**2.0)
        #        plt.plot( numpy.real(model))
        #plt.plot( numpy.real(zz), 'red')
        #plt.show()
        return(ss)
    v0 = grid_search1d(ssfun,-800.0,800.0,nstep=50)

    #    v = scipy.optimize.fmin(ssfun,numpy.array([v0]),full_output=False,disp=False,retall=False)
    return(v0)

def fit_velocity_and_power(z,t,var,frad=440.2e6):
    zz = numpy.exp(1.0j*numpy.angle(z))
    def ssfun(x):
        freq = 2.0*frad*x/scipy.constants.c
        model = numpy.exp(1.0j*2.0*scipy.constants.pi*freq*t)
        ss = numpy.sum((1.0/var)*numpy.abs(model-zz)**2.0)
        return(ss)
    v0 = grid_search1d(ssfun,-800.0,800.0,nstep=50)
    v0 = scipy.optimize.fmin(ssfun,numpy.array([v0]),full_output=False,disp=False,retall=False)
    freq = 2.0*frad*v0/scipy.constants.c
    dc = numpy.real(numpy.exp(-1.0j*2.0*scipy.constants.pi*freq*t)*z)
    p0 = (1.0/numpy.sum(1.0/var))*numpy.sum((1.0/var)*dc)

    return([v0,p0])

def dict2hdf5(d,fname):
    f = h5py.File(fname,'w')
    for k in d.keys():
        f[k] = d[k]
    f.close()

def save_object(obj, filename):
    with open(filename, 'wb') as output:
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)

def load_object(filename):
    with open(filename, 'rb') as input:
        return(pickle.load(input))

def date2unix(year,month,day,hour,minute,second):
    t = datetime.datetime(year, month, day, hour, minute, second)
    return(time.mktime(t.timetuple()))

def unix2date(x):
    return datetime.datetime.utcfromtimestamp(x)

def sec2dirname(t):
    return(unix2date(t).strftime("%Y-%m-%dT%H-00-00"))

def dirname2unix(dirn):
    r = re.search("(....)-(..)-(..)T(..)-(..)-(..)",dirn)
    return(date2unix(int(r.group(1)),int(r.group(2)),int(r.group(3)),int(r.group(4)),int(r.group(5)),int(r.group(6))))

def unix2datestr(x):
    return(unix2date(x).strftime('%Y-%m-%d %H:%M:%S'))

def compr(x,fr=0.001):
    sh = x.shape
    x = x.reshape(-1)
    xs = numpy.sort(x)
    mini = xs[int(fr*len(x))]
    maxi = xs[int((1.0-fr)*len(x))]
    mx = numpy.ones_like(x)*maxi
    mn = numpy.ones_like(x)*mini
    x = numpy.where(x < maxi, x, mx)
    x = numpy.where(x > mini, x, mn)
    x = x.reshape(sh)
    return(x)

def comprz(x):
    """ Compress signal in such a way that elements less than zero are set to zero. """
    zv = x*0.0
    return(numpy.where(x>0,x,zv))

def rep(x,n):
    """ interpolate """
    z = numpy.zeros(len(x)*n)
    for i in range(len(x)):
        for j in range(n):
            z[i*n+j]=x[i]
    return(z)

def comprz_dB(xx,fr=0.05):
    """ Compress signal in such a way that is logarithmic but also avoids negative values """
    x = numpy.copy(xx)
    sh = xx.shape
    x = x.reshape(-1)
    x = comprz(x)
    x = numpy.setdiff1d(x,numpy.array([0.0]))
    xs = numpy.sort(x)
    mini = xs[int(fr*len(x))]
    mn = numpy.ones_like(xx)*mini
    xx = numpy.where(xx > mini, xx, mn)
    xx = xx.reshape(sh)
    return(10.0*numpy.log10(xx))

def decimate(x,dec=2):
    Nout = int(math.floor(len(x)/dec))
    idx = numpy.arange(Nout,dtype=numpy.int)*int(dec)
    res = x[idx]*0.0

    for i in numpy.arange(dec):
        res = res + x[idx+i]
    return(res/float(dec))

def decimate2(x,dec=2):
    Nout = int(math.floor(len(x)/dec))
    idx = numpy.arange(Nout,dtype=numpy.int)*int(dec)
    res = x[idx]*0.0
    count = numpy.copy(x[idx])
    count[:]=1.0

    count_vector = numpy.negative(numpy.isnan(x))*1.0
    x[numpy.where(numpy.isnan(x))] = 0.0

    for i in numpy.arange(dec):
        res = res + x[idx+i]
        count += count_vector[idx+i]

    count[numpy.where(count == 0.0)] = 1.0
    return(res/count)


def median_dec(x,dec=10):
    Nout = int(math.floor(len(x)/dec))
    idx = numpy.arange(dec)
    res = numpy.zeros([Nout],dtype=x.dtype)
    for i in numpy.arange(Nout):
        res[i] = numpy.median(x[i*dec + idx])
    return(res)

def decimate_mat(M,dec0=10,dec1=10):
    shape2 = [math.floor(M.shape[0]/dec0),math.floor(M.shape[1]/dec1)]
    M2 = numpy.zeros(shape2,dtype=M.dtype)
    for i in numpy.arange(shape2[0]):
        for j in numpy.arange(dec0):
            M2[i,:] = M2[i,:] + decimate(M[dec0*i+j,:],dec=dec1)
    return(M2)

def decimate_mat_max(M,dec0=10):
    shape2 = [int(numpy.floor(M.shape[0]/dec0)),int(M.shape[1])]
    M2 = numpy.zeros(shape2,dtype=M.dtype)
    idx = numpy.arange(dec0,dtype=numpy.int)
    for i in range(shape2[0]):
        for j in range(shape2[1]):
            M2[i,j] = numpy.max(M[i*dec0 + idx,j])
    return(M2)

def plot_cts(x,plot_abs=False,plot_show=True):
    time_vec = numpy.linspace(0,len(x)-1,num=len(x))
    plt.clf()
    plt.plot(time_vec,numpy.real(x),"blue")
    plt.plot(time_vec,numpy.imag(x),"red")
    if plot_abs:
        plt.plot(time_vec,numpy.abs(x),"black")
    if plot_show:
        plt.show()

def hanning(L=1000):
    n = numpy.linspace(0.0,L-1,num=L)
    return(0.5*(1.0-numpy.cos(2.0*scipy.constants.pi*n/L)))

def spectrogram(x,window=1024,wf=hanning):
    wfv = wf(L=window)
    Nwindow = int(math.floor(len(x)/window))
    res = numpy.zeros([Nwindow,window])
    for i in range(Nwindow):
        res[i,] = numpy.abs(numpy.fft.fftshift(numpy.fft.fft(wfv*x[i*window + numpy.arange(window)])))**2
    return(res)


