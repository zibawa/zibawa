from django.test import TestCase,Client
from django.conf import settings
from stack_configs.models import getLDAPConn
import logging
#from chardet.test import result

logger = logging.getLogger(__name__)

#front tests
# Create your tests here.

testuser='autotestuser2'

class CreateAccountTestCase(TestCase):

    def test_createAccount(self):

        # First check for the default behavior
        #will need to delete user from LDAP...
        response=self.client.post('/createAccount/', {'username': testuser, 'password': 'secret', 'first_name':'fred','last_name':'test', 'email':'fred@me.com'})
        self.assertRedirects(response, '/thanks/')
    def test_passwordChange(self):
        
        response= self.client.login(username=testuser, password='secret')
        response=self.client.post('/change_password/', {'old_password': 'secret', 'new_password1': 'verysecret', 'new_password2':'verysecret'})
        self.assertRedirects(response, '/change_password/done/')
                
    def test_cleanUp(self):
        dn= str("cn=")+str(testuser)+str(",")+str(settings.AUTH_LDAP_USERS_OU_DN)
        con= getLDAPConn()
        result=con.delete(dn)
        logger.info('delete result %s', result)
        self.assertEqual(result,True)
        
'''
class ChangePasswordTestCase(TestCase):

    def test_change_password(self):

        # First check for the default behavior
        #will need to delete user from LDAP...
        response= self.client.login(username='fred', password='secret')
        response=self.client.post('/change_password/', {'old_password': 'secret', 'new_password1': 'verysecret', 'new_password2':'verysecret'})
        self.assertRedirects(response, '/change_password/done/')
                '''