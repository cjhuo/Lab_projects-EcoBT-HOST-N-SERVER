'''
Created on Feb 24, 2013

@author: cjhuo
'''
import json
import os
import csv
from BaseHandler import BaseHandler

class ConfigHandler(BaseHandler):
    def initialize(self, ecoBTApp):
        self.ecoBTApp = ecoBTApp
    
    def post(self): # get uploaded config file from user
        try:
            address = self.get_argument(u'address')
            if len(self.request.files) != 0: #user uploaded file from UI 
                f = self.request.files['uploaded_files'][0]
                orig_fname = f['filename']
                path = os.path.join(os.path.dirname(__file__), os.pardir, "static/Uploads/")
                fname = path + orig_fname
                ofd = open(fname, 'w')
                ofd.write(f['body'])
                ofd.close()
                
                # update settings in EcoBTApp
                self.ecoBTApp.managerWorker.findPeripheralWorkerByAddress(address).findSIDsSet().updateSettingsByFile(fname)
                self.ecoBTApp.managerWorker.findPeripheralWorkerByAddress(address).findSIDsRead().updateParamsByFile(fname)  

                
                #self.ecg.setFile(path + orig_fname)               
            else: #use default test file
                pass#self.ecg.setFile()               
            #val = self.getDataFromDicomFile()
            #self.write(val)
        except:
            self.send_error(302) # 302: invalid file
            
    def get(self): # get current settings from UI, generate config.csv for user to download
        data = json.loads(self.get_argument("data"))
        print data
        address = str(data['address'])
        settings = data['settings']
        params = data['params']
        path = os.path.join(os.path.dirname(__file__), os.pardir, "static/Uploads/")
        fname = "config_" + address + ".csv"
        with open(path + fname, 'w') as csvfile:
            csvWriter = csv.writer(csvfile, delimiter=',')
            for key, val in settings.items():
                csvWriter.writerow([str(key), int(val)])
            for key, val in params.items():
                csvWriter.writerow([str(key), float(val)])
        self.write({'url': self.static_url(path+fname)})
        self.ecoBTApp.managerWorker.findPeripheralWorkerByAddress(address).findSIDsSet().updateSettingsByDict(settings)
        self.ecoBTApp.managerWorker.findPeripheralWorkerByAddress(address).findSIDsRead().updateParamsByDict(params)
        
    def put(self): # get current settings from UI, update settings to EcoBTApp
        data = json.loads(self.get_argument("data"))
        print data
        address = str(data['address'])
        settings = data['settings']
        params = data['params']
        self.ecoBTApp.managerWorker.findPeripheralWorkerByAddress(address).findSIDsSet().updateSettingsByDict(settings)        
        self.ecoBTApp.managerWorker.findPeripheralWorkerByAddress(address).findSIDsRead().updateParamsByDict(params)
        
        # update settings in EcoBTApp


