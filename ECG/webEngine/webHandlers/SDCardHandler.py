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
            os.system(command)
            print command
            #self.readeSD(os.path.join(dataPath, "records"))
            #os.system('open "%s"' % dataPath)
            self.write("SD CARD READ SUCCESSFUL!")
        except:
            self.write("SD CARD READ FAILED!")
        '''
        for root, dirs,files in os.walk(dataPath):
            for file in files:
                if file.endswith(".txt"):
                    filename = os.path.abspath(file)
                    self.constructDicom(str(os.path.join(root, file)))
        '''
        
        #os.system("""osascript -e 'do shell script "sudo python %s /dev/disk1 ~/Desktop/ECG/data/records" with administrator privileges'""" % ())
        #os.system("""osascript -e 'do shell script "~/Desktop/ECG/applescript/convert.sh"'""")
    '''
    def constructDicom(self, filename):
        reader = SDCard_Reader(filename)
        ecg_data = reader.read_data()
        date = "%04d%02d%02d" % (ecg_data['start_time'].year, ecg_data['start_time'].month, ecg_data['start_time'].day)
        time = "%02d%02d%02d" % (ecg_data['start_time'].hour, ecg_data['start_time'].minute, ecg_data['start_time'].second)
        outfile = "%s/%s_%s.dcm" % (os.path.dirname(filename), date, time)
        packDICOM(ecg_data, outfile)        
    
    def readeSD(self, path, dev="/dev/disk1"):  
        SDCard_Reader(dev, path).read_data()
    '''
