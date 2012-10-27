__author__ = 'leetop'

# Making histogram
# originaldata : data to make histogram
# totalbin : the number of bins for making histogram
# histodata : the result of histogram

def Histogram(originaldata, totalbin) :
    histodata = []

    for i in range(0,totalbin) :
        histodata.append(0)

    minimumVal = min(originaldata)
    maximumVal = max(originaldata)

    binsize = float(maximumVal-minimumVal)/totalbin

    for i in range(0,len(originaldata)) :

        if originaldata[i]==maximumVal :
            location=totalbin-1
        else :
            location = int((originaldata[i]-minimumVal)/binsize)

        histodata[location]+=1

    return histodata