'''
Created on Feb 9, 2013

@author: cjhuo
'''
import tornado.web
import tornado.gen
from tornado.ioloop import IOLoop
import sys
import os.path
import json
import os
import subprocess
from datetime import datetime
import threading
import multiprocessing
from functools import partial

from config import *
from BaseHandler import BaseHandler
from ecg.ECG_reader import ECG_reader

DATA_PATH = "./data"
UPLOAD_PATH = "Uploads/"
ARRAY_LENGTH_WITH_NO_COMPRESSION_NEED = 2500 # if sample count is greater than this number, start compression
#fake the labels for each channels for demo purpose, 
#eventually label information should be passed from ecg module
ECG_CHANNELLABELS = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']


'''
Handler for ecg viewing page
'''
class ECGAllInOneHandler(BaseHandler):
    def initialize(self, ecgList):
        if not self.get_secure_cookie('PYCKET_ID'):
            self.redirect("/")
        else:
            print 'Session ID: ', self.get_secure_cookie('PYCKET_ID')
        sId = self.get_secure_cookie('PYCKET_ID')
        if not ecgList.has_key(sId):
            ecgList[sId] = dict()
        if not ecgList[sId].has_key('ecg'):
            ecgList[sId]['ecg'] = ECG_reader()
        self.ecg = ecgList[sId]['ecg']
        '''
        if not self.session.get('ecgAll'):
            print 'Initializing ECG_reader'
            self.session.set('ecgAll', ECG_reader())   
        self.ecg = self.session.get('ecgAll')
        '''
        #self.ecg = ecg
        
    def get(self): # asynchronous loading handler    
        minVal = self.get_argument("min", default=None)       
        maxVal = self.get_argument("max", default=None)
        wavech = []
        if minVal != None and maxVal !=None:
            minVal = int(minVal)
            maxVal = int(maxVal)
            for i in range(len(self.ecg.wavech)):
                wavech.append([self.ecg.wavech[i][j] for j in range(minVal, maxVal)])
            if len(wavech[0]) > ARRAY_LENGTH_WITH_NO_COMPRESSION_NEED: # compress it
                print >> sys.stderr, 'TOO MANY SAMPLES, CAN\'T DRAW DIRECTLY, START COMPRESSING'
                dataSetsCompression(wavech, wavech, ARRAY_LENGTH_WITH_NO_COMPRESSION_NEED)
                print >> sys.stderr, 'COMPRESSION COMPLETE, SENDING COMPRESSED DATA FOR DRAWING' 
            pointInterval = (1000/frequency) * int(round(float(len(self.ecg.wavech[0]))/float(ARRAY_LENGTH_WITH_NO_COMPRESSION_NEED)))
        else: # plot along the entire time period      
            # interval is 8, frequency 125, draw 5 samples in every small block(4px)
            # original frequency / lowered frequency === integer 
            sampleCountToBeSent = int(len(self.ecg.wavech[0]) / 2) # set to 1 to disable down sampling
            print >> sys.stderr, 'TOO MANY SAMPLES, CAN\'T DRAW DIRECTLY, START COMPRESSING'
            dataSetsCompression(self.ecg.wavech, wavech, sampleCountToBeSent)
            print >> sys.stderr, 'COMPRESSION COMPLETE, SENDING COMPRESSED DATA FOR DRAWING'  
            pointInterval = int((1000/frequency) * float(len(self.ecg.wavech[0]))/float(sampleCountToBeSent))

        print 'pointInterval: ', pointInterval
        datasets = []
        for i in range(len(wavech)):
            data = wavech[i]
            label = ECG_CHANNELLABELS[i]            
            datasets.append(dict())
            datasets[i]['data'] = data 
            datasets[i]['label'] = label
            datasets[i]['min'] = min(data)
            datasets[i]['max'] = max(data)
        
        self.write({
                    'data': datasets,
                    'pointInterval': pointInterval
                    })

    @tornado.web.asynchronous
    def put(self):
        options = self.get_argument("data")
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        jsonFile = 'options_' + timestamp + '.json'
        with open(os.path.join(self.settings['static_path'], UPLOAD_PATH, jsonFile), 'w') as outfile:
            outfile.write(options)
        
        t = threading.Thread(target=self.generateSVG, args=(jsonFile,))
        t.setDaemon(True)
        t.start()

            
    def generateSVG(self, jsonFile):
        convertTool = os.path.join(self.settings['static_path'], 'lib/highstock/highcharts-convert.js')
        callback = os.path.join(self.settings['static_path'], 'lib/highstock/callback.js')
        jsonFile = os.path.join(self.settings['static_path'], UPLOAD_PATH, jsonFile)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        returnPath = UPLOAD_PATH + 'svg/chart_'+ timestamp +'.png'
        svgFile = os.path.join(self.settings['static_path'], returnPath)
        command = "/usr/local/bin/phantomjs %s -infile %s -outfile %s -scale 1 -constr StockChart" % (convertTool, jsonFile, svgFile)
        rcode = subprocess.call(command, shell=True)
        print rcode
        if rcode == 0:
            self.write({'url': returnPath})
            self.finish()
        else:
            self.write({'message': 'file generation failed!'})
            self.finish()        
        
    @tornado.web.asynchronous         
    def post(self):
        try:         
            '''       
                using thread for concurrency (preventing blocking other request IO)
            '''
            t = threading.Thread(target=self.handleUpload)
            t.setDaemon(True)
            t.start()
        except:
            self.send_error(302) # 302: invalid file
            
    def handleUpload(self):
        def _callback(val):
            self.write(val)
            self.finish()   
        def _getDataFromDicomFile():
            wavech = self.ecg.wavech
            
            #create dataset dict to be sent to web server and fill in data
            datasets = []
            pointInterval = 1000/frequency
            if len(wavech[0]) > ARRAY_LENGTH_WITH_NO_COMPRESSION_NEED:
                print >> sys.stderr, 'TOO MANY SAMPLES, CAN\'T DRAW DIRECTLY, START COMPRESSING'
                base = []
                dataSetsCompression(wavech, base, ARRAY_LENGTH_WITH_NO_COMPRESSION_NEED)
                #base = compressList(ARRAY_LENGTH_WITH_NO_COMPRESSION_NEED, wavech[0])
                print >> sys.stderr, 'COMPRESSION COMPLETE, SENDING COMPRESSED DATA FOR DRAWING'
                pointInterval = (1000/frequency) * int(round(float(len(wavech[0]))/float(ARRAY_LENGTH_WITH_NO_COMPRESSION_NEED)))
                tmpWavech = []
                for i in range(len(wavech)):
                    tmpWavech.append([wavech[i][j] for j in range(ARRAY_LENGTH_WITH_NO_COMPRESSION_NEED)]) # only pick the first 2500 samples for the first time
                wavech = tmpWavech
            else:
                base = wavech
            
            for i in range(len(wavech)):
                data = wavech[i]
                label = ECG_CHANNELLABELS[i]            
                datasets.append(dict())
                datasets[i]['data'] = data 
                datasets[i]['label'] = label
                datasets[i]['min'] = min(data)
                datasets[i]['max'] = max(data)
                
            print 'pointInterval: ', pointInterval
            val = {
                   'dspData': datasets, 
                   'pointInterval': pointInterval, 
                   'base': base
                   }
            return val       
        if len(self.request.files) != 0: #user uploaded file from UI 
            f = self.request.files['uploaded_files'][0]
            orig_fname = f['filename']
            filePath = checkFileExistInPath(self.settings['static_path'], orig_fname, f['body'])            
        elif self.get_argument("filename", default=None):
            filePath = os.path.join(DATA_PATH, self.get_argument("filename", default=None))
        else: #user user the default test file
            filePath = None
        
        print >> sys.stderr, 'START READING ECG DATA IN ECG MODULE..'
        if filePath is not None:
            self.ecg.setFile(filePath)
        else:
            self.ecg.setFile()
        print >> sys.stderr, 'FINISH READING ECG DATA IN ECG MODULE..' 
        
        val = _getDataFromDicomFile()
        IOLoop.instance().add_callback(lambda: _callback(val))

