'''
This gateway serves as bridge between rimware and sensors.
It serves to get the BLE profile hierarchy from the sensor
and extract information of characteristics including
properties, description in descriptors, special services
(security, authentication).
Due to the current Apple's BLE implementation, peripheral
cannot detect disconnection event, peripheral reset 
security and authentication after a certain idle time 
(e.g. 1 seconds) determined by peripheral. So to keep
an active session without re-initializing security
and authentication checking gateway should send periodic
request to peripheral with an interval which is less
than the interval set on peripheral
'''