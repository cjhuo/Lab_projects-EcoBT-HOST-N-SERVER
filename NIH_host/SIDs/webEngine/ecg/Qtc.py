__author__ = 'leetop'
import math

# calculate the Qtc value from given waveform data
# peakdata : indices of peak point of waveform data
# Qpoint : Searching result using CAPS from manually selected Q point
# Tpoint : Searching result using CAPS from manually selected T point
# samplingrate : sampling rate of waveform

def CalculateQtc(peakdata, Qpoint, Tpoint, samplingrate) :
    Qtc = list()

    for i in range(1,len(peakdata)-2) :
        RR = float((peakdata[i+1] - peakdata[i]))/samplingrate
        QT = float((Tpoint[i-1]-Qpoint[i-1]))/samplingrate
        Qtc.append(float(QT/math.sqrt(RR)))

    return Qtc