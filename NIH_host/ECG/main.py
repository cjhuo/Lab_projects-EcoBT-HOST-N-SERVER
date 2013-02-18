'''
Created on Feb 11, 2013

@author: cjhuo
'''
import sys
sys.dont_write_bytecode = True
if __name__ == "__main__":
    sys.path.append("./host")
    sys.path.append("./webEngine")
    import host.main as m1
    import webEngine.main as m2
    import threading
    t = threading.Thread(target = m2.main)
    t.setDaemon(True)
    t.start()
    m1.main()
    
