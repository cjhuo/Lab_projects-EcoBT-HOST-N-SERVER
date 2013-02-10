'''
Created on Feb 9, 2013

@author: cjhuo
'''

webGUIPort = 8000
isWriteToLog = False # True to have std output write to log.txt

# addresses where live pages are going to fetch data from
plotServerAddr = 'ws://cps.eng.uci.edu:8000/socket' 
orientationServerAddr = 'ws://localhost:8001/socket'
temperatureServerAddr = 'ws://cps.eng.uci.edu:8001/socket'