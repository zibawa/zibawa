from django.test import TestCase
from django.conf import settings
from stack_configs.ldap_functions import createLDAPuser,addToLDAPGroup,removeFromLDAPGroup,getLDAPConn
from stack_configs.stack_functions import testGrafanaUp,testInfluxDB,testConnectToRabbitMQ
import logging
from stack_configs.models import getInfluxConnection
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
        test=testGrafanaUp()
        self.assertEqual(test.status,True)    
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
        