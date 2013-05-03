//
//  ECGMainViewController.m
//  ECGApp
//
//  Created by CJ Huo on 3/7/13.
//  Copyright (c) 2013 CJ Huo. All rights reserved.
//

#import "ECGMainViewController.h"
#import <CoreBluetooth/CoreBluetooth.h>

#import "TransferService.h"

@interface ECGMainViewController () <CBCentralManagerDelegate, CBPeripheralDelegate, UITextViewDelegate, ZBarReaderDelegate>

@property (strong, nonatomic) IBOutlet UITextView       *textView;
@property (strong, nonatomic) IBOutlet UILabel       *label;
@property (strong, nonatomic) IBOutlet UINavigationItem *navItem;
@property (strong, nonatomic) IBOutlet UIImageView       *imageView;
@property (strong, nonatomic) IBOutlet UIButton       *imageButton;
@property (strong, nonatomic) IBOutlet UISwitch         *advertisingSwitch;
@property (strong, nonatomic) CBCentralManager      *centralManager;
@property (strong, nonatomic) CBPeripheral          *discoveredPeripheral;
@property (strong, nonatomic) NSMutableData         *data;
@property (strong, nonatomic) NSString         *macAddr;
@property (strong, nonatomic) CBCharacteristic         *ecgCharac;
@property (strong, nonatomic) CBPeripheral         *ecgPeriph;
- (IBAction)switchChanged:(id)sender;
- (IBAction)startButtonClicked:(id)sender;
@end

@implementation ECGMainViewController

/*
- (id)initWithNibName:(NSString *)nibNameOrNil bundle:(NSBundle *)nibBundleOrNil
{
    self = [super initWithNibName:nibNameOrNil bundle:nibBundleOrNil];
    if (self) {
        // Custom initialization
    }
    return self;
}
*/
- (void)viewDidLoad
{
    [super viewDidLoad];
	// Do any additional setup after loading the view.
    _centralManager = [[CBCentralManager alloc] initWithDelegate:self queue:nil];
    
    // And somewhere to store the incoming data
    _data = [[NSMutableData alloc] init];
    
    _macAddr = [[NSString alloc] init];
    
    NSMutableArray * imageArray = [[NSMutableArray alloc] init];
    for(int i=1; i < 44; i++) {
        [imageArray addObject:[UIImage imageNamed:[NSString stringWithFormat:@"thumb_208 %02d.png", i]]];
    }
    self.imageView.animationImages = imageArray;
    self.imageView.animationDuration = 1.1;
    //self.imageView.contentMode = UIViewContentModeBottomLeft;
    
}

- (void)viewWillDisappear:(BOOL)animated
{
    // Don't keep it going while we're not showing.
    [self stopScan];
    [super viewWillDisappear:animated];
}

- (void)didReceiveMemoryWarning
{
    [super didReceiveMemoryWarning];
    // Dispose of any resources that can be recreated.
}

#pragma mark - Central Methods



/** centralManagerDidUpdateState is a required protocol method.
 *  Usually, you'd check for other states to make sure the current device supports LE, is powered on, etc.
 *  In this instance, we're just using it to wait for CBCentralManagerStatePoweredOn, which indicates
 *  the Central is ready to be used.
 */
- (void)centralManagerDidUpdateState:(CBCentralManager *)central
{
    NSString * state = nil;
    
    switch ([central state])
    {
        case CBCentralManagerStateUnsupported:
            state = @"The platform/hardware doesn't support Bluetooth Low Energy.";
            NSLog(@"Central manager state: %@", state);
            return;
        case CBCentralManagerStateUnauthorized:
            state = @"The app is not authorized to use Bluetooth Low Energy.";
            NSLog(@"Central manager state: %@", state);
            return;
        case CBCentralManagerStatePoweredOff:
            state = @"Bluetooth is currently powered off.";
            NSLog(@"Central manager state: %@", state);
            return;
        case CBCentralManagerStatePoweredOn:
            state = @"Bluetooth is ready.";
            NSLog(@"Central manager state: %@", state);
            return;
        case CBCentralManagerStateUnknown:
        default:
            return;
            
    }
    
    // The state must be CBCentralManagerStatePoweredOn...
    
    // ... so start scanning
    //[self scan];
    
}


/** Scan for peripherals - specifically for our service's 128bit CBUUID
 */
- (void)scan
{   
    [self.centralManager scanForPeripheralsWithServices:@[[CBUUID UUIDWithString:ADVERTISE_SERVICE_UUID]] options:@{ CBCentralManagerScanOptionAllowDuplicatesKey : @NO }];
    
    NSLog(@"Scanning started");
}

- (void)stopScan
{
    
    [self.centralManager stopScan];
    NSLog(@"Scanning stopped");

}

