__author__ = 'leetop'

import sys
import dicom
import struct
import numpy as np
import SDCard_reader

from dicom.tag import Tag

def initData(ds, info) :
    ds[0x0008,0x0012].value = info['Instance Creation Date']
    ds[0x0008,0x0013].value = info['Instance Creation Time']
    ds[0x0008,0x0016].value = ''
    ds[0x0008,0x0018].value = ''
    ds[0x0008,0x0020].value = info['Study Date']
    ds[0x0008,0x0023].value = info['Content Date']
    ds[0x0008,0x0025].value = ''
    ds[0x0008,0x002a].value = ''
    ds[0x0008,0x0030].value = info['Study Time']
    ds[0x0008,0x0033].value = ''
    ds[0x0008,0x0050].value = ''
    ds[0x0008,0x0030].value = info['Study Time']

    return ds

def packDICOM(ecg_data, outputfilename) :
    ds = dicom.read_file("template.dcm")

    waveform = list()
    NumofSamplesPerChannel = len(ecg_data['V1'])
    NumofChannels = 12

    info = {}
    date = "%04d%02d%02d" % (ecg_data['start_time'].year, ecg_data['start_time'].month, ecg_data['start_time'].day)
    time = "%02d%02d%02d" % (ecg_data['start_time'].hour, ecg_data['start_time'].minute, ecg_data['start_time'].second)
    info['Instance Creation Date'] = date
    info['Instance Creation Time'] = time
    info['Study Date'] = ''
    info['Study Time'] = ''
    info['Study Time'] = ''
    info['Content Date'] = ''
    ds = initData(ds, info)

    """
    minCom=list()
    minCom.append(min(ecg_data['LeadI']))
    minCom.append(min(ecg_data['LeadII']))
    minCom.append(min(ecg_data['LeadIII']))
    minCom.append(min(ecg_data['aVR']))
    minCom.append(min(ecg_data['aVL']))
    minCom.append(min(ecg_data['aVF']))
    minCom.append(min(ecg_data['V1']))
    minCom.append(min(ecg_data['V2']))
    minCom.append(min(ecg_data['V3']))
    minCom.append(min(ecg_data['V4']))
    minCom.append(min(ecg_data['V5']))
    minCom.append(min(ecg_data['V6']))

    arr_ecg_I=np.array(ecg_data['LeadI'])-minCom[0]
    arr_ecg_II=np.array(ecg_data['LeadII'])-minCom[1]
    arr_ecg_III=np.array(ecg_data['LeadIII'])-minCom[2]
    arr_ecg_aVR=np.array(ecg_data['aVR'])-minCom[3]
    arr_ecg_aVL=np.array(ecg_data['aVL'])-minCom[4]
    arr_ecg_aVF=np.array(ecg_data['aVF'])-minCom[5]
    arr_ecg_V1=np.array(ecg_data['V1'])-minCom[6]
    arr_ecg_V2=np.array(ecg_data['V2'])-minCom[7]
    arr_ecg_V3=np.array(ecg_data['V3'])-minCom[8]
    arr_ecg_V4=np.array(ecg_data['V4'])-minCom[9]
    arr_ecg_V5=np.array(ecg_data['V5'])-minCom[10]
    arr_ecg_V6=np.array(ecg_data['V6'])-minCom[11]
    """

    arr_ecg_I=np.array(ecg_data['LeadI'])
    arr_ecg_II=np.array(ecg_data['LeadII'])
    arr_ecg_III=np.array(ecg_data['LeadIII'])
    arr_ecg_aVR=np.array(ecg_data['aVR'])
    arr_ecg_aVL=np.array(ecg_data['aVL'])
    arr_ecg_aVF=np.array(ecg_data['aVF'])
    arr_ecg_V1=np.array(ecg_data['V1'])
    arr_ecg_V2=np.array(ecg_data['V2'])
    arr_ecg_V3=np.array(ecg_data['V3'])
    arr_ecg_V4=np.array(ecg_data['V4'])
    arr_ecg_V5=np.array(ecg_data['V5'])
    arr_ecg_V6=np.array(ecg_data['V6'])

    arr_ecg_I=arr_ecg_I.astype('int16')
    arr_ecg_II=arr_ecg_II.astype('int16')
    arr_ecg_III=arr_ecg_III.astype('int16')
    arr_ecg_aVR=arr_ecg_aVR.astype('int16')
    arr_ecg_aVL=arr_ecg_aVL.astype('int16')
    arr_ecg_aVF=arr_ecg_aVF.astype('int16')
    arr_ecg_V1=arr_ecg_V1.astype('int16')
    arr_ecg_V2=arr_ecg_V2.astype('int16')
    arr_ecg_V3=arr_ecg_V3.astype('int16')
    arr_ecg_V4=arr_ecg_V4.astype('int16')
    arr_ecg_V5=arr_ecg_V5.astype('int16')
    arr_ecg_V6=arr_ecg_V6.astype('int16')

    for i in range(0,NumofSamplesPerChannel) :
        waveform.append(arr_ecg_I[i])
        waveform.append(arr_ecg_II[i])
        waveform.append(arr_ecg_III[i])
        waveform.append(arr_ecg_aVR[i])
        waveform.append(arr_ecg_aVL[i])
        waveform.append(arr_ecg_aVF[i])
        waveform.append(arr_ecg_V1[i])
        waveform.append(arr_ecg_V2[i])
        waveform.append(arr_ecg_V3[i])
        waveform.append(arr_ecg_V4[i])
        waveform.append(arr_ecg_V5[i])
        waveform.append(arr_ecg_V6[i])

    format="<"+str(NumofSamplesPerChannel*NumofChannels)+"h"
    ds.WaveformSequence[0].WaveformData = struct.pack(format, *(waveform))
    ds[0x5400,0x100][0][0x3a,0x10].value = NumofSamplesPerChannel
    ds[0x5400,0x100][0][0x3a,0x5].value = NumofChannels
    ds[0x5400,0x100][0][0x3a,0x1a].value = '250'

    ds.save_as(outputfilename)

    ds2 = dicom.read_file(outputfilename)
    a=list()


if __name__ == "__main__":
    filename = "ecg_data_0.txt"
    filename = sys.argv[1]
    reader = SDCard_reader.SDCard_Reader(filename)
    ecg_data = reader.read_data()
    date = "%04d%02d%02d" % (ecg_data['start_time'].year, ecg_data['start_time'].month, ecg_data['start_time'].day)
    time = "%02d%02d%02d" % (ecg_data['start_time'].hour, ecg_data['start_time'].minute, ecg_data['start_time'].second)
    outfile = "%s_%s.dcm" % (date, time)

    packDICOM(ecg_data, outfile)
