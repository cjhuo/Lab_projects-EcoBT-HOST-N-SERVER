
import dicom
import struct
import ECG
import CAPS
import Qtc
import Histogram
import numpy
import Filterbank

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
        qpool = multiprocessing.pool.Pool()
        tpool = multiprocessing.pool.Pool()
        self.qpool = qpool
        self.tpool = tpool

    def setFile(self, Dfile = filePath):
        #print(Dfile)
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
        
        self.wavech = [
            [
                int((elem<<5)*self.sensitivity*1000) for index, elem in enumerate( wavedata ) if index % self.NumofChannels == channel_number
            ] for channel_number in range( self.NumofChannels )
        ]

        print('there is ', len(self.wavech), ' channels in the test dicom')
        print('samples of each channel: ', self.NumofsamplesPerChannel)
        print('sampling rate is: ', self.samplingrate)
        
        info = {'samplingrate':self.samplingrate,'name':self.name}
        #Filter is on.
        self.wavech = Filterbank.FilterAllChannel(12,5,self.samplingrate, self.wavech)

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
    
    def getBinInfo(self, qpoint, tpoint, bin=10, channelNo = 2, correlationVal=0.50) :
        ErrorCode = 0
        Qtcs = []
        AvgHR = 0
        LongQTc = 0
        ShortQTc = 0
        NumofHR = 0
        PercentOverQTc = []
        RangeRR = []

        self.peakdata = self.ecg.qrsDetect(1)
        from datetime import datetime
        s1=datetime.now()

#        self.wavech = Filterbank.FilterAllChannel(12, 5, self.samplingrate, self.wavech)
        Wavedata = numpy.array(self.wavech)

        # ECG R peak detection
        index_rangeQ = range( 1, len( self.peakdata ) - 1 )
        index_rangeT = range( 0, len( self.peakdata ) - 1 )

        # Searching similar point from manually selected Q point
        template, offset, stepsize = CAPS.get_templateParam(qpoint, Wavedata)

        SearchingQ = partial( CAPS.get_correlation, 'Q', offset, template, stepsize, self.peakdata, Wavedata, correlationVal )
        Qpoint = self.qpool.map( SearchingQ, index_rangeQ )

        # Searching similar point from manually selected T point
        template, offset, stepsize = CAPS.get_templateParam(tpoint, Wavedata)

        SearchingT = partial( CAPS.get_correlation, 'T', offset, template, stepsize,  self.peakdata, Wavedata, correlationVal )
        Tpoint = self.tpool.map( SearchingT, index_rangeT )

        # Calculate the Qtc value
        Qtcs, AvgHR, LongQTc, ShortQTc, NumofHR, PercentOverQTc, RangeRR, MeanQTc, MedianQTc = Qtc.CalculateQtc(self.peakdata, Qpoint, Tpoint, int(self.samplingrate))

        # Make histogram
        histo = Histogram.histo(Qtcs,bin)
        histodata = histo.Histogram(Qtcs, bin)

        s2=datetime.now()
        print(histodata)
        print(s2-s1)

        return histodata, [AvgHR, str(RangeRR[0]) + '~' + str(RangeRR[1]), NumofHR, LongQTc, ShortQTc, MeanQTc, MedianQTc, PercentOverQTc]#, ErrorCode

    def findrange(self, peaklist, value) :

        iList = numpy.array(peaklist)
        idx = numpy.abs(iList-value).argmin()

        if ((iList[idx]-value) > 0)&(idx>0) :
            return iList[idx-1], iList[idx], 0
        elif iList[idx]-value<0 :
            return iList[idx], iList[idx+1], 0
        else :
            return 0, 0, -1