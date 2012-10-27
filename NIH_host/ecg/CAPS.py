import scipy
import scipy.stats
import numpy

class caps() :
    def __init__(self, originaldata, searchingpoint, peakdata) :

        # originaldata : original waveform data
        # searchingpoint : index to be found
        # peakdata : indices of peak point of original waveform data

        self.threshold = 0.5        # threshold : threshold for determining the stepsize
        self.tempsize = 40          # tempsize : template size for making template
        self.originaldata = numpy.array(originaldata)
        self.searchingpoint = searchingpoint
        self.template = self.MakingTemplate()
        self.stepsize = self.FindingStepSize()
        self.peakdata = peakdata

    def MakingTemplate(self) :
        startpoint = self.searchingpoint-(self.tempsize/2)
        endpoint = self.searchingpoint+(self.tempsize/2)
        self.template = self.originaldata[startpoint:endpoint]

        return self.template

# Determine step size for coarse finding with autocorrelation
    def FindingStepSize(self):
        zeropad = numpy.zeros(self.template.size-1,numpy.int)
        datapadded = numpy.hstack((zeropad, self.template, zeropad))

        checkflag = False

        for i in range(self.template.size*2-1) :
            autocorr = scipy.stats.pearsonr(self.template, datapadded[i:i+self.template.size])

            if checkflag==False :
                if autocorr[0]>self.threshold :
                    checkflag=True
                    x1=i
            if checkflag==True :
                if autocorr[0]<self.threshold :
                    checkflag = False
                    x2=i

        self.stepsize = x2-x1

        return self.stepsize

    def MakingOriginal(self, peakpoint, RtoR):
        startpoint = peakpoint-(RtoR/2)
        endpoint = peakpoint+(RtoR/2)
        self.bufforiginal = self.originaldata[startpoint:endpoint]

        return self.bufforiginal

# First coarse searching, and then specific searching
    def MatchingTemplate(self):
        zerodata = numpy.zeros(self.template.size-1)
        datapadded = numpy.hstack((zerodata,self.bufforiginal,zerodata))
        checkflag = False
        maxcorr = -1
        for i in range(0,self.bufforiginal.size,self.stepsize) :
            crosscorr, pvalue = scipy.stats.pearsonr(self.template, datapadded[i:i+self.template.size])

            if checkflag==False :
                if crosscorr>self.threshold :
                    checkflag=True
                    x1=i
            if checkflag==True :
                if crosscorr<self.threshold :
                    checkflag = False
                    x2=i

        for i in range(x1, x2) :
            crosscorr, pvalue = scipy.stats.pearsonr(self.template, datapadded[i:i+self.template.size])

            if crosscorr>maxcorr :
                maxcorr = crosscorr
                maxindex = i

        return maxindex

    def SearchingSimilarPoint(self):
        self.MakingTemplate()
        self.FindingStepSize()
        maxidx = list()
        offset = (self.template.size/2) - 1;
        for i in range(0,len(self.peakdata)-1) :
            RtoR = self.peakdata[i+1]-self.peakdata[i]
            self.MakingOriginal(self.peakdata[i], RtoR)
            maxidx.append(self.peakdata[i]-(RtoR/2)+self.MatchingTemplate()-offset)

        return maxidx