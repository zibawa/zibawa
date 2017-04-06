from __future__ import unicode_literals
from __future__ import print_function
from builtins import str
from django.db import models
from django.core.exceptions import ValidationError
from datetime import datetime
from django.conf import settings
import pika
import ssl
from elasticsearch import Elasticsearch
from genericpath import exists
from django.contrib.admin.utils import help_text_for_field
from influxdb import InfluxDBClient,SeriesHelper
from .influx_functions import sendToInflux
import json



import logging
logger = logging.getLogger(__name__)




def getRabbitConnection():
    
    #setting heartbeat to 5 was an experiment to stop crashing, seems towork
    config=settings.RABBITMQ
    if settings.DASHBOARD['verify_certs']:
        verifycerts= ssl.CERT_REQUIRED 
    else:
        verifycerts= ssl.CERT_NONE
    credentials = pika.PlainCredentials(config['user'],config['password'])
    cp = pika.ConnectionParameters(host=config['host'],
                               port=int(config['port']),
                               virtual_host='/',
                               heartbeat_interval=5,
                               credentials=credentials,
                               ssl=config['use_ssl'],
                               ssl_options=dict(
                                   ca_certs=config['path_to_ca_cert'],
                                    keyfile=config['path_to_key'],
                                    certfile=config['path_to_client_cert'],
                                    cert_reqs=verifycerts
                                   ))
                               
    return cp






def sendToRabbitMQ(topic,message):

    cp=getRabbitConnection()    
    connection = pika.BlockingConnection(cp)
    channel = connection.channel()
    routing_key= topic
        
    channel.basic_publish(exchange='amq.topic',
                      routing_key=routing_key,
                      body=message)
    result=(" [x] Sent %r:%r" % (routing_key,message))
    connection.close()
            
    return result


def sendToDB(index,data,tags):
    
    config=settings.DATASTORE
    json_data = json.dumps(data,default=date_handler)
    json_tags = json.dumps(tags,default=date_handler)
    logger.info('Sending to db %s data %s', index,json_data)
    logger.info('Sending to db tags %s', json_tags)
    if (config=='ELASTICSEARCH'):
        #for elasticsearch merge data and tags arrays
        data.update(tags)
        result=sendToElastic(index,json_data)
        
    elif (config=='INFLUXDB'):
        
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
        res = es.index(index=indexName, doc_type="json", body=jsonData)
        return res
        
        #except:
        #    return False
def searchElastic(indexName,query):
        
        
        es = getElasticConnection()
                  
        try:
            res = es.search(index=indexName, body=query)
            return res
        except:
            return False

        
        





def initializeElasticIndex(indexName):
    
    mappingJson={"mappings": {
        "json": {
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
    
    
   
   
    
    es= getElasticConnection() 
    
    if not es.indices.exists(index=indexName):
        es.indices.create(index=indexName, ignore=400, body=mappingJson)
        
    return
