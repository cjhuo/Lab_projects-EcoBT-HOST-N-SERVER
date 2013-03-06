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
        c = SIDsEnable.SIDsEnable()
    elif UUID == "FE12":
        c = SIDsRate.SIDsRate()
    elif UUID == "FE13":
        c = SIDsStart.SIDsStart()
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
    else: # found a profile that has not implemented
        c = Characteristic.Characteristic()
    c.setUUIDInstanceServicePeripheralWorker(UUID, instance, service, peripheralWorker)
    c.setRole() # identify itself if it is a setter or getter of the service

    return c    
    