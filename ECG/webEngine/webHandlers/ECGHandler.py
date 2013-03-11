'''
Created on Feb 9, 2013

@author: cjhuo
'''
import tornado.web
import sys
import os.path
import json

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
        minVal = int(self.get_argument("min"))
        maxVal = int(self.get_argument("max"))
        wavech = []
        for i in range(len(self.ecg.wavech)):
            wavech.append([self.ecg.wavech[i][j] for j in range(minVal, maxVal)])
        if len(wavech[0]) > arrayLength: # compress it
            print >> sys.stderr, 'TOO MANY SAMPLES, CAN\'T DRAW DIRECTLY, START COMPRESSING'
            wavech = self.dataSetsCompression(wavech, arrayLength)
            print >> sys.stderr, 'COMPRESSION COMPLETE, SENDING COMPRESSED DATA FOR DRAWING'
        
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
                    'data': datasets
                    })

    def post(self): # file upload handler
        try:
            if len(self.request.files) != 0: #user uploaded file from UI 
                f = self.request.files['uploaded_files'][0]
                orig_fname = f['filename']
                # search locally by the filename, if existed, use it instead of uploading
                path1 = os.path.join(self.settings['static_path'], uploadPath)
                path2 = os.path.join(self.settings['static_path'], os.pardir, os.pardir, 'data')
                
                path = None
                if os.path.exists(os.path.join(path1,orig_fname)):
                    path = path1
                elif os.path.exists(os.path.join(path2,orig_fname)):
                    path = path2
                
                if path == None:
                    path = os.path.join(self.settings['static_path'], uploadPath)
                    ofd = open(path + orig_fname, 'w')
                    ofd.write(f['body'])
                    ofd.close()
                    print >> sys.stderr, 'FILE UPLOADED, OPENING'
                else:
                    print >> sys.stderr, 'FILE EXISTS, OPENING DIRECTLY'
                
                print >> sys.stderr, 'START READING ECG DATA IN ECG MODULE..'
                self.ecg.setFile(path + orig_fname)              
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
                tmpWavech.append([wavech[i][j] for j in range(2500)]) # only pick the first 2500 samples for the first time
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

        print pointInterval
        val = {'dspData': datasets, 'pointInterval': pointInterval, 'base': base}
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
            
        
    def dataSetsCompression(self, wavech, arrayLength): # compress data into length of arrayLength by averaging
        tempWavech = []
        for data in wavech:
            tmpList = []
            self.arrayCompression(data, tmpList, arrayLength)
            tempWavech.append(tmpList)            
        
        return tempWavech
            
            
class ECGHandler(BaseHandler):
    def initialize(self, ecg):
        self.ecg = ecg
    
    def post(self):
        try:
            if len(self.request.files) != 0: #user uploaded file from UI 
                f = self.request.files['uploaded_files'][0]
                orig_fname = f['filename']
                import os
                path = os.path.join(os.path.dirname(__file__), os.pardir, uploadPath)
                ofd = open(path + orig_fname, 'w')
                ofd.write(f['body'])
                ofd.close()
                self.ecg.setFile(path + orig_fname)               
            else: #user user the default test file
                self.ecg.setFile()               
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
       