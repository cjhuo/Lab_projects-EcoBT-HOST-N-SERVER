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

SECURITY_SERVICE = '7770'

# Profile Identifier dictionary 
# used to initialize service object and characteristic object
ProfileDict = {
# service UUID
'7770': { # security
         '7771': 'SecurityType',
         '7772': 'SecurityKey',
         '7773': 'SecurityIV' 
         },
'7780': {
         # characteristic UUID and implementation
         '7781': 'TestCharacteristic'
         },
               
}



