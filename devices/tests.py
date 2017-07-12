from django.test import TestCase,Client
from .models import Device,Section,Channel,Channel_tag
from django.contrib.auth.models import User,Group,Permission
from django.conf import settings
from stack_configs.ldap_functions import createLDAPuser,addToLDAPGroup,removeFromLDAPGroup,getLDAPConn
from stack_configs.influx_functions import getLastTimeInflux
import logging
import datetime
logger = logging.getLogger(__name__)
# Create your tests here.

  
testuser="autodevicetestuser"
test_device_id="autotestdevice"
testemail=testuser+"@autotest.com"
testtopic= "1."+str(test_device_id)+".1.1" #this ties in with the device and channel we create in setup


class DeviceTests(TestCase):

 
    
    @classmethod
    def setUpTestData(cls):
        # Set up data for the whole TestCase
        
        logger.info('tests: settingup device tests')
        cls.group = Group.objects.get_or_create(name='editor')
        
        
        cls.user=User.objects.create(username=testuser,first_name="test",last_name="test",email=testemail,is_superuser=True)
        #create above user in LDAP Note user is not included in any groups unless
        #we specify to do so.
        result=createLDAPuser(cls.user,'supersecret')
        addToLDAPGroup(testuser,'active')
        addToLDAPGroup(testuser,'editor')
        addToLDAPGroup(testuser,'superuser')
        cls.section= Section.objects.create(section_desc="autotestsection",account=cls.user)
        cls.channel_tag= Channel_tag.objects.create(name="mychanneltag",account=cls.user)
        cls.device = Device.objects.create(device_id=test_device_id,account=cls.user,section=cls.section,group="testgroup",subgroup="testsubgroup",latitude=50,longitude=3.53)
        cls.channel = Channel.objects.create(device=cls.device,channel_id=1,time_tag_year=True,time_tag_month=True,time_tag_day=True,time_tag_hour=True,elapsed_since_same_ch=True,elapsed_since_diff_ch=True,upper_warning= 2000,lower_warning=-5.3, alarm_logs=True,alarm_email=True)
        
    def Test_reset_psw(self):

        # First check for the default behavior
        #will need to delete user from LDAP...
        logger.info('tests: logging in test user')
        response= self.client.login(username=testuser, password='supersecret')
        logger.info('tests: getting devices resetPsw (creates device on ldap)')
        response=self.client.get('/devices/1/resetPsw/')
        self.assertEqual(response.context['mqttConnResult'],0)
        self.assertEqual(response.status_code, 200)
        
        
        logger.info('tests: getting devices resetPsw 2nd time, modifes existing device on ldap')
        response=self.client.get('/devices/1/resetPsw/')
        self.assertEqual(response.context['mqttConnResult'],0)
        self.assertEqual(response.status_code, 200)
        
    def Test_admin_pages(self):
        #get all pages
        response= self.client.login(username=testuser, password='supersecret')
        response=self.client.get('/devices/1/resetPsw/')
        self.assertEqual(response.status_code, 200)
        #make sure user has permissions, in zibawa and ldap!
        admin_pages = [
            "/admin/",
            "/admin/devices/channel_tag/",
            "/admin/devices/channel_tag/add/",
            "/admin/devices/device/",
            "/admin/devices/device/add/",
            "/admin/devices/section/",
            "/admin/devices/section/add/",
            "/admin/hooks/hook/add/",
            "/admin/hooks/hook/",
            "/admin/hooks/person/add/",
            "/admin/hooks/person/",
            "/admin/hooks/place/add/",
            "/admin/hooks/place/",
            "/admin/hooks/product/add/",
            "/admin/hooks/product/"
            
        ]
        for page in admin_pages:
            logger.info('testing GET page %s',page)
            response = self.client.get(page)
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
        
        messages={
            "{'value':1,'hooks':['peach','apricot']}",
            "{'text'}",
            "{text}",
            "10",
            "10.1",
            "|@#~¬''~{¬#''~@@{[]",
            "{'timestamp': '2017-02-21T18:51:29+00:00', 'value': '2189.22','status':'testing'}"
            
            }
            
            
            
            
        for message in messages:
            #response=self.client.post('/devices/testMessage/', {'topic': testtopic, 'message': '{"timestamp": "2017-02-21T18:51:29+00:00", "value": "2189.22","status":"autotesting"}'})
            response=self.client.post('/devices/testMessage/', {'topic': testtopic, 'message': message})
            
            self.assertEqual(response.status_code, 200)
    
    def Test_get_last_influx(self):
        #requires to be run after Test test message
        logger.info('tests: get last influx')
        result=getLastTimeInflux('dab'+str(testuser),test_device_id,'1')
        logger.info('tests: get last influx %s',result)
        self.assertEqual(isinstance(result, datetime.datetime),True)
    
    def test_All(self):
        self.Test_reset_psw()
        self.Test_test_message()
        self.Test_get_last_influx()
        #self.Test_admin_pages()
    
    def tearDown1(self):
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
        


class CertDownloadTests(TestCase):            
    
    
    def test_download_CA_cert(self):    
       
        logger.info('tests: download_CA_cert')
        response=self.client.get('/devices/download_CA_cert/')
        self.assertEqual(response.status_code, 200)
        
    