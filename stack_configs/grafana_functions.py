from django.contrib.auth.models import User
from django.conf import settings
from .models import getInfluxConnection

import logging
import email
import json
import random
import string

logger = logging.getLogger(__name__)  

class testObj(object):

    def __init__(self, name,status,message):
        self.name = name
        self.status = status #true or false
        self.message= message #error message human readable



def getFromGrafanaApi(apiurl,data,callType):

    from requests import Request, Session
    
    if settings.DASHBOARD['use_ssl']:
        protocol='https://'
        if settings.DASHBOARD['verify_certs']:
            verifycerts= settings.DASHBOARD['path_to_ca_cert'] 
        else:
            verifycerts=False
        
    else:   
        protocol='http://'
        verifycerts=False
    
    
    
    url=protocol+settings.DASHBOARD['host']+":"+settings.DASHBOARD['port']+apiurl
    #url= 'https://zibawa.com:3000/api/org'
    logger.debug('making %s request to grafana %s',callType,url)
    username= settings.DASHBOARD['user']
    password= settings.DASHBOARD['password']
    
    headers = {'Accept': 'application/json',
                   'Content-Type' : 'application/json','User-agent': 'Mozilla/5.0'}
    
    s = Session()
    req = Request(callType,  url, data=json.dumps(data), headers=headers, auth=(username,password))

    prepped = s.prepare_request(req)
    
    result = s.send(prepped,
    verify=verifycerts,
    
    )

    print(result.status_code)
    json_data=result.json()
    #json.loads(result.data.decode('utf-8'))
    logger.debug('grafana response %s',json_data)
   
    return result


