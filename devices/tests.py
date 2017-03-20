from django.test import TestCase,Client
from .models import Device,Section
from django.contrib.auth.models import User
from django.conf import settings
from stack_configs.ldap_functions import createLDAPuser,removeFromLDAPGroup,getLDAPConn
import logging
logger = logging.getLogger(__name__)
# Create your tests here.

  
testuser="autotestuser"
test_device_id="autotestdevice"

class MyTests(TestCase):

 
    
    @classmethod
    def setUpTestData(cls):
        # Set up data for the whole TestCase
        
        
        cls.user=User.objects.create(username=testuser,first_name="test",last_name="test")
        #create above user in LDAP Note user is not included in any groups unless
        #we specify to do so.
        result=createLDAPuser(cls.user,'supersecret')
        cls.section= Section.objects.create(section_desc="autotestsection",account=cls.user)
        cls.device = Device.objects.create(device_id=test_device_id,account=cls.user,section=cls.section)
    
    def test_reset_psw(self):

        # First check for the default behavior
        #will need to delete user from LDAP...
        response= self.client.login(username='autotestuser', password='supersecret')
        response=self.client.get('/devices/1/resetPsw/')
        self.assertEqual(response.status_code, 200)
        
        
    def tearDown(self):
        #remove device from ldap
        removeFromLDAPGroup(test_device_id,'device')
       
        dn= str("cn=")+str(test_device_id)+str(",")+str(settings.AUTH_LDAP_USERS_OU_DN)
        con= getLDAPConn()
        result=con.delete(dn)
        logger.info('delete device in test_cleanup %s', result)
        
        #remove test user from ldap if necessary, also remove from groups.
        #removeFromLDAPGroup(testuser,'active')
        #removeFromLDAPGroup(testuser,'editor')
        dn= str("cn=")+str(testuser)+str(",")+str(settings.AUTH_LDAP_USERS_OU_DN)
        con= getLDAPConn()
        result=con.delete(dn)
        logger.info('delete result in test_cleanup %s', result)
        
            