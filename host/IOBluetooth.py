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

# descriptor type UUID, only 0x2901 and 0x2904 can be created for current apple implementation
CBUUIDCharacteristicExtendedPropertiesString = u'2900'
CBUUIDCharacteristicUserDescriptionString = u'2901'
CBUUIDClientCharacteristicConfigurationString = u'2902'
CBUUIDServerCharacteristicConfigurationString = u'2903'
CBUUIDCharacteristicFormatString = u'2904'
CBUUIDCharacteristicAggregateFormatString = u'2905'

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
"FEC0": '',             # ECG Profile,
"7780": '',             # test Profile
'7770': '',             # Security
'7760': '',             # Authentication
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
'7771': 'SecurityType',
'7772': 'SecurityKey',
'7773': 'SecurityIV',
'7781': 'TestCharacteristic',
'7761': 'Authentication'
}



