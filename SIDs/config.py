'''
Created on Feb 9, 2013

@author: cjhuo
'''
# setup for ecoBT webEngine
webGUIPort = 8000
isWriteToLog = False # True to have std output write to log.txt

# addresses where live pages are going to fetch data from
#'ws://cps.eng.uci.edu:8000/socket' 
plotServerAddr = 'ws://localhost:8000/socket' 
orientationServerAddr = 'ws://localhost:8000/socket' 
temperatureServerAddr = 'ws://localhost:8000/socket' 
administrationServerAddr = 'ws://localhost:8001/socket' 
LiveECGServerAddr = 'ws://localhost:8001/socket'
LiveSIDsServerAddr = 'ws://localhost:8001/socket'

# setup for ecoBT host
# turn off keyboard interrupt detection for server mode in order not to get too many 'Enter' signal..
enableKeyboardInterrupt = False 
hostPort = 8001