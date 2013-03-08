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

    Validated = ValidateData(peakdata, Qpoint, Tpoint)

#    if peakdata[1]<Tpoint[0]<Qpoint[0] :
#        newPeakdata = peakdata[1:]
#        newTpoint = Tpoint[1:]
#        newQpoint = Qpoint

#    elif Tpoint[0]<Qpoint[0]<peakdata[1] :
#        newPeakdata = peakdata
#        newTpoint = Tpoint[1:]
#        newQpoint = Qpoint
#    else :
#        newPeakdata = peakdata
#        newTpoint = Tpoint
#        newQpoint = Qpoint

#    endpoint = min(len(newPeakdata)-2, len(newTpoint)+1, len(newQpoint)+1)

#    for i in range(1,endpoint) :
#        RR = float((newPeakdata[i] - newPeakdata[i-1]))/samplingrate
#        QT = float((newTpoint[i-1] - newQpoint[i-1]))/samplingrate
#        Qtc.append(float(QT/math.sqrt(RR)))

    RR = []

    for i in range(0,len(Validated)) :
        RR.append(float(Validated[i][1] - Validated[i][0])/samplingrate)
        QTc.append((float(Validated[i][3]-Validated[i][2])/math.sqrt(RR[i]))/samplingrate)

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
        if (Qpoint[i-1] != -1) and (Tpoint[i-1]!=-1) and (Tpoint[i] != -1) :
            temp.append(peakdata[i-1])
            temp.append(peakdata[i])
            temp.append(Qpoint[i-1])
            temp.append(Tpoint[i])

            validatedataset.append(temp)
        else :
            continue

    return validatedataset