- (void)setText: (NSString *) string
{
    [self.textView setText:[self.textView.text stringByAppendingString:string]];
    [self.textView scrollRangeToVisible:NSMakeRange([self.textView.text length], 0)];
}

/** This callback comes whenever a peripheral that is advertising the TRANSFER_SERVICE_UUID is discovered.
 *  We check the RSSI, to make sure it's close enough that we're interested in it, and if it is,
 *  we start the connection process
 */
- (void)centralManager:(CBCentralManager *)central didDiscoverPeripheral:(CBPeripheral *)peripheral advertisementData:(NSDictionary *)advertisementData RSSI:(NSNumber *)RSSI
{
    /*
    // Reject any where the value is above reasonable range
    if (RSSI.integerValue > -15) {
        return;
    }
    
    // Reject if the signal strength is too low to be close enough (Close is around -22dB)
    if (RSSI.integerValue < -35) {
        return;
    }
    */
    
    
    
    // Ok, it's in range - have we already seen it?
    if (self.discoveredPeripheral != peripheral) {
        
        // Save a local copy of the peripheral, so CoreBluetooth doesn't get rid of it
        self.discoveredPeripheral = peripheral;
        NSLog(@"Discovered %@ at %@", peripheral.name, RSSI);
        [self setText:[[NSString alloc] initWithFormat:@"Discovered a nearby EcoBT with name: %@\n", peripheral.name]];
        // And connect
        NSLog(@"Connecting to peripheral %@", peripheral);
        [self setText:[[NSString alloc] initWithFormat:@"Connecting to the EcoBT\n"]];

        [self.centralManager connectPeripheral:peripheral options:nil];
    }
}


/** If the connection fails for whatever reason, we need to deal with it.
 */
- (void)centralManager:(CBCentralManager *)central didFailToConnectPeripheral:(CBPeripheral *)peripheral error:(NSError *)error
{
    NSLog(@"Failed to connect to %@. (%@)", peripheral, [error localizedDescription]);
    [self cleanup];
}


/** We've connected to the peripheral, now we need to discover the services and characteristics to find the 'transfer' characteristic.
 */
- (void)centralManager:(CBCentralManager *)central didConnectPeripheral:(CBPeripheral *)peripheral
{
    NSLog(@"Peripheral Connected %@", peripheral);
    [self setText:[[NSString alloc] initWithFormat:@"EcoBT Node Connected\n"]];

    // Stop scanning
    //[self stopScan];
    
    // Clear the data that we may already have
    [self.data setLength:0];
    
    // Make sure we get the discovery callbacks
    //[peripheral setDelegate:self];
    
    peripheral.delegate = self;
    
    // Search only for services that match our UUID
    [peripheral discoverServices:nil];
    //[peripheral discoverServices:@[[CBUUID UUIDWithString:TRANSFER_SERVICE_UUID]]];

    NSLog(@"Discovering services");
    [self setText:[[NSString alloc] initWithFormat:@"Discovering services\n"]];

}


/** The Transfer Service was discovered
 */
- (void)peripheral:(CBPeripheral *)peripheral didDiscoverServices:(NSError *)error
{
    if (error) {
        NSLog(@"Error discovering services: %@", [error localizedDescription]);
        [self cleanup];
        return;
    }
    
    // Discover the characteristic we want...
    
    // Loop through the newly filled peripheral.services array, just in case there's more than one.
    for (CBService *service in peripheral.services) {
        NSLog(@"Service found with UUID: %@", service.UUID);
        
        if ([service.UUID isEqual:[CBUUID UUIDWithString:TRANSFER_SERVICE_UUID]] || [service.UUID isEqual:[CBUUID UUIDWithString:@"FEC0"]]) {
            [self setText:[[NSString alloc] initWithFormat:@"Service found with UUID: %@\n", service.UUID]];

            NSLog(@"Start discovering characteristics in service UUID: %@", service.UUID);
            [self setText:[[NSString alloc] initWithFormat:@"Start discovering characteristics in service UUID: %@\n", service.UUID]];

            [peripheral discoverCharacteristics:nil forService:service];
        }
        //[peripheral discoverCharacteristics:@[[CBUUID UUIDWithString:TRANSFER_CHARACTERISTIC_UUID]] forService:service];
    }
}


/** The Transfer characteristic was discovered.
 *  Once this has been found, we want to subscribe to it, which lets the peripheral know we want the data it contains
 */
