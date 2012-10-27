__authors__ = 'leetop, cj'

import dicom
import struct
import ECG
import CAPS
import Qtc
import Histogram

#from pylab import *
wavech = None #declare a global wavech variable
peakdata = None #declare a global wavech variable


def getBinInfo(qPoint, tPoint):
    aa = CAPS.caps(wavech[0], 120, peakdata)
    # result1 is the list of similar points of manually selected Q point
    result1 = aa.SearchingSimilarPoint()

    # Searching similar point from manually selected T point
    aa = CAPS.caps(wavech[0], 160, peakdata)
    # result2 is the list of similar points of manually selected T point
    result2 = aa.SearchingSimilarPoint()

    # Calculate the Qtc value, 200 is sampling rate
    result3 = Qtc.CalculateQtc(peakdata, result1, result2, 200)

    # Make histogram, result4 is bin values array for histogram
    result4 = Histogram.Histogram(result3, 3) 
    
    return result4
    #print(result4)
    
    
def getTestData():
    wavech = parseDicomFile()
    info = dict()
    ecg = ECG.Ecg(wavech,info)

    peaks = ecg.qrsDetect().tolist()
    
    return (wavech, peaks)

def parseDicomFile():
    ds = dicom.read_file("./Uploads/39DA47B7.dcm")
    
    
    length =  len(ds.WaveformSequence[0].WaveformData)
    
    format="<"+str(length/2)+"h"
    
    wavedata = list(struct.unpack(format,ds.WaveformSequence[0].WaveformData))

    wavech = [
                [
                    elem for index, elem in enumerate( wavedata ) if index % 12 == channel_number
                ] for channel_number in range( 12 )
            ]
    print 'there is ', len(wavech), ' channels in the test dicom'
    
    return wavech
 

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
    print len(wavech)
    info = dict()


    # ECG R peak detection
    ecg = ECG.Ecg(wavech,info)
    peakdata = ecg.qrsDetect(0)
    ecg.visualize_qrs_detection()

    # Searching similar point from manually selected Q point
    aa = CAPS.caps(wavech[0], 120, peakdata)
    # result1 is the list of similar points of manually selected Q point
    result1 = aa.SearchingSimilarPoint()

    # Searching similar point from manually selected T point
    aa = CAPS.caps(wavech[0], 160, peakdata)
    # result2 is the list of similar points of manually selected T point
    result2 = aa.SearchingSimilarPoint()

    # Calculate the Qtc value, 200 is sampling rate
    result3 = Qtc.CalculateQtc(peakdata, result1, result2, 200)

    # Make histogram
    result4 = Histogram.Histogram(result3, 3)

    print(result4)
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
