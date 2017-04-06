
from django.conf import settings
from django.utils.dateparse import parse_datetime
from influxdb import InfluxDBClient,SeriesHelper
import json
import logging
logger = logging.getLogger(__name__)


            
def getInfluxConnection():
    
    config=settings.INFLUXDB
    
    logger.info('Connecting to influx %s', config['host'])
    
    try:
        myClient = InfluxDBClient(host=config['host'],port=config['port'],username=config['user'],password=config['password'],ssl=config['use_ssl'],verify_ssl=config['verify_certs'])
    except Exception as e: 
        logger.critical('couldnt connect to influx %s,', e)
                           
        return str(e)
    return myClient  
   

        
    
def sendToInflux(indexName,jsonData,tags):   
    
    client=getInfluxConnection()
    
    
    '''for each field in jsonData if timestamp-pass with reserved key "time"
    if float, convert, otherwise pass as string field
    everything else treat as tag'''
    #jsonData={"timestamp":'2009-11-10T23:00:00Z',"value":0.44}
    f={}
    d={}             
    for key, value in list(jsonData.items()):
        if (key=='timestamp'):
            d["time"]= value
        else:
            try:
                f[key]=float(value)  
            except:
                f[key]=value
   
    #d = {}
    d["measurement"] = "mqttData"
    d["tags"] = tags
    #d["time"] = "2009-11-10T23:00:00Z"
    d["fields"] = f
    #below for debugging 
    json_tags = json.dumps(tags,default=date_handler)
    json_fields = json.dumps(f,default=date_handler)
    logger.debug('tags %s', json_tags)   
    logger.debug('fields %s', json_fields)
    #above for statements for debugging only
    json_body=[d]
    logger.debug('trying db create') 
       
    try:
        res=client.write_points(json_body,database=indexName)
        logger.info('influx write result %s,', res) 
    except Exception as e: 
        logger.warning('couldnt write to database %s,', e) 
    #result = client.query('select value from cpu_load_short;')
        res=e    
    logger.warning('returning res %s,', res)     
    return res



def getQueryInflux(index,query):

    client=getInfluxConnection()
    try:
        logger.debug('influx query: %s,database %s', query,index) 
        resultSet = client.query(query,database=index)
        logger.debug('influx resultset: %s,', resultSet) 
        result=resultSet.get_points()
    except Exception as e:
        result={}  
        logger.warning('influx query unsuccesful %s,', e) 
    return result


def getLastInflux(index,device_id,channel_id):
    #returns last influx line sent 
    query="SELECT * from \"mqttData\" WHERE \"device_id\" = \'"+str(device_id)+"\' AND \"channel_id\" = \'"+str(channel_id)+"\' ORDER BY time DESC LIMIT 1"
    results=getQueryInflux(index,query)
    return results

def getLastTimeInflux(index,device_id,channel_id):
    logger.debug ('getting lasttime for device id: %s and channelid :%s',device_id,channel_id)
    results=getLastInflux(index,device_id,channel_id)
    datetime="error" 
    for result in results:
        logger.debug ('getLastInflux time result %s',result)
        try:
            datetime=parse_datetime(result['time'])  
        except:
            pass
           
    return datetime




   
def sendToInfluxCurlForTesting(indexName,jsonData,tags):  
    
    #curl -i -XPOST 'http://localhost:8086/write?db=mydb' --data-binary 'cpu_load_short,host=server01,region=us-west value=0.64 1434055562000000000'
    #this works ok but i prefer to use library
    
    import requests
    
    url= 'http://192.168.1.10:8086/write?db=example'
    data= 'cpu_load_short,host=server01,region=us-west value=0.64 1434055562000000000'
    
    result = requests.post(url,
                    data,
                    headers={'Content-Type': 'application/octet-stream'})
    
    print("Result: {0}".format(result))
    
    
    return result   

def date_handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        raise TypeError

