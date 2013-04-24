'''
Created on Feb 9, 2013

@author: cjhuo
'''
# setup for ecoBT webEngine
webGUIPort = 8000
isWriteToLog = True # True to have std output write to log.txt
frequency = 250

# detecting self's IP address
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    s.connect(("gmail.com",80))
    ipAddr = s.getsockname()[0]
except:
    ipAddr = 'localhost' # no internet access available
s.close()
# addresses where live pages are going to fetch data from
#'ws://cps.eng.uci.edu:8000/socket' 
plotServerAddr = 'ws://' + ipAddr + ':8000/fakeSocket' 
orientationServerAddr = 'ws://' + ipAddr + ':8000/socket' 
temperatureServerAddr = 'ws://' + ipAddr + ':8000/socket' 
administrationServerAddr = 'ws://' + ipAddr + ':8000/socket' 
LiveECGServerAddr = 'ws://' + ipAddr + ':8000/socket'
LiveSIDsServerAddr = 'ws://' + ipAddr + ':8000/socket'

# setup for ecoBT host
# turn off keyboard interrupt detection for server mode in order not to get too many 'Enter' signal..
enableKeyboardInterrupt = True