'''
Handler for getting existing dicom files
'''
class DicomListHandler(BaseHandler):
    def get(self):
        fList = []
        for fname in os.listdir(DATA_PATH):
            prefix, suffix = fname.split(".")
            if suffix == 'dcm':
                fList.append(fname)
        self.write({'fileList': fList})

'''
Handler for analysis page
'''
class ECGHandler(BaseHandler):
    def initialize(self, ecgList):
        if not self.get_secure_cookie('PYCKET_ID'):
            self.redirect("/")
        else:
            print 'Session ID: ', self.get_secure_cookie('PYCKET_ID')        
        sId = self.get_secure_cookie('PYCKET_ID')
        if not ecgList.has_key(sId):
            ecgList[sId] = dict()
        if not ecgList[sId].has_key('ecg'):
            ecgList[sId]['ecg'] = ECG_reader()
        self.ecg = ecgList[sId]['ecg']
        
    @tornado.web.asynchronous         
    def post(self):
        try:  
            '''       
                using thread for concurrency (preventing blocking other request IO)
            '''
            t = threading.Thread(target=self.handleUpload) 
            t.setDaemon(True)
            t.start()
        except:
            self.send_error(302) # 302: invalid file
            
    def handleUpload(self):
        def _callback(val):
            self.write(val)
            self.finish() 
               
        '''           
        The datasets dict should have the structure as below:
        datasets = [
                        {
                            label: "channel",
                            #data: [array of [x, y]]
                            data: [array of y]
                        },
                        {
                            label: "channel2",
                            #data: [array of [x, y]]
                            data: [array of y]
                        },
                    ]
        '''
        def _getDataFromDicomFile():
            wavech = self.ecg.getTestData()
            
            #create dataset dict to be sent to web server and fill in data
            datasets = []
            for i in range(len(wavech)):
                data = wavech[i] #[wavech[i][j] for j in range(len(wavech[i]))]
                label = ECG_CHANNELLABELS[i]            
                #label = "channel " + str(i)
                datasets.append(dict())
                datasets[i]['data'] = data 
                datasets[i]['label'] = label
                datasets[i]['min'] = min(data)
                datasets[i]['max'] = max(data)            
                
            val = {'dspData': datasets}
            #print val
            return val
        if len(self.request.files) != 0: #user uploaded file from UI 
            f = self.request.files['uploaded_files'][0]
            orig_fname = f['filename']
            filePath = checkFileExistInPath(self.settings['static_path'], orig_fname, f['body'])            
        elif self.get_argument("filename", default=None):    
            filePath = os.path.join(DATA_PATH, self.get_argument("filename", default=None))
        else: #user user the default test file
            filePath = None
        
        print >> sys.stderr, 'START READING ECG DATA IN ECG MODULE..'
        if filePath is not None:
            self.ecg.setFile(filePath)
        else:
            self.ecg.setFile()
        print >> sys.stderr, 'FINISH READING ECG DATA IN ECG MODULE..' 
        
        val = _getDataFromDicomFile()
        IOLoop.instance().add_callback(lambda: _callback(val))

    def get(self): 
        data = json.loads(self.get_argument("data"))
        correlationVal = float(data.get('correlation'))/100

        print data

        try:
            #format of getBinInfo(): [[min, max, value],[min,max,value],...]
            bins, info = self.ecg.getBinInfo(data['qPoint'][0], data['tPoint'][0], data['bin'], data['lead'], correlationVal);
            
            print bins, info
            self.write({
                        'data': bins,
                        'info': info
                        #'info': [an array of additional information]
                        }) #format of bins json: {'data': bins info}
        except Exception as e:
            print e
            self.send_error(302)

