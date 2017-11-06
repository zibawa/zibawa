from __future__ import unicode_literals
from __future__ import print_function
from django.conf import settings

from elasticsearch import Elasticsearch,helpers
from .influx_functions import sendToInflux
import json
import logging
logger = logging.getLogger(__name__)




def sendToDB(index,data,tags):
    
    
    json_data = json.dumps(data,default=date_handler)
    json_tags = json.dumps(tags,default=date_handler)
    logger.info('Sending to db %s data %s', index,json_data)
    logger.info('Sending to db tags %s', json_tags)
    if (settings.DATASTORE=='ELASTICSEARCH'):
        #for elasticsearch merge data and tags arrays
        data.update(tags)
        result=sendToElastic(index,json_data)
        
    elif (settings.DATASTORE=='INFLUXDB'):
        
        result=sendToInflux(index,data,tags)
    return result


def date_handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        raise TypeError



def getElasticConnection():
    config=settings.ELASTICSEARCH
    es = Elasticsearch([config['host']],
                           http_auth=(config['user'], config['password']),
                           port=config['port'],
                           use_ssl=config['use_ssl'],
                           ca_certs=config['path_to_ca_cert'],
                           client_cert=config['path_to_client_cert'],
                           client_key=config['path_to_key'])
    return es  


    
def sendToElastic(indexName,jsonData):    
#careful with document types! currently static as json mapping must also use json!        
   
    es = getElasticConnection()
    result = es.index(index=indexName, doc_type="zibawa", body=jsonData)
    return result

def sendToElasticBulk(indexName,datapoints):
    
    
   


    es = getElasticConnection()
  
    actions =[]
    
    for datapoint in datapoints:
        action = {
        "_index": indexName,
        "_type": "zibawaBulk",
        "_source": datapoint
        }
        actions.append(action)

    result=helpers.bulk(es, actions)
    
    return result
    


    
    




        
   
def searchElastic(indexName,query):
        
        
        es = getElasticConnection()
                  
        try:       
            res = es.search(index=indexName, body=query)
            return res
        
        except:
            return False

        
        





def initializeElasticIndex(indexName):
    
    mappingJson={"mappings": {
        "zibawa": {
            "properties": {
                "timestamp": {
                    "type": "date"
                    },
        "queueTime": {
          "type": "integer"
          },
        "processTime": {
          "type": "integer"
          },
        "value":{
            "type": "float"
          },
         "location": {
          "type": "geo_point"
          }, "ch_config":{
           "type": "text"
          },
          "channel_id":{
              "type": "text",
              "fields":{
                  "keyword":{"type":"keyword"}}
          },
          "operation":{
              "type": "text",
              "fields":{
                  "keyword":{"type":"keyword"}}
          },
         "device_name":{
             "type": "text",
             "fields":{
                  "keyword":{"type":"keyword"}}
          },
         "device_id": {
             "type": "text",
             "fields":{
                  "keyword":{"type":"keyword"}}
          },
          "section": {
             "type": "text",
             "fields":{
                  "keyword":{"type":"keyword"}}
          },
          "subgroup": {
             "type": "text",
             "fields":{
                  "keyword":{"type":"keyword"}}
          }
                           
          }
                 }
                              }
        }
    
    
   
   
    try:
        es= getElasticConnection() 
    
        if not es.indices.exists(index=indexName):
            es.indices.create(index=indexName, ignore=400, body=mappingJson)
    except:
        return False
        
    return True