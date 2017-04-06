from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User
from stack_configs.ldap_functions import createLDAPuser,addToLDAPGroup,removeFromLDAPGroup,getLDAPConn
from stack_configs.stack_functions import createInfluxDB,testConnectToRabbitMQ
from .grafana_functions import getFromGrafanaApi,GrafanaUser
import logging
from stack_configs.influx_functions import getInfluxConnection
logger = logging.getLogger(__name__)
# Create your tests here.
#these test are to check connectivity of the different apis

class StackTests(TestCase):

 
    
    @classmethod
    def setUpTestData(cls):
        # Set up data for the whole TestCase
        
        pass
    
    def test_bind_LDAP(self):
        logger.info('tests: trying to bind to ldap')
        conn=getLDAPConn()
        self.assertEqual(conn.bound,True)
        
    def test_bind_influx(self):
        logger.info('tests: trying to bind to influx')
        conn=getInfluxConnection()
        try:
            conn.get_list_database()
            result=True
        except Exception as e:
            logger.info('influx get list database failed %s',e)
            result=False
        
        self.assertEqual(result,True)
        
        
    def test_bind_grafana(self):
        
        logger.info('tests: trying to bind to grafana')
        data={}
        apiurl="/api/org"
        result=getFromGrafanaApi(apiurl, data,'GET')
        self.assertEqual('result' in locals(),True)    
        # First check for the default behavior
        #will need to delete user from LDAP...
        '''
        response= self.client.login(username=testuser, password='supersecret')
        logger.info('tests: getting devices resetPsw')
        response=self.client.get('/devices/1/resetPsw/')
        self.assertEqual(response.status_code, 200)
        '''
    def test_bind_rabbit(self):
        
        logger.info('tests: trying to bind to rabbit')
        test=testConnectToRabbitMQ()
        self.assertEqual(test.status,True)   
    
    
    


class GrafanaTests(TestCase):

 
    
    @classmethod
    def setUpTestData(cls):
        # createZibawaUser and GrafanaUser
        
        
        pass
    
    def test_get_grafana_user(self):
        #do not seem to be able to create users with the same name or email as
        #deleted users..so do not create users unnecesarily 
        zibawa_user=User.objects.create(username="autotestuser4",first_name="test",last_name="test",email="autotest4@me.com")
        grafana_user=GrafanaUser(zibawa_user.id, zibawa_user.username,"supersecret",zibawa_user.email)
       
        logger.info('tests: trying to find grafana user')
        if not (grafana_user.exists()):
        
            logger.info('tests: trying to create grafana user')
            self.assertEqual(grafana_user.create(),True)
        
        logger.info('tests: trying to find grafana user')
        self.assertEqual(grafana_user.exists(),True)
        logger.info('tests: trying to find non grafana admin org')
        if not (grafana_user.get_orgID()):
            grafana_user.add_to_own_org()
        self.assertEqual(grafana_user.get_orgID(),True)
        self.assertEqual(grafana_user.fix_permissions(),True)
        self.assertEqual(grafana_user.add_datasource(),True)
    
    def tearDown(self):
        #delete GrafanaUser
        #check doesnt exist anymore
        pass
    
    