'''
Utilities methods
'''
def compressList(outputLength, inputList):
    outputList = []
    step = int(len(inputList)/outputLength)    
    for i in range(outputLength):
        tmpSum = 0
        tmpLen = 0
        for j in range(i*step, (i+1)*step):
            if j >= len(inputList): # hit the end of the list
                break
            else:
                tmpSum += inputList[j]
                tmpLen += 1
        outputList.append(int(tmpSum/tmpLen))
    return outputList
                    
def dataSetsCompression(wavech, output, arrayLength): # compress data into length of arrayLength by averaging
    ''' multi-threaded way of doing compression
    paralFunc = partial(compressList, arrayLength)
    tmpList = multiprocessing.pool.Pool().map(paralFunc, wavech)
    for l in tmpList:
        output.append(l)
    '''
    import copy
    wavechTmp = copy.deepcopy(wavech) #clone input list first
    del output[:] #clear output list
    for data in wavechTmp:
        tmpList = []
        tmpList = compressList(arrayLength, data)
        output.append(tmpList)
    
            
def checkFileExistInPath(pathName, fileName, fileContent):
    # search locally by the filename, if existed, use it instead of uploading
    path1 = os.path.join(pathName, UPLOAD_PATH)
    path2 = os.path.join(pathName, os.pardir, os.pardir, 'data')
    
    path = None
    ''' checking if file exists in different predefined locations
    if os.path.exists(os.path.join(path1,fileName)):
        path = path1
    elif os.path.exists(os.path.join(path2,fileName)):
        path = path2
    '''
    
    if path == None:
        path = os.path.join(pathName, UPLOAD_PATH)
        ofd = open(path + fileName, 'w')
        ofd.write(fileContent)
        ofd.close()
        print >> sys.stderr, 'FILE UPLOADED, OPENING'
    else:
        print >> sys.stderr, 'FILE EXISTS, OPENING DIRECTLY'
    return os.path.join(path, fileName)


if __name__ == "__main__":
    print ECGHandler().handleUpload()