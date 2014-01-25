import objc

# Load IOBluetooth
objc.loadBundle('IOBluetooth', globals(),
                bundle_path=objc.pathForFramework("IOBluetooth.framework"))

# CBPeripheralManager states CONSTS from CBPeripheralManager.h
CBPeripheralManagerStateUnknown = 0
CBPeripheralManagerStateResetting = 1
CBPeripheralManagerStateUnsupported = 2
CBPeripheralManagerStateUnauthorized = 3
CBPeripheralManagerStatePoweredOff = 4
CBPeripheralManagerStatePoweredOn = 5

# CBPeripheralManager advertisement key CONSTS from CBAdvertisementData.h
CBAdvertisementDataServiceUUIDsKey = u'kCBAdvDataServiceUUIDs'
CBAdvertisementDataLocalNameKey = u'kCBAdvDataLocalName'

# descriptor type UUID, only 0x2901 and 0x2904 can be created for current apple implementation
CBUUIDCharacteristicExtendedPropertiesString = u'2900'
CBUUIDCharacteristicUserDescriptionString = u'2901'
CBUUIDClientCharacteristicConfigurationString = u'2902'
CBUUIDServerCharacteristicConfigurationString = u'2903'
CBUUIDCharacteristicFormatString = u'2904'
CBUUIDCharacteristicAggregateFormatString = u'2905'

# CBCharacteristicProperties CONSTS from CBCharacteristic.h
CBCharacteristicPropertyBroadcast                                                = 0x01
CBCharacteristicPropertyRead                                                    = 0x02
CBCharacteristicPropertyWriteWithoutResponse                                    = 0x04
CBCharacteristicPropertyWrite                                                    = 0x08
CBCharacteristicPropertyNotify                                                    = 0x10
CBCharacteristicPropertyIndicate                                                = 0x20
CBCharacteristicPropertyAuthenticatedSignedWrites                                = 0x40
CBCharacteristicPropertyExtendedProperties                                        = 0x80
#CBCharacteristicPropertyNotifyEncryptionRequired NS_ENUM_AVAILABLE(NA, 6_0)        = 0x100
#CBCharacteristicPropertyIndicateEncryptionRequired NS_ENUM_AVAILABLE(NA, 6_0)    = 0x200

# CBAttributePermissions CONSTS from CBCharacteristic.h
CBAttributePermissionsReadable                    = 0x01
CBAttributePermissionsWriteable                    = 0x02
CBAttributePermissionsReadEncryptionRequired    = 0x04
CBAttributePermissionsWriteEncryptionRequired    = 0x08
    
# CBError CONSTS from CBError.h
CBATTErrorSuccess     = 0x00,
CBATTErrorInvalidHandle                            = 0x01
CBATTErrorReadNotPermitted                        = 0x02
CBATTErrorWriteNotPermitted                        = 0x03
CBATTErrorInvalidPdu                            = 0x04
CBATTErrorInsufficientAuthentication            = 0x05
CBATTErrorRequestNotSupported                    = 0x06
CBATTErrorInvalidOffset                            = 0x07
CBATTErrorInsufficientAuthorization                = 0x08
CBATTErrorPrepareQueueFull                        = 0x09
CBATTErrorAttributeNotFound                        = 0x0A
CBATTErrorAttributeNotLong                        = 0x0B
CBATTErrorInsufficientEncryptionKeySize            = 0x0C
CBATTErrorInvalidAttributeValueLength            = 0x0D
CBATTErrorUnlikelyError                            = 0x0E
CBATTErrorInsufficientEncryption                = 0x0F
CBATTErrorUnsupportedGroupType                    = 0x10
CBATTErrorInsufficientResources                    = 0x11

# NSString encoding CONSTS
NSUTF8StringEncoding = 4

# Profile Identifier dictionary 
# used to initialize service object and characteristic object
ProfileDict = {
# Service Profile
"180D": '',             # EcoBT Profile
"180A": '',             # "180A" Generic Access Profile
"FF10": '',             # LED Profile
"FFA0": '',             # ACC Profile
"FE10": '',             # SIDS SHT25 Profile
"FF20": '',             # RTC Profile,
"FEC0": '',             # ECG Profile
# Characteristic Profile
"2A23": 'DeviceInfo',             # Device Info Characteristic Profile
"FE11": 'SIDsCO2Status',             # SIDs Enable Characteristic Profile
"FE12": 'SIDsCO2Set',             # SIDs Rate Characteristic Profile, default 10
"FE13": 'SIDsCO2Read',             # SIDs Start Characteristic Profile , default 0
"FE14": 'SIDsTempRead' ,             # Temperature Characteristic Profile
"FE15": 'SIDsHumidRead',             # Humidity Characteristic Profile
"FF11": 'LEDEnable',             # LED 0 Enable Characteristic Profile
"FF12": 'LEDEnable',             # LED 1 Enable Characteristic Profile
"FF13": 'LEDBlinkInterval',             # LED 0 Blink Characteristic Profile
"FF14": 'LEDBlinkInterval',             # LED 1 Blink Characteristic Profile
"FFA1": 'ACCEnable',             # ACC Enable Characteristic Profile
#"FFA2",             # ACC Range Selection Characteristic Profile
#"FFA3",             # ACC X Characteristic Profile
#"FFA4",             # ACC Y Characteristic Profile
#"FFA5",             # ACC Z Characteristic Profile
"FFA6": 'ACCXYZ',             # ACC XYZ Characteristic Profile
"FF21": 'RTCSet',             # RTC Set Time Characteristic Profile
"FF22": 'RTCGet',              # RTC Get Time Characteristic Profile
#"FEC1",              # ECG characteristic info
"FEC2": 'ECGStatus',              # ECG characteristic status
#"FEC3",              # ECG characteristic config 1
#"FEC4",              # ECG characteristic config 2
"FEC5": 'ECGSet',              # ECG characteristic start flag
"FEC6": 'ECGGet',              # ECG characteristic first 6 channels
"FEC7": 'ECGGet',              # ECG characteristic second 6 channels
#"FEC8"              # ECG characteristic
}



