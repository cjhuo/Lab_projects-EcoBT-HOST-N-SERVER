__author__ = 'leetop'

# Making histogram
# originaldata : data to make histogram
# totalbin : the number of bins for making histogram
# histodata : the result of histogram

class histo() :

    def __init__(self, originaldata, totalbin) :
        # self.minimumVal : minimum data of given dataset. Starting value of histogram
        # self.binsize : the size of histogram bin.
        if len(originaldata)!=0 :
            self.originaldata = originaldata
            self.minimumVal = min(self.originaldata)
            self.maximumVal = max(self.originaldata)
            self.binsize = float(self.maximumVal-self.minimumVal)/totalbin

    def Histogram(self, originaldata, totalbin) :
        histodata = []
        formatted = []

        if len(originaldata)!=0 :

            for i in range(0,totalbin) :
                histodata.append(0)

            for i in range(0,len(originaldata)) :

                if originaldata[i]==self.maximumVal :
                    location=totalbin-1
                else :
                    location = int((originaldata[i]-self.minimumVal)/self.binsize)

                histodata[location]+=1

            for i in range(0,totalbin) :
                temp = []
                temp.append(self.minimumVal+(i*self.binsize))
                temp.append(self.minimumVal+((i+1)*self.binsize))
                temp.append(histodata[i])

                formatted.append(temp)


        return formatted