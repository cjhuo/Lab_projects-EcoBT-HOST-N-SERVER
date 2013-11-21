__author__ = 'leetop'
import math
import numpy

# calculate the Qtc value from given waveform data
# peakdata : indices of peak point of waveform data
# Qpoint : Searching result using CAPS from manually selected Q point
# Tpoint : Searching result using CAPS from manually selected T point
# samplingrate : sampling rate of waveform

def CalculateQtc(peakdata, Qpoint, Tpoint, samplingrate) :
    QTc = []
    RR  = []

    Validated = ValidateData(peakdata, Qpoint, Tpoint)

    for i in range(0,len(Validated)) :
        IntervalRR = float(Validated[i][1] - Validated[i][0])/samplingrate
        IntervalQTc = (float(Validated[i][3]-Validated[i][2])/math.sqrt(IntervalRR))/samplingrate

        if (IntervalRR>0.33)&(IntervalRR<1.00) :
            if (IntervalQTc>0.3)&(IntervalQTc<0.6) :
                RR.append(IntervalRR)
                QTc.append(IntervalQTc)

#    AverageQTc = numpy.mean(QTc)
#    StdQTc = numpy.std(QTc)

#    print AverageQTc, StdQTc

    FilteredQTc = []
    FilteredRR = []

    Outlier = int(len(QTc) * 0.05)
    SortedIndex = sorted(range(len(QTc)), key=QTc.__getitem__)
    QTcIndex = SortedIndex[Outlier:len(SortedIndex)-Outlier]

    for i in QTcIndex :
        FilteredQTc.append(QTc[i])
        FilteredRR.append(RR[i])

#    for i in range(0,len(QTc)) :
#        if ((QTc[i]<(AverageQTc-(3*StdQTc))) | (QTc[i]>(AverageQTc+(3*StdQTc)))) :
#            FilteredQTc.append(QTc[i])
#            FilteredRR.append(RR[i])

    AvgHR = round( float(60) / numpy.mean(FilteredRR), 2 )
    LongQTc = round( max(FilteredQTc), 2 )
    ShortQTc = round( min(FilteredQTc), 2 )
    NumofHR = len(FilteredRR)
    OverCheck = numpy.array(FilteredQTc)>0.45
    PercentOverQTc = round (float(len(numpy.array(FilteredQTc)[OverCheck])*100)/len(FilteredQTc), 2 )
    RangeRR = round(min(FilteredRR), 2 ), round(max(FilteredRR), 2 )

    return FilteredQTc, AvgHR, LongQTc, ShortQTc, NumofHR, PercentOverQTc, RangeRR

def ValidateData(peakdata, Qpoint, Tpoint) :
    validatedataset = list()
    for i in range(1,len(Tpoint)) :
        temp = []
        if (Qpoint[i-1] != -1) & (Tpoint[i-1]!=-1) & (Tpoint[i] != -1) :
            temp.append(peakdata[i-1])
            temp.append(peakdata[i])
            temp.append(Qpoint[i-1])
            temp.append(Tpoint[i])

            validatedataset.append(temp)
        else :
            continue
    print validatedataset
    return validatedataset