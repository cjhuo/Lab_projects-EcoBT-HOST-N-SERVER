__author__ = 'leetop'

import dicom
import struct
import scipy
import numpy
import ECG

#from pylab import *

def main() :
    ds = dicom.read_file("Uploads/39DA47B7.dcm")
    format="<"+str(28800)+"h"
    
    print len(ds.WaveformSequence[0].WaveformData)
    
    wavedata = list(struct.unpack(format,ds.WaveformSequence[0].WaveformData))

    wavech = [
                [
                    elem for index, elem in enumerate( wavedata ) if index % 12 == channel_number
                ] for channel_number in range( 12 )
            ]
    #print wavech
    info = dict()

    ecg = ECG.Ecg(wavech,info)
    filtered = ecg.bpfilter(numpy.array(wavech[0]).transpose())
    diffdata = scipy.diff(filtered)
    sqdata = abs(diffdata)
    print len(sqdata)
    int_data = ecg.mw_integrate(sqdata)
    print int_data
    '''
    figure()
    subplot(611)
    plot(ecg.data[:,0])
    subplot(612)
#    plot(wavech[1])
    plot(filtered)
    subplot(613)
#    plot(wavech[2])
    plot(diffdata)
    subplot(614)
#    plot(wavech[3])
    plot(sqdata)
    subplot(615)
#    plot(wavech[4])
    plot(int_data)
    subplot(616)
    plot(wavech[5])
    show()
    '''

if __name__ == "__main__":
    main()
