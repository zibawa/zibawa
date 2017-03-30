from __future__ import print_function
from __future__ import absolute_import
from builtins import str
from builtins import range
from builtins import object
from django.http import Http404
from django.shortcuts import render
from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from .models import sendToRabbitMQ
from .models import sendToRabbitMQ, getInfluxConnection
from .grafana_functions import GrafanaUser,testGrafanaUp
import random
import string

import logging
logger = logging.getLogger(__name__)  

class testObj(object):

    def __init__(self, name,status,message):
        self.name = name
        self.status = status #true or false
        self.message= message #error message human readable

      




def constructStatusList(request):
    #statusList is list of status with error messages also used in device/testMessage view

    rabbitMQTest=testConnectToRabbitMQ 
    grafanaUpTest=testGrafanaUp 
    grafana_user=GrafanaUser(request.user.id, request.user.username,"not_used",request.user.email)
    grafanaUserTest=grafana_user.exists()
    grafanaUserTest=testObj("Grafana User",grafana_user.exists(),"")
    influxTest=testInfluxDB(request.user)
        #grafanaDataSourceTest=addDataBaseToGrafana(influxTest,grafanaUserTest.message,request.user) 
    if not(grafana_user.get_orgID):
        grafana_user.add_to_own_org()
        grafana_user.fix_permissions()
    grafanaDataSourceTest=testObj("GrafanaDataSource",grafana_user.add_datasource(),"")
        
    status_list=(rabbitMQTest,grafanaUpTest,grafanaUserTest,influxTest,grafanaDataSourceTest)
    
    return status_list
    
    
       
def testConnectToRabbitMQ():
        
    result=sendToRabbitMQ('health.admin.test','testMessage')
    try: 
        result=sendToRabbitMQ('health.admin.test','testMessage')
        output= testObj("rabbitMQ",True,"")
    except Exception as e: #return str(e)
        #this is not sending any string as e dont know why
        output= testObj("rabbitMQ",False,"Contact your administrator, Grafana could not contact rabbitMQ")
        logger.critical('couldnt connect to rabbitMQ %s,', e)
            
    return output
  
def testInfluxDB(current_user):
    #creates new database 
    #returns db name and credentials in array

    output=testObj("influxDB",False,"")
    output.database="dab"+str(current_user.username)
   
    try:
        client=getInfluxConnection()
        result=client.create_database(output.database)
        if not result:
            output.status=True
            output.message="UserDatabase on-line"
    
        
    except Exception as e: 
        logger.warning('Couldnt create influxDB %s,', e)
        output.message='Could not create influxDB'
        output.status=False
        #credentials['success']=False
                
    return output
    
    

def id_generator(size=10, chars=string.ascii_uppercase + string.digits):
    '''need to add tags to database!!!!'''
    return ''.join(random.choice(chars) for _ in range(size))

    


    