class GrafanaUser(object):
    
    def __init__(self,zibawaID,username,password,email):
        #in order to be able to create or change password we need to pass in data
        #even though sometimes we wont need to use it (or it isnt available)
        self.zibawaID=zibawaID
        self.username=username
        self.password=password
        self.email=email
        self.orgId=None
        
        
        
    
        

    def create(self):
                
        apiurl= "/api/admin/users"
        data={
                "name":str(self.zibawaID),
                "email":self.email,
                "login":self.username,
                "password":self.password
                }
        '''
        data={
            "name":"User",
            "email":"user@graf.com",
            "login":"user",
            "password":"userpassword"
        }   
        '''    
            
        
        result=getFromGrafanaApi(apiurl,data,'POST')
        if (result.status_code==200):
            logger.info('Grafana user created %s,',self.username)
            output=result.json()
            self.id=output['id']
            logger.info('Grafana user created %s with grafana id %s,',self.username,self.id)
            return True
            logger.info('Could not create Grafana user %s error %s,',self.username,result.statuscode)
        #insert except
        logger.info('Could not create Grafana user %s,',self.username)
        return False    
    
    def delete(self):
        #deletes from Grafana via api
        
        try:
            apiurl= "/api/admin/users/"+str(self.id)
            data={}
            result=getFromGrafanaApi(apiurl,data,'DELETE')
            if (result.status_code==200):
                logger.info('Grafana user deleted %s,',self.username)
                return True
            logger.info('Could not delete Grafana user %s error %s,',self.username,result.status_code)
        except:
            pass
        logger.info('Could not delete Grafana user %s,',self.username)
        return False 
                      
        
    
    def exists(self):
        #looks for self via Grafana api
        #adds id to user object...??
        apiurl="/api/users"
        data={}
        try:
            output=getFromGrafanaApi(apiurl,data,'GET')
            results=output.json()
            for result in results:
                logger.debug('checking %s against %s,',result['login'],self.username)
                if result['login']==self.username:
                    self.id=result['id']
                    logger.info('Grafana user found %s,',self.username)
                    return True
        except:
            pass
        logger.info('Couldnt find Grafana User %s,',self.username)
        return False
    
    def fix_permissions(self):
        #this method requires that we have already called get_orgID 
        #this is required because grafana creates users in org with admin role
        #to remove, we need to assign admin user to organization and
        #then change user role
        
        if not(self.role=="Admin"):    
            return True
        else:
            data={
                "loginOrEmail":settings.DASHBOARD['user'],
                "role":"Admin"
                 }
            apiurl="/api/orgs/"+str(self.orgId)+"/users"
            result=getFromGrafanaApi(apiurl,data,'POST')
            if (result.status_code==200):
                logger.info('Admin user added to organization for org %s,', self.username)
                
            #change admin level of user back to editor (grafana creates users with admin level)
            apiurl="/api/orgs/"+str(self.orgId)+"/users/"+str(self.id)
            data={"role":"Editor"}
            result=getFromGrafanaApi(apiurl,data,'PATCH')
            if (result.status_code==200):
                logger.info('Permissions changed for organization for org%s,', self.username)
                return True
        return False
        
    
    def get_orgID(self):
        apiurl="/api/users/"+str(self.id)+"/orgs"
        data={}
        output=getFromGrafanaApi(apiurl,data,'GET')
        results=output.json()
        for result in results:
            logger.debug('found org id: %s,',result['orgId'],)
            if not result['orgId']==1:
                
                self.orgId=result['orgId']
                self.role=result['role']
                logger.info('Grafana org found %s,',self.orgId)
                return True
        logger.info('Couldnt find non admin Grafana Org  %s,',self.username)
        return False    
    
    
    def found_own_org(self):
        #searches for org with name==user.email, if not creates it
        #when configured to do so, Grafana creates orgs automatically for users with name=email
        
        apiurl="/api/orgs"
        data={}
        output=getFromGrafanaApi(apiurl,data,'GET')
        if (output.status_code==200):
            results=output.json()
            for result in results:
                logger.debug('checking %s against %s,',result['name'],self.email)
                if result['name']==self.email:
                    self.orgId=result['id']
                    logger.info('Grafana org found for %s,',self.email)
                    return True
            apiurl="/api/orgs/"
            data={"name": self.email}       
            output=getFromGrafanaApi(apiurl,data,'POST')
            if (output.status_code==200):
                logger.info('Grafana organization created for %s,',self.username)
                result=output.json()
                self.orgId=result['orgId']
                return True
            logger.info('Could not create Grafana org %s error %s,',self.username,output.status_code)
        
        return False
        
    def add_to_own_org(self):
        # adds self to own org as editor (although Grafana seems to create always as admin)
        if (self.found_own_org()):
        
            apiurl="/api/orgs/"+str(self.orgId)+"/users"
            data={
                "loginOrEmail":self.username,
                "role":"Editor"
            }
            output=getFromGrafanaApi(apiurl,data,'POST')
            if (output.status_code==200):
                logger.info('User %s added to Grafana organization %s,',self.username,self.orgId)
                return True
            logger.info('Could not add user to Grafana org %s error %s,',self.username,output.status_code)
            return False
    
    def add_datasource(self):
        
        #change active organization
        #creates influx readonly user if it doesnt already exist and
        #resets password if it does
        
        #ensure that we have found our own orgID to add datasource to
        if not self.found_own_org():
            return False
        #change active organization
        data={}
        apiurl="/api/user/using/"+str(self.orgId)
        result=getFromGrafanaApi(apiurl,data,'POST')
        if not(result.status_code==200):
            logger.warning('unable to change user to organization %s',self.orgId)
            return False 
        
        #check to see if datasource exists once we have changed active organization
        logger.debug('Adding datasource.  Checking if datasource already exists for %s,',self.username)
        if self.datasource_exists():
            logger.debug('datasource already exists %s,',self.username)
            return True
        
               
        
        #add datasource to organization
        DBname= "dab"+str(self.username)
        DBusername="gu"+str(self.username)
        DBpassword=id_generator(size=20)
        
        if (settings.INFLUXDB('use_ssl')):
            Urlprotocol="https://"
        else:
            Urlprotocol="http://"
            
        
        Urlstring= Urlprotocol+settings.INFLUXDB('host')+":"+str(settings.INFLUXDB('port'))
        
        #createInfluxReadOnlyUser for database
        logger.debug('trying to create influx user for datasource %s',DBusername)
        client=getInfluxConnection()
        try:
            result=client.create_user(DBusername, DBpassword, admin=False)
            result=client.grant_privilege('read',DBname,DBusername)
        except:
            #if db user already exists (and has been lost by grafana)then reset password
            result=client.set_user_password(DBusername, DBpassword)
        apiurl= "/api/datasources"
        data={}
        data['name']=DBname
        data['type']="influxdb"
        data['url']=Urlstring
        data['access']="proxy"
        data['basicAuth']=False
        data['password']=DBpassword
        data['user']= DBusername
        data['database']=DBname
        data['isDefault']=True
        
        result=getFromGrafanaApi(apiurl,data,'POST')
        if (result.status_code==200):
            logger.debug('data source added %s',DBname)
            return True
        else:
            logger.warning('could not add datasource %s',result.json())
            return False
                  
    def changeGrafanaPassword(self):
        
        #sets Grafana psw to the psw fed into the GrafanaUser object when created
        #called from psw reset functions in zibawa
        
        #check that user exists in Grafana, and obtain self.id
        if not self.exists():
            return False
        
        apiurl="/api/admin/users/"+str(self.id)+"/password"
        data={"password":self.password
            }
        output=getFromGrafanaApi(apiurl,data,'PUT')
        if (output.status_code==200):
            return True
        return False
    
    def datasource_exists(self):
        #check if grafana user organization has datasource associated
        #if not try to create
        apiurl="/api/datasources"
        datasourcename= "dab"+str(self.username)
        data={}
        output=getFromGrafanaApi(apiurl,data,'GET')
        if (output.status_code==200):
            results=output.json()
            for result in results:
                logger.debug('checking %s against %s,',result['name'],datasourcename)
                if result['name']==datasourcename:
                    self.datasourceID=result['id']
                    logger.info('Grafana datasource found name %s id:%s,',datasourcename,str(self.datasourceID))
                    return True
        #if no datasource found, then try to add datasource
        
        return False
        


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
    #apiurl="/api/orgs/name/"+str(current_user.email)
    apiurl="/api/orgs/name/"+str(current_user.email)
    data={}
         
    try:
        result=getFromGrafanaApi(apiurl,data,'GET')    
        orgID=result['id']
        return orgID
    except Exception as e: 
        logger.critical('Couldnt find Grafana Organization %s,', e)
        return str(e)

