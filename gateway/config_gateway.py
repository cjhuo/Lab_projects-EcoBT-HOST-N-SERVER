import objc

# Load IOBluetooth
objc.loadBundle('IOBluetooth', globals(),
                bundle_path=objc.pathForFramework("IOBluetooth.framework"))

# IOBluetooth CBCentralManager state CONSTS
CBCentralManagerStateUnkown = 0
CBCentralManagerStateResetting = 1
CBCentralManagerStateUnsupported = 2
CBCentralManagerStateUnauthorized = 3
CBCentralManagerStatePoweredOff = 4
CBCentralManagerStatePoweredOn = 5

# CBCentralManager option keys
CBCentralManagerScanOptionAllowDuplicatesKey = u"kCBScanOptionAllowDuplicates"
CBConnectPeripheralOptionNotifyOnDisconnectionKey = u"kCBConnectOptionNotifyOnDisconnection"

# CBCharacteristicWriteType CONSTS
CBCharacteristicWriteWithResponse = 0
CBCharacteristicWriteWithoutResponse = 1


# CBPeripheralManager states CONSTS from CBPeripheralManager.h
CBPeripheralManagerStateUnknown = 0
CBPeripheralManagerStateResetting = 1
CBPeripheralManagerStateUnsupported = 2
CBPeripheralManagerStateUnauthorized = 3
CBPeripheralManagerStatePoweredOff = 4
CBPeripheralManagerStatePoweredOn = 5

# CBCharacteristicWriteType CONSTS
CBCharacteristicWriteWithResponse = 0
CBCharacteristicWriteWithoutResponse = 1


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
CBCharacteristicPropertyNotifyEncryptionRequired                                = 0x100
CBCharacteristicPropertyIndicateEncryptionRequired                              = 0x200

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
DEVICE_INFO_SERVICE = '180A'
SYSTEM_ID_CHAR = '2A23'
AUTHENTICATION_SERVICE = '7760'
AUTHENTICATION_CHAR = '7761'

GATEWAY_AUTHENTICATION_TOKEN = '123456'

GATEWAY_RECONNECT_WAIT_INTERVAL = 5 # UNIT: SECOND
GATEWAY_UPDATE2CENTRAL_INTERVAL = 10 # UNIT: SECOND
