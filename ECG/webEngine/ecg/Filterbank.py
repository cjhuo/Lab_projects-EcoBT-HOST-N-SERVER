__author__ = 'leetop'
import scipy.signal
import numpy

def bandpassECG(n, fs, data) :
    Nyq = float(fs / 2)

    wn = [0.5/ Nyq, 60.0 / Nyq]
    b,a = scipy.signal.butter(n, wn, btype = 'bandpass')

    return scipy.signal.filtfilt(b, a, data)

def FilterAllChannel(nChannel, nTap, fs, wavedata) :
    print('Bandpass filtering...')

    for i in range(0,nChannel) :
        wavedata[i] = bandpassECG(nTap, fs, wavedata[i]).tolist()

    print('Completed to Bandpass filtering...')

    return wavedata
