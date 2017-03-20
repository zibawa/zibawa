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

    def Test_createAccount(self):

        # First check for the default behavior
        #will need to delete user from LDAP...
        response=self.client.post('/create_account/', {'username': testuser, 'password': 'secret', 'first_name':'fred','last_name':'test', 'email':'fred@me.com'})
        self.assertRedirects(response, '/thanks/')
        
        #ensure cant login with a username that already exists
        response=self.client.post('/create_account/', {'username': testuser, 'password': 'secret', 'first_name':'fred','last_name':'test', 'email':'fred2@me.com'})
        self.assertEqual(response.status_code, 200)
        #ensure cant login with email that already exists
        response=self.client.post('/create_account/', {'username': 'differenttestuser', 'password': 'secret', 'first_name':'fred','last_name':'test', 'email':'fred@me.com'})
        self.assertEqual(response.status_code, 200)
        
    def Test_passwordChange(self):
        
        response= self.client.login(username=testuser, password='secret')
        response=self.client.post('/change_password/', {'old_password': 'secret', 'new_password1': 'verysecret', 'new_password2':'verysecret'})
        self.assertRedirects(response, '/change_password/done/')
        response=self.client.get('/logout/')
        self.assertRedirects(response, '/login/')
        response=self.client.get('/login/')
        self.assertEqual(response.status_code, 200)
        response= self.client.login(username=testuser, password='verysecret')
             
    def Test_cleanUp(self):
        
        removeFromLDAPGroup(testuser,'active')
        removeFromLDAPGroup(testuser,'editor')
        
        dn= str("cn=")+str(testuser)+str(",")+str(settings.AUTH_LDAP_USERS_OU_DN)
        con= getLDAPConn()
        result=con.delete(dn)
        logger.info('delete result in test_cleanup %s', result)
        self.assertEqual(result,True)
    
    
    def test_Create_Sequence(self):
        #self.Test_cleanUp()
        self.Test_createAccount()
        self.Test_passwordChange()
        self.Test_cleanUp()
        
