'''
Created on Jan 28, 2014

@author: cjhuo
'''
import tornado.httpclient, json, pprint, struct, binascii

def getOverview():
    client = tornado.httpclient.HTTPClient()
    
    try: 
        response = client.fetch("http://ecocloud.eng.uci.edu:8881/check")
    except httpclient.HTTPError as e:
        print "Error:", e
        http_client.close()    
    
    pprint.pprint(json.loads(response.body))
    
def Query(query_type, gateway_id, peripheral_id, service_id, characteristic_id):
    client = tornado.httpclient.HTTPClient()
    
    try: 
        response = client.fetch("http://ecocloud.eng.uci.edu:8881/query?"+
                                "query_type="+str(query_type)+
                                "&gateway_id="+str(gateway_id)+
                                "&peripheral_id="+str(peripheral_id)+
                                "&service_id="+str(service_id)+
                                "&characteristic_id="+str(characteristic_id))
    except tornado.httpclient.HTTPError as e:
        print "Error:", e
        client.close()    
    
    pprint.pprint(json.loads(response.body))
    data = json.loads(response.body)
    value =struct.unpack("@i",binascii.unhexlify(data['result']))[0]
    print 'value is', value


if __name__ == "__main__":
    while True:
        s = raw_input('> ')
        
        print s
        if s.strip() =='':
            print 'bye'
            break
        if s.strip() == 'check':
            getOverview()
        else:
            try:
                eval(s.strip())
            except Exception as e:
                print "Error: ", e
    

