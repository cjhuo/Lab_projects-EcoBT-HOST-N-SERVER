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

