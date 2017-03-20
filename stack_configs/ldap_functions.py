from ldap3 import Server, Connection,ALL,MODIFY_ADD,MODIFY_REPLACE,MODIFY_DELETE,Tls
from django.conf import settings
import logging
import ssl
#from chardet.test import result

logger = logging.getLogger(__name__)
# Create your models here.


def createLDAPDevice(new_device,password):
    #returns true or false uses LDAP3  
    uidNumber= str(new_device.id + 1000000)
    
    con= getLDAPConn()
    dn= str("cn=")+str(new_device.device_id)+str(",")+str(settings.AUTH_LDAP_USERS_OU_DN)
    result=con.add(dn, 'inetOrgPerson', {
        'givenName': 'device', 
        'sn': 'device',
        'mail': 'dontuse@mail.com',
        'cn': new_device.device_id,
        'displayName': new_device.id,
        'uid': new_device.device_id,
        'userPassword':password,
        })
    con.unbind()
    logger.info('create ldap device %s',result)
    return result





def getLDAPConn():
    #ldap3
    tls = Tls(validate=ssl.CERT_REQUIRED, version=ssl.PROTOCOL_TLSv1, ca_certs_file=settings.LDAP3['path_to_ca_cert'])
    server = Server(settings.AUTH_LDAP_SERVER_URI, get_info=ALL,tls=tls)
    logger.info('Connecting to ldap %s',settings.AUTH_LDAP_SERVER_URI )
   
    con = Connection(server,settings.AUTH_LDAP_BIND_DN,settings.AUTH_LDAP_BIND_PASSWORD,auto_bind=False,raise_exceptions=True)
    con.open()
    
    if settings.LDAP3['use_start_tls']:
        con.start_tls()
    con.bind()    
    return con


def createLDAPuser(new_user,password):
    #returns true or false uses LDAP3  
    con= getLDAPConn()
    dn= str("cn=")+str(new_user.username)+str(",")+str(settings.AUTH_LDAP_USERS_OU_DN)
    logger.info('createldap user dn %s',dn)
    result=con.add(dn, 'inetOrgPerson', {
        'givenName': new_user.first_name, 
        'sn': new_user.last_name,
        'mail': new_user.email,
        'cn': new_user.username,
        'displayName': str(new_user.id),
        'uid': new_user.username,
        'userPassword':password,
        })
    con.unbind()
    logger.info('createldap user result %s',result)
    return result

def addToLDAPGroup(user_name,group_name):
    
    #returns true or false uses LDAP3  
    con= getLDAPConn()
    group_dn= str("cn=")+str(group_name)+str(",")+str(settings.AUTH_LDAP_GROUPS_OU_DN)
    logger.info('add user %s ToLdapgroup %s',user_name,group_name)
    
    result=con.modify(group_dn,
                      {'memberUid': (MODIFY_ADD, [user_name])
    })
    
    logger.info ("add group result is %s", result )
    con.unbind()
    return result

def removeFromLDAPGroup(user_name,group_name):
    #this is used in testing
    #returns true or false uses LDAP3  
    con= getLDAPConn()
    group_dn= str("cn=")+str(group_name)+str(",")+str(settings.AUTH_LDAP_GROUPS_OU_DN)
    result=con.modify(group_dn,
                      {'memberUid': (MODIFY_DELETE, [user_name])
    })
    
    logger.info ("remove %s from group %s result is %s", user_name, group_name, result )
    con.unbind()
    return result



def resetLDAPpassword(user_dn,new_password):
     #returns True or False uses LDAP3  
    con= getLDAPConn()
    #group_dn= str("cn=")+str(group_name)+str(",")+str(settings.AUTH_LDAP_GROUPS_OU_DN)
    result=con.modify(user_dn,
                      {'userPassword': (MODIFY_REPLACE, [new_password])
    })
    
   
    logger.info('reset LDAP password for: %s', user_dn) 
    logger.info('result of psw reset: %s', result)
    con.unbind()
    return result

