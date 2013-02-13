__author__ = 'leetop'
import math

# calculate the Qtc value from given waveform data
# peakdata : indices of peak point of waveform data
# Qpoint : Searching result using CAPS from manually selected Q point
# Tpoint : Searching result using CAPS from manually selected T point
# samplingrate : sampling rate of waveform

def CalculateQtc(peakdata, Qpoint, Tpoint, samplingrate) :
    Qtc = []

    if peakdata[1]<Tpoint[0]<Qpoint[0] :
        newPeakdata = peakdata[1:]
        newTpoint = Tpoint[1:]
        newQpoint = Qpoint

    elif Tpoint[0]<Qpoint[0]<peakdata[1] :
        newPeakdata = peakdata
        newTpoint = Tpoint[1:]
        newQpoint = Qpoint
    else :
        newPeakdata = peakdata
        newTpoint = Tpoint
        newQpoint = Qpoint

    endpoint = min(len(newPeakdata)-2, len(newTpoint)+1, len(newQpoint)+1)

    for i in range(1,endpoint) :
        RR = float((newPeakdata[i] - newPeakdata[i-1]))/samplingrate
        QT = float((newTpoint[i-1] - newQpoint[i-1]))/samplingrate
        Qtc.append(float(QT/math.sqrt(RR)))

    return Qtc