from django.test import TestCase
from django.test import TestCase,Client
from devices.models import Device,Section
from django.contrib.auth.models import User,Group,Permission
from django.conf import settings
from stack_configs.ldap_functions import createLDAPuser,addToLDAPGroup,removeFromLDAPGroup,getLDAPConn
import logging
logger = logging.getLogger(__name__)
# Create your tests here.

  
testuser="autosimulatortestuser"
test_device_id="autotestdevice"
# Create your tests here.
class SimulatorTests(TestCase):

 
    
    @classmethod
    def setUpTestData(cls):
        # Set up data for the whole TestCase
        
        logger.info('tests: settingup simulator tests')
        cls.group = Group.objects.get_or_create(name='editor')
        
        
        cls.user=User.objects.create(username=testuser,first_name="test",last_name="test",is_superuser=True)
        #create above user in LDAP Note user is not included in any groups unless
        #we specify to do so.
        result=createLDAPuser(cls.user,'supersecret')
        addToLDAPGroup(testuser,'active')
        addToLDAPGroup(testuser,'editor')
        addToLDAPGroup(testuser,'superuser')
        cls.section= Section.objects.create(section_desc="autotestsection",account=cls.user)
        cls.device = Device.objects.create(device_id=test_device_id,account=cls.user,section=cls.section)
    

        
    def Test_admin_pages(self):
        #get all pages
        response= self.client.login(username=testuser, password='supersecret')
        
        #make sure user has permissions, in zibawa and ldap!
        admin_pages = [
            
            "/admin/simulator/simulation/",
            "/admin/simulator/simulation/add/",
            "/admin/simulator/thing/",
            "/admin/simulator/thing/add/",
           
            
        ]
        for page in admin_pages:
            logger.info('testing GET page %s',page)
            response = self.client.get(page)
            self.assertEqual(response.status_code, 200)
            
      
    
        
    
    def test_All(self):
        
        self.Test_admin_pages()
    
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
        
            