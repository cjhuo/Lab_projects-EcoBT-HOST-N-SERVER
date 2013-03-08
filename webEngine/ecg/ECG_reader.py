
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
filePath = os.path.join(os.path.dirname(__file__), os.pardir, "static/Uploads/MIICWwIBAAKBgQCMs1QxLEFE.dcm")

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
        print Dfile
        self._parseDicomFile(Dfile)
        
    def _parseDicomFile(self, Dfile):
        ds = dicom.read_file(Dfile)
    
        self.samplingrate = ds[0x5400,0x100][0][0x3a,0x1a].value
        self.name = ds[0x10,0x10].value
        self.NumofsamplesPerChannel = ds[0x5400,0x100][0][0x3a,0x10].value
        self.NumofChannels = ds[0x5400,0x100][0][0x3a,0x5].value
        self.sensitivity = float(ds[0x5400,0x100][0][0x3a,0x200][0][0x3a,0x210].value)
        
    
        fmt="<"+str(self.NumofsamplesPerChannel*self.NumofChannels)+"h"
        wavedata = list(struct.unpack(fmt,ds.WaveformSequence[0].WaveformData))
        
        # original unit in dicom is milliVolt, converted unit in self.wavech is microVolt, assuming channel sensitivity's unit is mV
        # data in dicom file is mising the last 5 bits which will be always 0, adding them when reading
        if 'MIICWwIBAAKBgQCMs1QxLEFE.dcm' in Dfile:
            self.wavech = [
                        [
                            int((elem)*self.sensitivity*1000) for index, elem in enumerate( wavedata ) if index % self.NumofChannels == channel_number
                        ] for channel_number in range( self.NumofChannels )
                    ]            
        else:
            self.wavech = [
                        [
                            int((elem << 5)*self.sensitivity*1000) for index, elem in enumerate( wavedata ) if index % self.NumofChannels == channel_number
                        ] for channel_number in range( self.NumofChannels )
                    ]    
        print 'there is ', len(self.wavech), ' channels in the test dicom'
        print 'samples of each channel: ', self.NumofsamplesPerChannel
        print 'sampling rate is: ', self.samplingrate
        
        info = {'samplingrate':self.samplingrate,'name':self.name}
        self.ecg = ECG.Ecg(self.wavech,info)
        
    def getTestData(self):
        #get only first 2500 samples for each channels
        if self.NumofsamplesPerChannel > 2500:
            wavedata = [
                        [
                            self.wavech[channel_number][i] for i in range(2500)
                        ] for channel_number in range( self.NumofChannels )
                    ] 
        else: 
            wavedata = self.wavech   
        return wavedata
    
    def getBinInfo(self, qpoint, tpoint, bin=10, channelNo = 2) :
        self.peakdata = self.ecg.qrsDetect(0)
        from datetime import datetime
        s1=datetime.now()

        # ECG R peak detection
        index_range = range( 1, len( self.peakdata ) - 2 )
        
        # Searching similar point from manually selected Q point
        new_func = partial( CAPS.SearchingSimilarPoint, qpoint, self.peakdata, self.wavech[int(channelNo)] )
        Qpoint = multiprocessing.pool.Pool().map( new_func, index_range )
    
        # Searching similar point from manually selected T point
        new_func = partial( CAPS.SearchingSimilarPoint, tpoint, self.peakdata, self.wavech[int(channelNo)] )
        Tpoint = multiprocessing.pool.Pool().map( new_func, index_range )
    
        # Calculate the Qtc value
        Qtcs = Qtc.CalculateQtc(self.peakdata, Qpoint, Tpoint, int(self.samplingrate))

        # Make histogram
        histo = Histogram.histo(Qtcs,bin)
        histodata = histo.Histogram(Qtcs, bin)
    
        s2=datetime.now()
        print(histodata)
        print s2-s1
        return histodata