- (void)peripheral:(CBPeripheral *)peripheral didDiscoverCharacteristicsForService:(CBService *)service error:(NSError *)error
{
    // Deal with errors (if any)
    if (error) {
        NSLog(@"Error discovering characteristics: %@", [error localizedDescription]);
        [self cleanup];
        return;
    }
    
    // Again, we loop through the array, just in case.
    for (CBCharacteristic *characteristic in service.characteristics) {
        
        // And check if it's the right one
        if ([characteristic.UUID isEqual:[CBUUID UUIDWithString:TRANSFER_CHARACTERISTIC_UUID]]) {
            [self setText:[[NSString alloc] initWithFormat:@"Discovered characteristics %@ in service %@\n", characteristic.UUID, service.UUID]];
            // If it is, subscribe to it
            //[peripheral setNotifyValue:YES forCharacteristic:characteristic];
            [peripheral readValueForCharacteristic:characteristic];
            NSLog(@"Reading value from characteristic with UUID: %@ in service with UUID: %@", characteristic.UUID, service.UUID);
            [self setText:[[NSString alloc] initWithFormat:@"Reading value from characteristic with UUID: %@ in service with UUID: %@\n", characteristic.UUID, service.UUID]];
        }
        
        if ([characteristic.UUID isEqual:[CBUUID UUIDWithString:@"FEC5"]]) {
            //store a local copy of connected device
            self.ecgCharac = characteristic;
            self.ecgPeriph = peripheral;
        }
        /*
        if ([characteristic.UUID isEqual:[CBUUID UUIDWithString:@"FE15"]]) {
            if ((characteristic.properties & CBCharacteristicPropertyRead) == CBCharacteristicPropertyRead)
                NSLog(@"Charateristic has propertie: %@", @"Read"); 
            if ((characteristic.properties & CBCharacteristicPropertyWrite) == CBCharacteristicPropertyWrite)
                NSLog(@"Charateristic has propertie: %@", @"Write");
            if ((characteristic.properties & CBCharacteristicPropertyNotify) == CBCharacteristicPropertyNotify)
                NSLog(@"Charateristic has propertie: %@", @"Notify");
        }
        */
    }
    
    // Once this is complete, we just need to wait for the data to come in.
}


/** This callback lets us know more data has arrived via notification on the characteristic
 */
- (void)peripheral:(CBPeripheral *)peripheral didUpdateValueForCharacteristic:(CBCharacteristic *)characteristic error:(NSError *)error
{
    if (error) {
        NSLog(@"Error discovering characteristics: %@", [error localizedDescription]);
        return;
    }
    
    NSData * updatedValue = characteristic.value;
    uint8_t* dataPointer = (uint8_t*)[updatedValue bytes];
    
    NSString *stringFromData = [NSString stringWithFormat:@"EcoBT Node's MAC Address:\n %02X-%02X-%02X-%02X-%02X-%02X", dataPointer[7], dataPointer[6], dataPointer[5], dataPointer[2], dataPointer[1], dataPointer[0]];
    NSLog(@"Device MAC Address = %@", stringFromData);
    [self setText:[[NSString alloc] initWithString:stringFromData]];
    //[self setText:[[NSString alloc] initWithFormat:@"\n\nIt worked!"]];
    if ([self.macAddr isEqualToString:[NSString stringWithFormat: @"%02X%02X%02X%02X%02X%02X", dataPointer[7], dataPointer[6], dataPointer[5], dataPointer[2], dataPointer[1], dataPointer[0]]]) {
        [self.imageButton setHidden:FALSE];
        [self stopScan];
        //[self.label setText:@"Connected"];
    }
    
    // Log it
    NSLog(@"Received: %@", stringFromData);
}


/** The peripheral letting us know whether our subscribe/unsubscribe happened or not
 */
- (void)peripheral:(CBPeripheral *)peripheral didUpdateNotificationStateForCharacteristic:(CBCharacteristic *)characteristic error:(NSError *)error
{
    if (error) {
        NSLog(@"Error changing notification state: %@", error.localizedDescription);
    }
    
    // Exit if it's not the transfer characteristic
    if (![characteristic.UUID isEqual:[CBUUID UUIDWithString:TRANSFER_CHARACTERISTIC_UUID]]) {
        return;
    }
    
    // Notification has started
    if (characteristic.isNotifying) {
        NSLog(@"Notification began on %@", characteristic);
    }
    
    // Notification has stopped
    else {
        // so disconnect from the peripheral
        NSLog(@"Notification stopped on %@.  Disconnecting", characteristic);
        [self.centralManager cancelPeripheralConnection:peripheral];
    }
}


/** Once the disconnection happens, we need to clean up our local copy of the peripheral
 */
- (void)centralManager:(CBCentralManager *)central didDisconnectPeripheral:(CBPeripheral *)peripheral error:(NSError *)error
{
    if (error) {
        NSLog(@"Error diconnecting peripheral: %@", [error localizedDescription]);
    }
    NSLog(@"Peripheral Disconnected");
    self.discoveredPeripheral = nil;
    
}


