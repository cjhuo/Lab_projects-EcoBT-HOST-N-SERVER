#from multiprocessing import Pool

__author__ = 'leetop'

import dicom
import struct
import ECG
import CAPS
import Qtc
import Histogram
from dicom.tag import Tag
import multiprocessing
from functools import partial

import os
filePath = os.path.join(os.path.dirname(__file__), os.pardir, "Uploads/MIICWwIBAAKBgQCMs1QxLEFE.dcm")

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
        
    def setFile(self, Dfile = filePath):
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
    
    def getBinInfo(self, qpoint, tpoint, bin=10, samplingrate=250) :
        from datetime import datetime
        s1=datetime.now()
    
        # ECG R peak detection
        index_range = range( 1, len( self.peakdata ) - 2 )
    
        # Searching similar point from manually selected Q point
        new_func = partial( CAPS.SearchingSimilarPoint, qpoint, self.peakdata, self.wavech[0] )
        Qpoint = multiprocessing.pool.Pool(1).map( new_func, index_range )
    
        # Searching similar point from manually selected T point
    
        new_func = partial( CAPS.SearchingSimilarPoint, tpoint, self.peakdata, self.wavech[0] )
        Tpoint = multiprocessing.pool.Pool(1).map( new_func, index_range )
    
        # Calculate the Qtc value
        Qtcs = Qtc.CalculateQtc(self.peakdata, Qpoint, Tpoint, int(samplingrate))
    
        # Make histogram
        histo = Histogram.histo(Qtcs,10)
        histodata = histo.Histogram(Qtcs, 10 )
    
        s2=datetime.now()
        print(histodata)
        print s2-s1
        return histodata

