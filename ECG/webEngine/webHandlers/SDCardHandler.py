'''
Created on Feb 27, 2013

@author: cjhuo
'''
from BaseHandler import BaseHandler
class SDCardHandler(BaseHandler):
    def get(self):
        import os
        os.system("""osascript -e 'do shell script "sudo python ~/Desktop/ECG/applescript/SDCard_reader.py /dev/disk1 ~/Desktop/ECG/data/records" with administrator privileges'""")
        os.system("""osascript -e 'do shell script "~/Desktop/ECG/applescript/convert.sh"'""")
        