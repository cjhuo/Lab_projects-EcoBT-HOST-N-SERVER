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

# Profile Identifier List
ProfileList = [
# Service Profile
"180D",             # EcoBT Profile
"180A",             # "180A" Generic Access Profile
"FF10",             # LED Profile
"FFA0",             # ACC Profile
"FE10",             # SIDS SHT25 Profile
"FF20",             # RTC Profile,
"FEC0",             # ECG Profile
# Characteristic Profile
"2A23",             # Device Info Characteristic Profile
"FE11",             # SIDs CO2 STATUS Characteristic Profile
"FE12",             # SIDs CO2 PARAM Characteristic Profile, default 10
"FE13",             # SIDs CO2 READING Characteristic Profile , default 0
"FE14",             # Temperature Characteristic Profile
"FE15",             # Humidity Characteristic Profile
"FF11",             # LED 0 Enable Characteristic Profile
"FF12",             # LED 1 Enable Characteristic Profile
"FF13",             # LED 0 Blink Characteristic Profile
"FF14",             # LED 1 Blink Characteristic Profile
"FFA1",             # ACC Enable Characteristic Profile
#"FFA2",             # ACC Range Selection Characteristic Profile
#"FFA3",             # ACC X Characteristic Profile
#"FFA4",             # ACC Y Characteristic Profile
#"FFA5",             # ACC Z Characteristic Profile
"FFA6",             # ACC XYZ Characteristic Profile
"FF21",             # RTC Set Time Characteristic Profile
"FF22",              # RTC Get Time Characteristic Profile
#"FEC1",              # ECG characteristic info
"FEC2",              # ECG characteristic status
#"FEC3",              # ECG characteristic config 1
#"FEC4",              # ECG characteristic config 2
"FEC5",              # ECG characteristic start flag
"FEC6",              # ECG characteristic first 6 channels
"FEC7",              # ECG characteristic second 6 channels
#"FEC8"              # ECG characteristic
]



