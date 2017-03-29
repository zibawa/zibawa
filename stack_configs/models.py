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
import json



import logging
#from chardet.test import result

logger = logging.getLogger(__name__)
# Create your models here.



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

        
        

            
def getInfluxConnection():
    #will change name of object elasticDbase in future
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
    
    try:
        client.create_database(indexName)
    except Exception as e: 
        logger.critical('couldnt create database %s,', e)   
    try:
        res=client.write_points(json_body,database=indexName)
    except Exception as e: 
        logger.warning('couldnt write to database %s,', e) 
    #result = client.query('select value from cpu_load_short;')
        res=e    
    
    return res


def getQueryInflux(index,query):

    client=getInfluxConnection()
    try:
        logger.debug('influx query: %s,', query) 
        resultSet = client.query(query,database=index)
        logger.debug('influx resultset: %s,', resultSet) 
        result=resultSet.get_points()
    except Exception as e:
        result={}  
        logger.warning('influx query unsuccesful %s,', e) 
    return result




   
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


'''
def getFromGrafanaApi(apiurl,data,callType):
    
    #call type= GET,POST,PUT,DELETE
    import urllib3
        
    if settings.DASHBOARD['use_ssl']:
        protocol='https://'
        cert_reqs='CERT_REQUIRED' # Force certificate check.
    else:   
        protocol='http://'
        cert_reqs=None #
        
    http = urllib3.PoolManager(
    cert_reqs=cert_reqs,
    ca_certs=settings.DASHBOARD['path_to_ca_cert'],         # Path to your certificate bundle.
    )
    
    auth= settings.DASHBOARD['user']+":"+settings.DASHBOARD['password']
    headers=urllib3.util.request.make_headers(keep_alive=None, accept_encoding='application/json', user_agent=None, basic_auth=auth, proxy_basic_auth=None, disable_cache=None)
        
    encoded_data = json.dumps(data).encode('utf-8')
        
        
    request_url=protocol+settings.DASHBOARD['host']+":"+settings.DASHBOARD['port']+apiurl
    logger.debug('sending http request to  %s,', request_url)     
    r = http.request(
        callType,
        url= request_url,
        body=encoded_data,
        headers=headers,
        )
    json_data=json.loads(r.data.decode('utf-8'))
    logger.debug('grafana response %s',json_data)
   
    return json_data
'''
'''
def getFromGrafanaApi(apiurl,data,callType):
    
    #call type= GET,POST,PUT,DELETE
    import urllib3
    
        
    http = urllib3.PoolManager(
    cert_reqs=None,
    ca_certs='/home/julimatt/vps370273/fullchain.pem',         # Path to your certificate bundle.
    )
    
    http=urllib3.PoolManager()
    
    auth= settings.DASHBOARD['user']+":"+settings.DASHBOARD['password']
    
    headers=urllib3.util.request.make_headers(keep_alive=None, accept_encoding='application/json', user_agent=None, basic_auth=auth, proxy_basic_auth=None, disable_cache=None)
        
    encoded_data = json.dumps(data).encode('utf-8')
      
    r = http.request(
        callType,
        url= 'https://zibawa.com:3000/api/org',
        body=encoded_data,
        headers=headers,
        )
    json_data=json.loads(r.data.decode('utf-8'))
    logger.debug('grafana response %s',json_data)
   
    return json_data
'''

    

#openssl s_client -connect zibawa.com:3000 -CAfile /home/julimatt/vps370273/fullchain.pem


def getFromGrafanaApiAsUser(apiurl,data,username,password):

#probably need to rewrite this!!

#testing from command line
# curl http://user:password@192.168.1.10:3000/api/org
    import requests
    config=settings.DASHBOARD
    if config['use_ssl']:
        protocol='https://'
    else:   
        protocol='http://'
    
    url=protocol+config['host']+":"+config['port']+apiurl
    
    
    headers = {'Accept': 'application/json',
                   'Content-Type' : 'application/json'}
       
    result = requests.get(url,auth=(username,password),headers=headers,data=json.dumps(data))
    json_data = json.loads(result.text)
    return json_data





def addToLDAPGroupOld(ldapUserName,groupName):
    con=connectToLDAP()
    old_members = dict()
    new_members = dict()
    new_members['memberUid']=str(ldapUserName).encode('utf-8')
    old_members
    
    group_dn = 'cn='+groupName+','+settings.AUTH_LDAP_GROUPS_OU_DN
    
    try:
        ldif = ldap.modlist.modifyModlist(old_members,new_members)
        con.modify_s(group_dn, ldif)
        con.unbind_s()
    except Exception as e: 
        logger.warning('couldntAdd to LDAP group %s,', e)   
    
        
    return    



def initializeDeviceLDAPOld(device,password):
             
    #deviceID is unique to database. (as defined in models.devices
    #deviceID could colide with (human) userNames.at present this will
    #cause failure.
    #uid is autonumeric id field from device table (not same as device id)
    #add 1000000 so as not to colide with people uids.
    
    username=str(device.device_id)
    
    dn= str("cn="+str(username)+","+settings.AUTH_LDAP_USERS_OU_DN)
    #check if entry already exists
    result =simpleLDAPQuery(username)
    
    if (result==[]):
        #create device in LDAP    
        uidNumber= str(device.id + 1000000)
    
        con=connectToLDAP() 
          
        modlist={}
        modlist['objectClass']=["inetOrgPerson", "posixAccount", "shadowAccount"]
        modlist['sn']=str("lastname")
        modlist['givenName']=str("first_name")
        modlist['mail']= str("dontuse@mail.com")
        modlist['cn']=str(username)
        modlist['displayName']=str(username)
        modlist['uid']=str(username)
        modlist['uidNumber']=str(uidNumber)
        modlist['gidNumber']=str(settings.AUTH_LDAP_DEVICES_DEFAULT_GID)
        modlist['homeDirectory']=str("/home/zibawa/"+str(username))
        modlist['userPassword']=str(password)
    
        
# addModList transforms your dictionary into a list that is conform to ldap input.
        result = con.add_s(dn, ldap.modlist.addModlist(modlist))
                
        addToLDAPGroup(username,'active')
        addToLDAPGroup(username,'device') 
    
        return result
    else:
        #if doesnt exist we just reset password
        result= resetLDAPpassword(dn,password)
    return result 




def resetLDAPpasswordold(user_dn,new_password):
    
    con=connectToLDAP()
    password_value= str(new_password)
    add_pass = [(ldap.MOD_REPLACE, 'userPassword', [password_value])]
    try:
        result= con.modify_s(user_dn,add_pass)
        con.unbind_s()
        return result
    except Exception as e: 
        
        logger.warning('couldntreset LDAP password %s,', e)   
        result=None
        return result


 
def connectToLDAP():
    #old ldap-python to eliminate
    logger.info('connecting to LDAP on %s,', settings.AUTH_LDAP_SERVER_URI)
    try:
        
        con = ldap.initialize(settings.AUTH_LDAP_SERVER_URI,bytes_mode=False)
        con.simple_bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)
        return con
    except Exception as e: 
        logger.warning('couldntConnect to LDAP %s,', e)   
        return 
     
    
    return con  



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
