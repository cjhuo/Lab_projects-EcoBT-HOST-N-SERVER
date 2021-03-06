'''
Created on Jan 28, 2014

@author: cjhuo
@summary: 1. Test client send query with 'check' command to get overview under central including
          gateways, peripherals under gateways, profile hierarchy in each peripherals
          2. Send query to read, write value against any characteristic using 'Query' command
          Example:
          > Query('Read', gateway_id, peripheral_id. srv
'''
import tornado.httpclient, json, pprint, struct, binascii, readline
CENTRAL_SERVER_ADDRESS = 'ecocloud.eng.uci.edu:8881'
def getOverview():
    client = tornado.httpclient.HTTPClient()
    
    try: 
        response = client.fetch("http://" +CENTRAL_SERVER_ADDRESS+"/check")
    except tornado.httpclient.HTTPError as e:
        print "Error:", e
        client.close()    
        return
    pprint.pprint(json.loads(response.body))
    
def QUERY(query_type, gateway_id, peripheral_id, service_id, characteristic_id, message=None):
    client = tornado.httpclient.HTTPClient()
    
    try: 
        response = client.fetch("http://"+CENTRAL_SERVER_ADDRESS+"/query?"+
                                "query_type="+str(query_type)+
                                "&gateway_id="+str(gateway_id)+
                                "&peripheral_id="+str(peripheral_id)+
                                "&service_id="+str(service_id)+
                                "&characteristic_id="+str(characteristic_id)+
                                "&message="+str(message))
    except tornado.httpclient.HTTPError as e:
        print "Error:", e
        client.close()    

    try:
        pprint.pprint(json.loads(response.body))
    except:
        print response.body  
        return
    try:
        data = json.loads(response.body)
        value =struct.unpack("@i",binascii.unhexlify(data['result']))[0]
        print 'value is', value
    except Exception as e:
        return

  


if __name__ == "__main__":
    while True:
        s = raw_input('> ')
        
        #print s
        if s.strip() =='':
            print 'bye'
            break
        if s.strip() == 'check':
            getOverview()
        else:
            try:
                eval(s.strip().upper())
            except Exception as e:
                print "Error: ", e
    