def getGrafanaUser(current_user):
    #returns userID username equal to that of current user
    #if fails returns error string
    apiurl="/api/users"
    data={}
    try:
        results=getFromGrafanaApi(apiurl,data,'GET')
        for result in results:
            if result['login']==current_user.username:
                output=testObj("GrafanaUser",True,result['id'])
                logger.info('Grafana user found %s,',current_user.username)
                return output
    except:
        pass
    logger.info('Couldnt find Grafana User %s,',current_user.username)
    output=testObj("GrafanaUser",False,"You need to login to the grafana dashboard, then return here to complete configuration")
        
    return output      

def getGrafanaOrgFromGrafanaUser(grafana_user_ID):
    apiurl="/api/users/"+str(grafana_user_ID)+"/orgs"
    data={}
    try:
        results=getFromGrafanaApi(apiurl,data,'GET')
        result=results[0]
        grafanaOrg=result['id']
        output=testObj("GrafanaOrg",True,result['orgId'])
        logger.info('Grafana org found %s,',result['orgId'])
        return output
    except:
        pass
    output=testObj("GrafanaOrg",False,"not found")
    logger.info('Grafana org not found for userid %s,',grafana_user_ID)
    return output

'''   
def addDataBaseToGrafana(influxTest,grafana_user_id,current_user):

#adds influxDB datasource to Grafana organization based on array of credentials
 
 
 #get Grafana userID (ignore master Admin)
    result=getGrafanaOrgFromGrafanaUser(grafana_user_id)
    orgID=result.message
    if not(result.status):
        return False
    
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
            try:
                result=client.create_user(DBusername, DBpassword, admin=False)
                result=client.grant_privilege('read',influxTest.database,DBusername)
            except:
                #if db user already exists (and has been lost by grafana)then reset password
                result=client.set_user_password(DBusername, DBpassword)
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
    '''

def id_generator(size=10, chars=string.ascii_uppercase + string.digits):
    
    return ''.join(random.choice(chars) for _ in range(size)) 