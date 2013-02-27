'''
Created on Feb 9, 2013

@author: cjhuo
'''
import tornado.web

import json

from BaseHandler import BaseHandler
from ecg.ECG_reader import ECG_reader

uploadPath = "static/Uploads/"
#fake the labels for each channels for demo purpose, 
#eventually label information should be passed from ecg module
ECG_CHANNELLABELS = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']

class ECGAllInOneHandler(BaseHandler):
    def initialize(self):
        self.ecg = ECG_reader()

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
            
    def getDataFromDicomFile(self):
        #wavech, peaks = ecg.ECG_reader.getTestData()
        wavech = self.ecg.wavech
        
        #create dataset dict to be sent to web server and fill in data
        datasets = []
        for i in range(len(wavech)):
            data = [wavech[i][j] for j in range(len(wavech[i]))]
            label = ECG_CHANNELLABELS[i]            
            #label = "channel " + str(i)
            datasets.append(dict())
            datasets[i]['data'] = data 
            datasets[i]['label'] = label
            
        #add peak information to structure to be sent to frontend
        # format of peaks: "peaks": [index of 1st peak, index of 2nd peak, ...]

        val = {'dspData': datasets}
        return val        
    
    
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
        bins = self.ecg.getBinInfo(data['qPoint'][0], data['tPoint'][0], data['bin']);
        
        print bins
        self.write({'data': bins}) #format of bins json: {'data': bins info}
              
            
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
            data = [wavech[i][j] for j in range(len(wavech[i]))]
            label = ECG_CHANNELLABELS[i]            
            #label = "channel " + str(i)
            datasets.append(dict())
            datasets[i]['data'] = data 
            datasets[i]['label'] = label
            
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
       