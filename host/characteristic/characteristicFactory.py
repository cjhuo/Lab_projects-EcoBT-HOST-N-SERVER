'''
Created on Feb 9, 2013

@author: cjhuo
'''
from host.characteristic.implementation import *

def createCharacteristic(UUID, instance, service, peripheralWorker):
    c = None
    if UUID == "2A23":
        c = DeviceInfo.DeviceInfo() 
    elif UUID == "FFA6":
        c = ACCXYZ.ACCXYZ()
    elif UUID == "FFA1":
        c = ACCEnable.ACCEnable()
    elif UUID == "FE11":
        c = SIDsCO2Status.SIDsCO2Status()
    elif UUID == "FE12":
        c = SIDsCO2Set.SIDsCO2Set()
    elif UUID == "FE13":
        c = SIDsCO2Read.SIDsCO2Read()
    elif UUID == "FE14":
        c = SIDsTempRead.SIDsTempRead()
    elif UUID == "FE15":
        c = SIDsHumidRead.SIDsHumidRead()
    elif UUID == "FF11" or UUID == "FF12":
        c = LEDEnable.LEDEnable()
    elif UUID == "FF13" or UUID == "FF14":
        c = LEDBlinkInterval.LEDBlinkInterval()
    elif UUID == "FF21":
        c = RTCSet.RTCSet()
    elif UUID == "FF22":
        c = RTCGet.RTCGet()  
    elif UUID == "FEC2":
        c = ECGStatus.ECGStatus()    
    elif UUID == "FEC5":
        c = ECGSet.ECGSet() 
    elif UUID == "FEC6" or UUID == "FEC7":
        c = ECGGet.ECGGet()     
    elif UUID == "ADD1":
        c = SIDsAudioSet.SIDsAudioSet()
    elif UUID == "ADD2":
        c = SIDsAudioRead.SIDsAudioRead()
    elif UUID == "BDA1":
        c = SIDsBodySet.SIDsBodySet()
    elif UUID == "BDA2":
        c = SIDsBodyRead.SIDsBodyRead()
    else: # found a profile that has not implemented
        c = Characteristic.Characteristic()
    c.setUUIDInstanceServicePeripheralWorker(UUID, instance, service, peripheralWorker)
    c.setRole() # identify itself if it is a setter or getter of the service

    return c    
    