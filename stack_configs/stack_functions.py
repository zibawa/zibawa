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
from .models import sendToRabbitMQ, getFromGrafanaApi,getInfluxConnection
import random
import string

import logging
logger = logging.getLogger(__name__)  

class testObj(object):

    def __init__(self, name,status,message):
        self.name = name
        self.status = status
        self.message= message

      

def constructStatusList(request):
    #statusList is list of status with error messages also used in device/testMessage view

    rabbitMQTest=testConnectToRabbitMQ 
    grafanaUpTest=testGrafanaUp 
    orgID= getGrafanaOrg(request.user)
    if not(isinstance(orgID, ( int, int ) )):
        grafanaOrgTest=testObj("GrafanaLogIn",False,"You need to sign in to Grafana Dashboard for the first time before it can be configured")
        status_list=(rabbitMQTest,grafanaUpTest,grafanaOrgTest)
    else:
        influxTest=testInfluxDB(request.user)
        grafanaOrgTest=testObj("GrafanaLogIn",True,"")   
        grafanaDataSourceTest=addDataBaseToGrafana(influxTest,orgID,request.user) 
        status_list=(rabbitMQTest,grafanaUpTest,grafanaOrgTest,influxTest,grafanaDataSourceTest)
    
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

def testGrafanaUp():
    try:
        data={}
        apiurl="/api/org"
        result=getFromGrafanaApi(apiurl, data,'GET')
        output=testObj("Grafana Running",True,"")
    except Exception as e:
        output=testObj("Grafana Running", False,"Contact your administrator, Zibawa cannot contact Grafana")
        logger.critical('could not connect to Grafana %s',e)
    return output

def getGrafanaOrg(current_user):    
    
    
    #get orgID whose name is equal to email for the current user
    #if fails returns error string
    orgID=0
    apiurl="/api/orgs/name/"+str(current_user.email)
    data={}
         
    try:
        result=getFromGrafanaApi(apiurl,data,'GET')    
        orgID=result['id']
        return orgID
    except Exception as e: 
        logger.critical('Couldnt find Grafana Organization %s,', e)
        return str(e)

    
def addDataBaseToGrafana(influxTest,orgId,current_user):

#adds influxDB datasource to Grafana organization based on array of credentials
 
 
 #get Grafana userID (ignore master Admin)
    
    apiurl="/api/orgs/"+str(orgId)+"/users"
    data={}
    results=getFromGrafanaApi(apiurl,data,'GET') 
    for result in results:
        #check if the login of the grafana user is the login of super user as defined in settings.py
        if not (result['login']==settings.DASHBOARD['user']):
            grafanaUser=result['userId']
#get Grafana Datasource by name
    
    data={}
    apiurl="/api/datasources/name/"+str(influxTest.database)
    result=getFromGrafanaApi(apiurl,data,'GET') 
    print(result)   
    if not result or not 'database' in result:
        #create the datasource
        #add Admin user to the user-specific organization
        try:
        
            data={
                "loginOrEmail":settings.DASHBOARD['user'],
                "role":"Admin"
                }
            apiurl="/api/orgs/"+str(orgId)+"/users"
            result=getFromGrafanaApi(apiurl,data,'POST')
                
    #change admin level of user back to editor (grafana creates users with admin level)
   
    
    
            apiurl="/api/orgs/"+str(orgId)+"/users/"+str(grafanaUser)
            data={"role":"Editor"}
            result=getFromGrafanaApi(apiurl,data,'PATCH')
        #change active organization (empty data array)
            data={}
            apiurl="/api/user/using/"+str(orgId)
            result=getFromGrafanaApi(apiurl,data,'POST')
         
        #add datasource to organization
            DBusername="dab"+str(current_user.username)
            DBpassword=id_generator()
            #createInfluxReadOnlyUser for database
            client=getInfluxConnection()
            result=client.create_user(DBusername, DBpassword, admin=False)
            result=client.grant_privilege('read',influxTest.database,DBusername)
        
            apiurl= "/api/datasources"
            data={}
            data['name']=influxTest.database
            data['type']="influxdb"
            data['url']="http://localhost:8086"
            data['access']="proxy"
            data['basicAuth']=False
            data['password']=DBpassword
            data['user']= DBusername
            data['database']=influxTest.database
        
            result=getFromGrafanaApi(apiurl,data,'POST')
            output= testObj("Grafana Data Source",True,influxTest.database)
        except Exception as e: 
            
            message= "Database:"+str(influxTest.database)
            
            logger.warning('Couldnt add datasource to Grafana Organization %s,', e)
            output= testObj("Grafana Data Source",False,e)
    elif result['database']==influxTest.database:
          
            output=testObj("Grafana Data Source",True, influxTest.database)
    else:
        message="unexpected datasource"+str(result['database'])
        output=testObj("Grafana Data Source",False,message)                

   
    
    return output
   
   
def testInfluxDB(current_user):
    #creates new database 
    #returns db name and credentials in array

    output=testObj("influxDB",False,"")
    output.database="dab"+str(current_user.id)
   
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

    


    