__authors__ = 'leetop, cj'

import dicom
import struct
import ECG
import CAPS
import Qtc
import Histogram

#from pylab import *

class ECG_reader():
    def __init__(self):
        pass
        '''
        self.file = None
        self.samplingrate = None
        self.name = None
        self.NumofsamplesPerChannel = None
        self.NumofChannels = None
        '''
        
    def setFile(self, Dfile = "Uploads/MIICWwIBAAKBgQCMs1QxLEFE.dcm"):
        self._parseDicomFile(Dfile)
        
    def _parseDicomFile(self, Dfile):
        ds = dicom.read_file(Dfile)
    
        self.samplingrate = ds[0x5400,0x100][0][0x3a,0x1a].value
        self.name = ds[0x10,0x10].value
        self.NumofsamplesPerChannel = ds[0x5400,0x100][0][0x3a,0x10].value
        self.NumofChannels = ds[0x5400,0x100][0][0x3a,0x5].value
    
        fmt="<"+str(self.NumofsamplesPerChannel*self.NumofChannels)+"h"
        wavedata = list(struct.unpack(fmt,ds.WaveformSequence[0].WaveformData))
    
        self.wavech = [
                    [
                        elem for index, elem in enumerate( wavedata ) if index % self.NumofChannels == channel_number
                    ] for channel_number in range( self.NumofChannels )
                ]    
        print 'there is ', len(self.wavech), ' channels in the test dicom'
        print 'samples of each channel: ', self.NumofsamplesPerChannel
        print 'sampling rate is: ', self.samplingrate
        
        info = {'samplingrate':self.samplingrate,'name':self.name}
        ecg = ECG.Ecg(self.wavech,info)
        self.peakdata = ecg.qrsDetect(0)
    
        
    
    def getTestData(self):
        #get only first 2400 samples for each channels
        if self.NumofsamplesPerChannel > 2400:
            wavedata = [
                        [
                            self.wavech[channel_number][i] for i in range(2400)
                        ] for channel_number in range( self.NumofChannels )
                    ] 
        else: 
            wavedata = self.wavech   
        peaks = self.peakdata.tolist()
        return (wavedata, peaks)

    def getBinInfo(self,qPoint, tPoint, bin = 10):
        from multiprocessing import Process, Manager
        manager = Manager()
        aa = CAPS.caps(self.wavech[0], qPoint, self.peakdata)
        # result1 is the list of similar points of manually selected Q point
        
        result1 = manager.list()
        p1 = Process(target=aa.SearchingSimilarPoint, args=(result1,))
        #result1 = aa.SearchingSimilarPoint()
        p1.start()
        # Searching similar point from manually selected T point
        aa = CAPS.caps(self.wavech[0], tPoint, self.peakdata)
        # result2 is the list of similar points of manually selected T point
        result2 = manager.list()
        p2 = Process(target=aa.SearchingSimilarPoint, args=(result2,))
        #result2 = aa.SearchingSimilarPoint()
        p2.start()
        
        p1.join()
        p2.join()
        
        # Calculate the Qtc value, 200 is sampling rate
        result3 = Qtc.CalculateQtc(self.peakdata, result1, result2, int(self.samplingrate))
  
        # Make histogram, result4 is bin values array for histogram
        histo = Histogram.histo(result3, bin)
        result4 = histo.Histogram(result3, bin)
        
        return result4

if __name__ == "__main__":
    e = ECG_reader()
    e.setFile()
    print e.getBinInfo(342, 625, 10)
'''
def getBinInfo(qPoint, tPoint):
    wavech = parseDicomFile()
    info = dict()
    ecg = ECG.Ecg(wavech,info)
    peakdata = ecg.qrsDetect(0)

    aa = CAPS.caps(wavech[0], qPoint, peakdata)
    # result1 is the list of similar points of manually selected Q point
    result1 = aa.SearchingSimilarPoint()

    # Searching similar point from manually selected T point
    aa = CAPS.caps(wavech[0], tPoint, peakdata)
    # result2 is the list of similar points of manually selected T point
    result2 = aa.SearchingSimilarPoint()

    # Calculate the Qtc value, 200 is sampling rate
    result3 = Qtc.CalculateQtc(peakdata, result1, result2, 200)

    # Make histogram, result4 is bin values array for histogram
    histo = Histogram.histo(result3,3)
    result4 = histo.Histogram(result3, 3)
    
    return result4
    #print(result4)   
    
def getTestData():
    wavech = parseDicomFile()
    info = dict()
    ecg = ECG.Ecg(wavech,info)
    peakdata = ecg.qrsDetect(0)

    peaks = peakdata.tolist()
    
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
    histo = Histogram.histo(result3,3)
    result4 = histo.Histogram(result3, 3)
    print(result4)
'''
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


if __name__ == "__main__":
    main()
'''