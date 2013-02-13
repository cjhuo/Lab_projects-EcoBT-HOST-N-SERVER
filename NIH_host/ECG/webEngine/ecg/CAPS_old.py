import scipy
import scipy.stats
import numpy

class caps() :
    def __init__(self, originaldata, searchingpoint, peakdata) :

        # originaldata : original waveform data
        # searchingpoint : index to be found
        # peakdata : indices of peak point of original waveform data

        self.threshold = 0.5  # threshold : threshold for determining the stepsize
        self.tempsize = 40  # tempsize : template size for making template
        self.originaldata = numpy.array(originaldata)
        self.searchingpoint = searchingpoint
        self.template = self.MakingTemplate()
        self.stepsize = self.FindingStepSize()
        self.peakdata = peakdata
        self.offset = 0

    def MakingTemplate(self) :
        startpoint = self.searchingpoint - (self.tempsize / 2)
        endpoint = self.searchingpoint + (self.tempsize / 2)

        if startpoint < 0 :
            self.offset = startpoint
            startpoint = 0
            endpoint = endpoint - self.offset

        self.template = self.originaldata[startpoint:endpoint]

        return self.template

# Determine step size for coarse finding with autocorrelation
    def FindingStepSize(self):
        zeropad = numpy.zeros(len(self.template) - 1, numpy.int)
        datapadded = numpy.hstack((zeropad, self.template, zeropad))
        autocorrs = list(
            scipy.stats.pearsonr(self.template, datapadded[ i:i + len(self.template) ])[0]
                for i in range(len(self.template) * 2 - 1)
        )
        arr_autocorrs = numpy.array(autocorrs)
        filtered_index = numpy.argwhere(arr_autocorrs > self.threshold)
        return (filtered_index[-1][0] - filtered_index[0][0]) / 2
# cost 7sec
        '''
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
#cost 4.4sec
        '''
    def MakingOriginal(self, peakpoint, RtoR):
        startpoint = peakpoint - ((RtoR + self.template.size) / 2)
        endpoint = peakpoint + ((RtoR + self.template.size) / 2)

        self.bufforiginal = self.originaldata[startpoint:endpoint]

        return self.bufforiginal

# First coarse searching, and then specific searching
    def MatchingTemplate(self):
#        zerodata = numpy.zeros(self.template.size/2)
#        datapadded = numpy.hstack((self.bufforiginal,zerodata))
        checkflag = False
        maxcorr = -1

        x1 = []
        x2 = []

        for i in range(0, self.bufforiginal.size - self.template.size, self.stepsize) :
            crosscorr, pvalue = scipy.stats.pearsonr(self.template, self.bufforiginal[i:i + self.template.size])

            if checkflag == False :
                if crosscorr > self.threshold :
                    checkflag = True
                    x1.append(i)
            if checkflag == True :
                if crosscorr < self.threshold :
                    checkflag = False
                    x2.append(i)

        if len(x1) == 0 :
            startingpoint = 0
        else :
            startingpoint = min(x1)

        if len(x2) == 0 :
            endpoint = self.bufforiginal.size - self.template.size
        else :
            endpoint = max(x2)

        for i in range(startingpoint, endpoint) :
            crosscorr, pvalue = scipy.stats.pearsonr(self.template, self.bufforiginal[i:i + self.template.size])

            if crosscorr > maxcorr :
                maxcorr = crosscorr
                maxindex = i

        return maxindex

    def SearchingSimilarPoint(self, l):
        self.FindingStepSize()

        # maxidx = []
        offset = (self.template.size / 2);

        for i in range(1, len(self.peakdata) - 2) :

            RtoR = self.peakdata[i + 1] - self.peakdata[i]
            self.MakingOriginal(self.peakdata[i], RtoR)
            l.append(self.peakdata[i] - ((RtoR + self.template.size) / 2) + self.MatchingTemplate() + offset + self.offset)
#            maxidx.append(self.peakdata[i]-((RtoR+self.tempsize)/2)+self.MatchingTemplate()-offset+self.offset)
        # print self.searchingpoint
        # return maxidx