/** Call this when things either go wrong, or you're done with the connection.
 *  This cancels any subscriptions if there are any, or straight disconnects if not.
 *  (didUpdateNotificationStateForCharacteristic will cancel the connection if a subscription is involved)
 */
- (void)cleanup
{
    // Don't do anything if we're not connected
    if (!self.discoveredPeripheral.isConnected) {
        return;
    }
    
    // See if we are subscribed to a characteristic on the peripheral
    if (self.discoveredPeripheral.services != nil) {
        for (CBService *service in self.discoveredPeripheral.services) {
            if (service.characteristics != nil) {
                for (CBCharacteristic *characteristic in service.characteristics) {
                    if ([characteristic.UUID isEqual:[CBUUID UUIDWithString:TRANSFER_CHARACTERISTIC_UUID]]) {
                        if (characteristic.isNotifying) {
                            // It is notifying, so unsubscribe
                            [self.discoveredPeripheral setNotifyValue:NO forCharacteristic:characteristic];
                            
                            // And we're done.
                            return;
                        }
                    }
                }
            }
        }
    }
    
    // If we've got this far, we're connected, but we're not subscribed, so we just disconnect
    [self.centralManager cancelPeripheralConnection:self.discoveredPeripheral];
}

- (void) imagePickerController:(UIImagePickerController *)reader didFinishPickingMediaWithInfo:(NSDictionary *)info
{
    id<NSFastEnumeration> results = [info objectForKey:ZBarReaderControllerResults];
    ZBarSymbol *symbol = nil;
    for(symbol in results)
        break;
    /*
    self.resultText.text = @"";
    for(symbol in results)
    
    [self.resultText setText:[self.resultText.text stringByAppendingString:symbol.data]];
    //break;
     
    //resultText.text = symbol.data;
    resultImage.image = [info objectForKey:UIImagePickerControllerOriginalImage];
    */
    self.macAddr = symbol.data;
    [reader dismissModalViewControllerAnimated:YES];
    NSLog(@"Scanning Data: %@", symbol.data);
    [self setText:[[NSString alloc] initWithFormat:@"Scanning Data: %@\n", symbol.data]];
    // start scan nearby device
    [self scan];
    [self setText:[[NSString alloc] initWithFormat:@"Start Scanning...\n"]];

    
}


#pragma mark - Switch Methods


/** Start/stop scan when switch on/off
 */
- (IBAction)switchChanged:(id)sender
{
    
    if (self.advertisingSwitch.on) {
        ZBarReaderViewController *reader = [ZBarReaderViewController new];
        reader.readerDelegate = self;
        reader.supportedOrientationsMask = ZBarOrientationMaskAll;
        ZBarImageScanner *scanner = reader.scanner;
        
        [self presentModalViewController:reader animated:YES];
        /*
        // start scan nearby device
        [self scan];
        [self setText:[[NSString alloc] initWithFormat:@"Start Scanning...\n"]];
         */
    }
    
    else {
        [self stopScan];
        //[self.centralManager stopScan];
        
        //clean up
        [self cleanup];
        
        //clear Text field
        self.textView.text = @"";
        //[self.label setText:@"Scanning"];
        [self.imageButton setHidden:TRUE];
        if(self.imageButton.selected == TRUE){
            [self.imageButton setSelected:FALSE];
            [self.imageView stopAnimating];
        }
        //[self.textView setText:[self.textView.text stringByAppendingString:@"stop Scanning...\n"]];
    }
     
}

- (IBAction)startButtonClicked:(id)sender;
{
    if(self.imageButton.selected == FALSE){
        [self.imageButton setSelected:TRUE];
        [self.imageView startAnimating];
        
        //start Recording
        [self.ecgPeriph writeValue:[NSData dataWithBytes:(unsigned char[]){0x01} length:1] forCharacteristic:self.ecgCharac type:CBCharacteristicWriteWithResponse];
        /*
        UIImageView * ryuJump = [[UIImageView alloc] initWithFrame:CGRectMake(0, 0, 150, 130)];
        ryuJump.animationImages = imageArray;
        ryuJump.animationDuration = 1.1;
        ryuJump.contentMode = UIViewContentModeBottomLeft;
        [self.view addSubview:ryuJump];
        [ryuJump startAnimating];
         */
    }
    else if(self.imageButton.selected == true){
        
        //stop recording
        [self.ecgPeriph writeValue:[NSData dataWithBytes:(unsigned char[]){0x00} length:1] forCharacteristic:self.ecgCharac type:CBCharacteristicWriteWithResponse];
        
        [self.imageButton setSelected:FALSE];
        [self.imageView stopAnimating];
    }

}

@end
