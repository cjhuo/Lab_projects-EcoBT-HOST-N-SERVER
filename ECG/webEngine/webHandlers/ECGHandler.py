'''
Created on Feb 9, 2013

@author: cjhuo
'''
import tornado.web
import sys
import os.path
import json
import os
import subprocess
from datetime import datetime
import threading

from config import *
from BaseHandler import BaseHandler
from ecg.ECG_reader import ECG_reader

uploadPath = "Uploads/"
arrayLength = 2500 # if sample count is greater than this number, start compression
#fake the labels for each channels for demo purpose, 
#eventually label information should be passed from ecg module
ECG_CHANNELLABELS = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']

class ECGAllInOneHandler(BaseHandler):
    def initialize(self, ecg):
        self.ecg = ecg
        
    def get(self): # asynchronous loading handler    
        minVal = self.get_argument("min", default=None)       
        maxVal = self.get_argument("max", default=None)
        wavech = []
        if minVal != None and maxVal !=None:
            minVal = int(minVal)
            maxVal = int(maxVal)
            for i in range(len(self.ecg.wavech)):
                wavech.append([self.ecg.wavech[i][j] for j in range(minVal, maxVal)])
            if len(wavech[0]) > arrayLength: # compress it
                print >> sys.stderr, 'TOO MANY SAMPLES, CAN\'T DRAW DIRECTLY, START COMPRESSING'
                self.dataSetsCompression(wavech, wavech, arrayLength)
                print >> sys.stderr, 'COMPRESSION COMPLETE, SENDING COMPRESSED DATA FOR DRAWING' 
            pointInterval = (1000/frequency) * int(round(float(len(self.ecg.wavech[0]))/float(arrayLength)))

        else: # plot along the entire time period
            sampleCountToBeSent = len(self.ecg.wavech[0]) / 4 # interval is 16, draw 3 samples in every small block
            if len(self.ecg.wavech[0]) > sampleCountToBeSent: # compress it
                print >> sys.stderr, 'TOO MANY SAMPLES, CAN\'T DRAW DIRECTLY, START COMPRESSING'
                self.dataSetsCompression(self.ecg.wavech, wavech, sampleCountToBeSent)
                print >> sys.stderr, 'COMPRESSION COMPLETE, SENDING COMPRESSED DATA FOR DRAWING'   
            else: 
                sampleCountToBeSent = len(self.ecg.wavech[0])
                wavech = self.ecg.wavech                    
            pointInterval = (1000/frequency) * int(round(float(len(self.ecg.wavech[0]))/float(sampleCountToBeSent)))

        print 'pointInterval: ', pointInterval
        datasets = []
        for i in range(len(wavech)):
            #data = wavech[i] #[wavech[i][j] for j in range(len(wavech[i]))]
            data = wavech[i]
            label = ECG_CHANNELLABELS[i]            
            #label = "channel " + str(i)
            datasets.append(dict())
            datasets[i]['data'] = data 
            #print len(data)
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

        with open(os.path.join(self.settings['static_path'], uploadPath, 'options.json'), 'w') as outfile:
            outfile.write(options)
        
        t = threading.Thread(target=self.generateSVG)
        t.start()

            
    def generateSVG(self):
        convertTool = os.path.join(self.settings['static_path'], 'lib/highstock/highcharts-convert.js')
        jsonFile = os.path.join(self.settings['static_path'], uploadPath, 'options.json')
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        svgFile = os.path.join(self.settings['static_path'], uploadPath, 'svg/chart_'+ timestamp +'.svg')
        command = "/usr/local/bin/phantomjs %s -infile %s -outfile %s -constr StockChart" % (convertTool, jsonFile, svgFile)
        rcode = subprocess.call(command, shell=True)
        print rcode
        if rcode == 0:
            #os.system('open "%s"' % os.path.dirname(svgFile))
            self.write({'url': self.static_url(svgFile)})
            self.finish()
        else:
            self.write({'message': 'file generation failed!'})
            self.finish()        
        
            
    def post(self): # file upload handler
        try:
            if len(self.request.files) != 0: #user uploaded file from UI 
                f = self.request.files['uploaded_files'][0]
                orig_fname = f['filename']
                filePath = checkFileExistInPath(self.settings['static_path'], orig_fname, f['body'])
                
                print >> sys.stderr, 'START READING ECG DATA IN ECG MODULE..'
                self.ecg.setFile(filePath)              
                print >> sys.stderr, 'FINISH READING ECG DATA IN ECG MODULE..' 
            else: #user user the default test file
                print >> sys.stderr, 'START READING ECG DATA IN ECG MODULE..'
                self.ecg.setFile()               
                print >> sys.stderr, 'FINISH READING ECG DATA IN ECG MODULE..' 
            val = self.getDataFromDicomFile()
            self.write(val)
        except:
            self.send_error(302) # 302: invalid file
            
    def getDataFromDicomFile(self):
        #wavech, peaks = ecg.ECG_reader.getTestData()
        wavech = self.ecg.wavech
        
        #create dataset dict to be sent to web server and fill in data
        datasets = []
        pointInterval = 1000/frequency
        if len(wavech[0]) > arrayLength:
            print >> sys.stderr, 'TOO MANY SAMPLES, CAN\'T DRAW DIRECTLY, START COMPRESSING'
            
            #base = self.dataSetsCompression(wavech, arrayLength)
            base = []
            self.compressList(wavech[0], base, arrayLength)
            print >> sys.stderr, 'COMPRESSION COMPLETE, SENDING COMPRESSED DATA FOR DRAWING'
            pointInterval = (1000/frequency) * int(round(float(len(wavech[0]))/float(arrayLength)))
            tmpWavech = []
            for i in range(len(wavech)):
                tmpWavech.append([wavech[i][j] for j in range(arrayLength)]) # only pick the first 2500 samples for the first time
            wavech = tmpWavech
        else:
            base = wavech[0]

        for i in range(len(wavech)):
            #data = wavech[i] #[wavech[i][j] for j in range(len(wavech[i]))]
            data = wavech[i]
            label = ECG_CHANNELLABELS[i]            
            #label = "channel " + str(i)
            datasets.append(dict())
            datasets[i]['data'] = data 
            #print len(data)
            datasets[i]['label'] = label
            datasets[i]['min'] = min(data)
            datasets[i]['max'] = max(data)
            #print min(data), data.index(min(data))
            
        #add peak information to structure to be sent to frontend
        # format of peaks: "peaks": [index of 1st peak, index of 2nd peak, ...]

        print 'pointInterval: ', pointInterval
        val = {
               'dspData': datasets, 
               'pointInterval': pointInterval, 
               'base': base
               }
        return val       
    
    def compressList(self, inputList, outputList, outputLength):
        step = int(len(inputList)/outputLength)     
        for i in range(outputLength):
            tmpSum = 0
            tmpLen = 0
            for j in range(i*step, (i+1)*step):
                if j == len(inputList): # hit the end of the list
                    break
                else:
                    tmpSum += inputList[j]
                    tmpLen += 1
            outputList.append(tmpSum/tmpLen)
            
        
    def dataSetsCompression(self, wavech, output, arrayLength): # compress data into length of arrayLength by averaging
        for data in wavech:
            tmpList = []
            self.compressList(data, tmpList, arrayLength)
            output.append(tmpList)
            
