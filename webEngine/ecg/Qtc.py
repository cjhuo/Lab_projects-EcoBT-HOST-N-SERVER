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

#    DebugData = []

    Validated = ValidateData(peakdata, Qpoint, Tpoint)

    for i in range(0,len(Validated)) :
        IntervalRR = float(Validated[i][1] - Validated[i][0])/samplingrate
        IntervalQTc = (float(Validated[i][3]-Validated[i][2])/math.sqrt(IntervalRR))/samplingrate

        if (IntervalRR>0.33)&(IntervalRR<1.00) :
            if (IntervalQTc>0.3)&(IntervalQTc<0.6) :
                RR.append(IntervalRR)
                QTc.append(IntervalQTc)
#        if ((RR[i]>0.75)|(RR[i]<0.33))&((QTc[i]>0.6)|(QTc[i]<0.3)) :
#        if RR[i]>0.85:
#            DebugData.append(Validated[i])

    AvgHR = round( float(60) / numpy.mean(RR), 2 )
    LongQTc = round( max(QTc), 2 )
    ShortQTc = round( min(QTc), 2 )
    NumofHR = len(RR)
    OverCheck = numpy.array(QTc)>0.45
    PercentOverQTc = round (float(len(numpy.array(QTc)[OverCheck])*100)/len(QTc), 2 )
    RangeRR = round(min(RR), 2 ), round(max(RR), 2 )

    return QTc, AvgHR, LongQTc, ShortQTc, NumofHR, PercentOverQTc, RangeRR

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

    return validatedataset