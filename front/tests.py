from django.test import TestCase,Client
from django.conf import settings
from stack_configs.ldap_functions import getLDAPConn,removeFromLDAPGroup
import logging
#from chardet.test import result

logger = logging.getLogger(__name__)

#front tests
# Create your tests here.

testuser='autotestuser2'

class CreateAccountTestCase(TestCase):
#note test which start in capitals only run when called by a test starting in small letter
#this is to force the tests to run in sequence
    
    
    def Test_create_client(self):
                
        logger.info('test start setUpCreateAccountTest ' )
        # First check for the default behavior
        #will need to delete user from LDAP...
        logger.info('test calling create_account')
        response=self.client.post('/create_account/', {'username': testuser, 'password': 'secret', 'first_name':'fred','last_name':'test', 'email':'fred@me.com'})
        self.assertRedirects(response, '/thanks/')
        
        #ensure cant login with a username that already exists
        logger.info('test trying to create username which already exists')
        response=self.client.post('/create_account/', {'username': testuser, 'password': 'secret', 'first_name':'fred','last_name':'test', 'email':'fred2@me.com'})
        self.assertEqual(response.status_code, 200)
        #ensure cant login with email that already exists
        logger.info('test trying to create username with email which already exists')
        response=self.client.post('/create_account/', {'username': 'differenttestuser', 'password': 'secret', 'first_name':'fred','last_name':'test', 'email':'fred@me.com'})
        self.assertEqual(response.status_code, 200)
        
    def test_passwordChange(self):
        
        self.Test_create_client()
        logger.info('test starting test password change')
        logger.info('test logging in')
        response= self.client.login(username=testuser, password='secret')
        logger.info('test post to change password')
        response=self.client.post('/change_password/', {'old_password': 'secret', 'new_password1': 'verysecret', 'new_password2':'verysecret'})
        self.assertRedirects(response, '/change_password/done/')
        logger.info('test logging out')
        response=self.client.get('/logout/')
        self.assertRedirects(response, '/login/')
        logger.info('test get login page')
        response=self.client.get('/login/')
        self.assertEqual(response.status_code, 200)
        logger.info('test login with new password')
        response= self.client.login(username=testuser, password='verysecret')
             
    
    
    
        
    
    def tearDown(self):
        logger.info('test teardown CreateAccount')
        removeFromLDAPGroup(testuser,'active')
        removeFromLDAPGroup(testuser,'editor')
        
        dn= str("cn=")+str(testuser)+str(",")+str(settings.AUTH_LDAP_USERS_OU_DN)
        con= getLDAPConn()
        result=con.delete(dn)
        logger.info('delete result in test_cleanup %s', result)
        self.assertEqual(result,True)    
