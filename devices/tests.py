from django.test import TestCase,Client
from .models import Device,Section
from django.contrib.auth.models import User,Group
from django.conf import settings
from stack_configs.ldap_functions import createLDAPuser,addToLDAPGroup,removeFromLDAPGroup,getLDAPConn
import logging
logger = logging.getLogger(__name__)
# Create your tests here.

  
testuser="autodevicetestuser"
test_device_id="autotestdevice"

class DeviceTests(TestCase):

 
    
    @classmethod
    def setUpTestData(cls):
        # Set up data for the whole TestCase
        
        logger.info('tests: settingup device tests')
        cls.group = Group.objects.get_or_create(name='editor')
        cls.user=User.objects.create(username=testuser,first_name="test",last_name="test")
        #create above user in LDAP Note user is not included in any groups unless
        #we specify to do so.
        result=createLDAPuser(cls.user,'supersecret')
        addToLDAPGroup(testuser,'active')
        addToLDAPGroup(testuser,'editor')
        cls.section= Section.objects.create(section_desc="autotestsection",account=cls.user)
        cls.device = Device.objects.create(device_id=test_device_id,account=cls.user,section=cls.section)
    
    def Test_reset_psw(self):

        # First check for the default behavior
        #will need to delete user from LDAP...
        logger.info('tests: logging in test user')
        response= self.client.login(username=testuser, password='supersecret')
        logger.info('tests: getting devices resetPsw')
        response=self.client.get('/devices/1/resetPsw/')
        self.assertEqual(response.status_code, 200)
    
    def Test_test_message(self):    
        logger.info('tests: logging in test user')
        response= self.client.login(username=testuser, password='supersecret')
        logger.info('tests: getting devices testMessage')
        response=self.client.get('/devices/testMessage/',follow=True)
        #last_url, status_code = response.redirect_chain[-1]
        #print(last_url)
        self.assertEqual(response.status_code, 200)
        logger.info('tests: posting to devices testMessage')
        response=self.client.post('/devices/testMessage/', {'topic': '1.autotest.1.1', 'message': '{"timestamp": "2017-02-21T18:51:29+00:00", "value": "2189.22","status":"testing"}'})
        self.assertEqual(response.status_code, 200)
        
    
    def test_All(self):
        self.Test_reset_psw()
        self.Test_test_message()
    
    def tearDown(self):
        #remove device from ldap
        logger.info('tests: tearDown device tests')
        removeFromLDAPGroup(test_device_id,'device')
       
        dn= str("cn=")+str(test_device_id)+str(",")+str(settings.AUTH_LDAP_USERS_OU_DN)
        con= getLDAPConn()
        result=con.delete(dn)
        logger.info('delete device in test_cleanup %s', result)
        
        #remove test user from ldap if necessary, also remove from groups.
        removeFromLDAPGroup(testuser,'active')
        removeFromLDAPGroup(testuser,'editor')
        dn= str("cn=")+str(testuser)+str(",")+str(settings.AUTH_LDAP_USERS_OU_DN)
        con= getLDAPConn()
        result=con.delete(dn)
        logger.info('delete result in test_cleanup %s', result)
        
            