def checkFileExistInPath(pathName, fileName, fileContent):
    # search locally by the filename, if existed, use it instead of uploading
    path1 = os.path.join(pathName, uploadPath)
    path2 = os.path.join(pathName, os.pardir, os.pardir, 'data')
    
    path = None
    if os.path.exists(os.path.join(path1,fileName)):
        path = path1
    elif os.path.exists(os.path.join(path2,fileName)):
        path = path2
    
    if path == None:
        path = os.path.join(pathName, uploadPath)
        ofd = open(path + fileName, 'w')
        ofd.write(fileContent)
        ofd.close()
        print >> sys.stderr, 'FILE UPLOADED, OPENING'
    else:
        print >> sys.stderr, 'FILE EXISTS, OPENING DIRECTLY'
    return path + fileName
  
class ECGHandler(BaseHandler):
    def initialize(self, ecg):
        self.ecg = ecg
    
    def post(self):
        try:
            if len(self.request.files) != 0: #user uploaded file from UI 
                f = self.request.files['uploaded_files'][0]
                orig_fname = f['filename']
                filePath = checkFileExistInPath(self.settings['static_path'], orig_fname, f['body'])
                
                print >> sys.stderr, 'START READING ECG DATA IN ECG MODULE..'
                self.ecg.setFile(filePath)              
                print >> sys.stderr, 'FINISH READING ECG DATA IN ECG MODULE..' 
            else: #user user the default test file
                print >> sys.stderr, 'START READING ECG DATA IN ECG MODULE..'
                self.ecg.setFile()               
                print >> sys.stderr, 'FINISH READING ECG DATA IN ECG MODULE..' 
            val = self.getDataFromDicomFile()
            self.write(val)
        except:
            self.send_error(302) # 302: invalid file
            
    def get(self): 
        data = json.loads(self.get_argument("data"))
        print data
        
        #format of getBinInfo(): [[min, max, value],[min,max,value],...]
        bins, info = self.ecg.getBinInfo(data['qPoint'][0], data['tPoint'][0], data['bin'], data['lead']);
        
        print bins, info
        self.write({
                    'data': bins,
                    'info': info
                    #'info': [an array of additional information]
                    }) #format of bins json: {'data': bins info}
              
            
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
    def getDataFromDicomFile(self):
        #wavech, peaks = ecg.ECG_reader.getTestData()
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
            
        #add peak information to structure to be sent to frontend
        # format of peaks: "peaks": [index of 1st peak, index of 2nd peak, ...]

        val = {'dspData': datasets}
        #print val
        return val

    '''    
    def get(self):        
        #val = self.fakeData()  #should be replaced by ecg dsp data generation module
        f = self.get_argument("file")      
#        print f
        self.ecg.setFile(f)
        val = self.getDataFromDicomFile()
        self.write(val)
    '''  

''' 
class DSPHandler(BaseHandler):
    def initialize(self, ecg):
        self.ecg = ecg
             
    def post(self): 
        data = json.loads(self.get_argument("data"))
        print data
        
        #format of getBinInfo(): [[min, max, value],[min,max,value],...]
        bins = self.ecg.getBinInfo(data['qPoint'][0], data['tPoint'][0], data['bin']);
        
        print bins
        self.write({'data': bins}) #format of bins json: {'data': bins info}
          
    
    def get(self):        
        val = self.fakeData()  #should be replaced by ecg dsp data generation module
        print val
        self.write({'dspData': val})   
    
    #generate data for n channels with 100 data each, ranged from (-100, 100)
    def fakeData(self, n=2):
        datasets = dict()
        for i in range(n):
            #data = [[j, random.randint(-100, 100)] for j in range(100)]  
            data = [random.randint(-100, 100) for j in range(100)]           
            #label = "channel " + str(i)
            label = ECG_CHANNELLABELS[i]
            #print label
            datasets[i] = dict()
            datasets[i]['data'] = data 
            datasets[i]['label'] = label
        return datasets
'''  

if __name__ == "__main__":
    print DSPHandler().getDataFromDicomFile()
       