from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User,Group
from stack_configs.ldap_functions import getLDAPConnWithUser
import logging
logger = logging.getLogger(__name__)

class OpenLdapBackend(object):
    """
    Authenticate against openLdap using LDAP3 library
    
    """

    def authenticate(self, username, password):
        
        #authenticate with cn=username
        #users who are introduced via phpLDAPadmin may get different cn and uid and would not
        #authenticate. 
        ldapAttributes=[]
        for userAttribute, ldapAttribute in settings.LDAP3_ATTR_MAP.items():
            ldapAttributes.append(ldapAttribute)
        
        dn= str("cn=")+str(username)+str(",")+str(settings.AUTH_LDAP_USERS_OU_DN)
        logger.debug('connecting to ldap as user %s ',dn)
        conn=getLDAPConnWithUser(dn,password)
        if (conn.bound):
             
            logger.debug('ldap user found %s',dn)
            filter_string='(&(objectclass=posixGroup)(memberUid='+str(username)+'))'                      
            #con.search(settings.AUTH_LDAP_GROUPS_OU_DN, '(&(objectclass=posixGroup)(cn=active)(memberUid=rtamudo))',attributes=['cn','gidNumber']) 
            conn.search(settings.AUTH_LDAP_GROUPS_OU_DN, filter_string,attributes=['cn','gidNumber']) 
            grouplist=[]
            for entry in conn.entries:
                #print(entry.dn)
                logger.debug('user %s is a member of group %s',username,entry)
                grouplist.append(entry.cn)
            if (settings.LDAP3_USER_FLAGS_BY_GROUP['is_active']) in grouplist:
                    
                try:
                    user = User.objects.get(username=username)
                    logger.debug('user %s exists ', username)
                except User.DoesNotExist:
                    logger.debug('creating new user in zibawa from ldap for %s',username)
                # Create a new user. There's no need to set a password
                # because only the password from settings.py is checked.
                    user = User(username=username)
                
                #update attributes for all users new and old according to LDAP
                logger.debug('updating attributes for %s',username)
                user.is_active = settings.LDAP3_USER_FLAGS_BY_GROUP['is_active'] in grouplist
                user.is_staff = settings.LDAP3_USER_FLAGS_BY_GROUP['is_staff'] in grouplist
                user.is_superuser = settings.LDAP3_USER_FLAGS_BY_GROUP['is_superuser'] in grouplist
                
                search_filter= '(&(objectclass=inetOrgPerson)(uid='+str(username)+'))'
                logger.debug('searching for attributes for %s',search_filter)
                conn.search(settings.AUTH_LDAP_USERS_OU_DN, search_filter, attributes=ldapAttributes)
                                
                #update user Attributes according to mapping defined in settings.py
                for userAttribute, ldapAttribute in settings.LDAP3_ATTR_MAP.items():
                    setattr(user, userAttribute,getattr(conn.entries[0], ldapAttribute))         
                user.save()
                syncUserGroups(user,grouplist)
                                
                return user
        
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
        
        
def syncUserGroups(user,grouplist):
    #add to groups that user is not in. Currently do not remove.
    for group in grouplist:
        try:
            g = Group.objects.get(name=group) 
            g.user_set.add(user.object)        
        except:
            pass    