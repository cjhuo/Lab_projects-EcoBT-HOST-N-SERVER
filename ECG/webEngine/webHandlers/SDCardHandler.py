'''
Created on Feb 27, 2013

@author: cjhuo
'''
import os
from BaseHandler import BaseHandler
#from sdReader.SDCard_reader import SDCard_Reader
class SDCardHandler(BaseHandler):
    def get(self):
        try:
            dataPath = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir, "data/record"))
            dev="/dev/disk1"
            command = """osascript -e 'do shell script "sudo python %s %s %s" with administrator privileges'""" % \
                ((os.path.join(os.path.dirname(__file__), os.path.pardir,"sdReader/SDCard_reader.py"),  dev, dataPath))
            result = os.system(command)
            #print result
            #self.readeSD(os.path.join(dataPath, "records"))
            #os.system('open "%s"' % dataPath)
            if result == 0:
                self.write({'message': "SD CARD READ SUCCESSFUL!"})
            else:
                self.write({'message': "SD CARD READ FAILED!"})
            
        except:
            self.write("SD CARD READ FAILED!")

