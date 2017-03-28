from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User,Group
from stack_configs.ldap_functions import getLDAPConnWithUser
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission

import logging
logger = logging.getLogger(__name__)

class OpenLdapBackend(object):
    """
    Authenticate against openLdap using LDAP3 library
    
    The authenticate function and groupsync function is modified using LDAP3
    All other functions are copied as is from 
    https://github.com/django/django/blob/master/django/contrib/auth/backends.py#L1
    
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
        try:
            conn=getLDAPConnWithUser(dn,password)
        except:
            return None
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
        
    def user_can_authenticate(self, user):
        """
        Reject users with is_active=False. Custom user models that don't have
        that attribute are allowed.
        """
        is_active = getattr(user, 'is_active', None)
        return is_active or is_active is None

    def _get_user_permissions(self, user_obj):
        return user_obj.user_permissions.all()

    def _get_group_permissions(self, user_obj):
        user_groups_field = get_user_model()._meta.get_field('groups')
        user_groups_query = 'group__%s' % user_groups_field.related_query_name()
        return Permission.objects.filter(**{user_groups_query: user_obj})

    def _get_permissions(self, user_obj, obj, from_name):
        """
        Return the permissions of `user_obj` from `from_name`. `from_name` can
        be either "group" or "user" to return permissions from
        `_get_group_permissions` or `_get_user_permissions` respectively.
        """
        if not user_obj.is_active or user_obj.is_anonymous or obj is not None:
            return set()

        perm_cache_name = '_%s_perm_cache' % from_name
        if not hasattr(user_obj, perm_cache_name):
            if user_obj.is_superuser:
                perms = Permission.objects.all()
            else:
                perms = getattr(self, '_get_%s_permissions' % from_name)(user_obj)
            perms = perms.values_list('content_type__app_label', 'codename').order_by()
            setattr(user_obj, perm_cache_name, set("%s.%s" % (ct, name) for ct, name in perms))
        return getattr(user_obj, perm_cache_name)

    def get_user_permissions(self, user_obj, obj=None):
        """
        Return a set of permission strings the user `user_obj` has from their
        `user_permissions`.
        """
        return self._get_permissions(user_obj, obj, 'user')

    def get_group_permissions(self, user_obj, obj=None):
        """
        Return a set of permission strings the user `user_obj` has from the
        groups they belong.
        """
        return self._get_permissions(user_obj, obj, 'group')

    def get_all_permissions(self, user_obj, obj=None):
        if not user_obj.is_active or user_obj.is_anonymous or obj is not None:
            return set()
        if not hasattr(user_obj, '_perm_cache'):
            user_obj._perm_cache = self.get_user_permissions(user_obj)
            user_obj._perm_cache.update(self.get_group_permissions(user_obj))
        return user_obj._perm_cache

    def has_perm(self, user_obj, perm, obj=None):
        if not user_obj.is_active:
            return False
        return perm in self.get_all_permissions(user_obj, obj)

    def has_module_perms(self, user_obj, app_label):
        """
        Return True if user_obj has any permissions in the given app_label.
        """
        if not user_obj.is_active:
            return False
        for perm in self.get_all_permissions(user_obj):
            if perm[:perm.index('.')] == app_label:
                return True
        return False

        
def syncUserGroups(user,grouplist):
    #add to groups that user is not in. Currently do not remove.
    for group_name in grouplist:
        logger.debug('trying to add user to group %s',group_name)
        try:
            group = Group.objects.filter(name=group_name)[0]
            if not user.groups.filter(name=group_name).exists(): 
                user.groups.add(group)  
                logger.debug('added to %s',group)   
        except:
            logger.debug('group %s not found ',group_name)    