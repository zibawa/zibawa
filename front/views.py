
#from urllib.parse import urlparse, urlunparse

from django.conf import settings
# Avoid shadowing the login() and logout() views below.
from django.contrib.auth import (
    REDIRECT_FIELD_NAME, get_user_model, login as auth_login,
    logout as auth_logout, update_session_auth_hash,
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import (
    AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm,
)
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponseRedirect, QueryDict
from django.shortcuts import resolve_url
from django.shortcuts import render

from django.template.response import TemplateResponse
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
#from django.utils.deprecation import RemovedInDjango21Warning
from django.utils.encoding import force_text
from django.utils.http import is_safe_url, urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

UserModel = get_user_model()



from django.contrib.auth.models import User
from django.http import HttpResponse


from django.template import loader

import ldap.modlist
import random
import string
import user

from forms import UserForm
from stack_configs.models import addToLDAPGroup,resetLDAPpassword
import logging

LOGGER = logging.getLogger(__name__)
# Create your views here.
# Create your views here.
#from django.contrib.auth.forms import UserCreationForm
def index(request):
    template = loader.get_template('welcome.html')
    result="welcome"
    context = {
         'content':result,
         'has_permission':request.user.is_authenticated,
         'is_popup':False,
         'title':'welcome!'
    }
    return HttpResponse(template.render(context, request))


   

def createAccount(request):
    template = loader.get_template('admin/base_site.html')
    
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            new_user = User.objects.create_user(**form.cleaned_data)
            new_user.is_staff=True 
            new_user.save()
           
            
            context =initializeAccount(new_user,password)
            
            # redirect, or however you want to get to the main view
            return HttpResponseRedirect('/devices/testMessage/')
    else:
        form = UserForm() 

    return render(request, 'form.html', {'form': form}) 
    


def thanks(request):
    
    template = loader.get_template('admin/base_site.html')
    
        
    context = {
         'content':'Thanks. Please log in to your dashboard',
         'title':'Your account has been created'
    }
    return HttpResponse(template.render(context, request))
    

def id_generator(size=10, chars=string.ascii_uppercase + string.digits):
    
    return ''.join(random.choice(chars) for _ in range(size))


def initializeAccount(new_user,password):
    #updates LDAP with user data
    
     
    con = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
    con.simple_bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)
    
   
    
    dn= "cn="+str(new_user.username)+","+settings.AUTH_LDAP_USERS_OU_DN
    modlist={}
    modlist['objectClass']=["inetOrgPerson", "posixAccount", "shadowAccount"]
    modlist['sn']= str(new_user.last_name)
    modlist['givenName']= str(new_user.first_name)
    modlist['mail']= str(new_user.email)
    modlist['cn']= str(new_user.username)
    # modlist['displayName']= str(new_user.id)
    modlist['uid']= str(new_user.username)
    modlist['uidNumber']= str(new_user.id)
    modlist['gidNumber']= str(settings.AUTH_LDAP_USERS_DEFAULT_GID)
    modlist['homeDirectory']="/home/zibawa/"+str(new_user.username)
    modlist['userPassword']= str(password)
    
            
# addModList transforms your dictionary into a list that is conform to ldap input.
    result = con.add_s(dn, ldap.modlist.addModlist(modlist))
    addToLDAPGroup(new_user.username,'active')
    addToLDAPGroup(new_user.username,'editor') 
    #addToLDAPGroup(new_user,'public')

# Doesn't need csrf_protect since no-one can guess the URL
@sensitive_post_parameters()
@never_cache
def zibawa_password_reset_confirm(request, uidb64=None, token=None,
                           template_name='registration/password_reset_confirm.html',
                           token_generator=default_token_generator,
                           set_password_form=SetPasswordForm,
                           post_reset_redirect=None,
                           extra_context=None):
    """
    ZIBAWA NOTE. THIS VIEW CODE IS COPIED FROM DJANGO DEFAULT VIEW WITH MINOR
    MODIFICATIONS TO UPDATE PASSWORD IN LDAP (INSTEAD OF THE DJANGO DATABASE)
    https://github.com/django/django/blob/master/django/contrib/auth/views.py
    
    Check the hash in a password reset link and present a form for entering a
    new password.

    warnings.warn("The password_reset_confirm() view is superseded by the "
                  "class-based PasswordResetConfirmView().",
                  RemovedInDjango21Warning, stacklevel=2)"""
    assert uidb64 is not None and token is not None  # checked by URLconf
    if post_reset_redirect is None:
        post_reset_redirect = reverse('password_reset_complete')
    else:
        post_reset_redirect = resolve_url(post_reset_redirect)
    try:
        # urlsafe_base64_decode() decodes to bytestring
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = UserModel._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None
    if user is not None and token_generator.check_token(user, token):
        validlink = True
        title = _('Enter new password')
        if request.method == 'POST':
            form = set_password_form(user, request.POST)
            if form.is_valid():
                form.save()
                #ZIBAWA MODIFICATIONS START HERE
                user_dn= "cn="+str(user.username)+","+settings.AUTH_LDAP_USERS_OU_DN
                new_password = form.cleaned_data['new_password1']
                result= resetLDAPpassword(user_dn,new_password)
                try:
                    #ldap should return empty array in position 1 if successful
                    if result[1]==[]:
                        LOGGER.debug('reset LDAP password %s,', result)  
                        return HttpResponseRedirect(post_reset_redirect)
                                            
                except:
                    result=None
                    pass
                #if result from LDAP is not what we expect, or if no result
                LOGGER.warning('couldnt reset LDAP password %s,', result)  
                title = _('Could not reset LDAP password')
                #ZIBAWA MODIFICATIONS END HERE
                
                
        else:
            form = set_password_form(user)
    else:
        validlink = False
        form = None
        title = _('Password reset unsuccessful')
    context = {
        'form': form,
        'title': title,
        'validlink': validlink,
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


@sensitive_post_parameters()
@csrf_protect
@login_required
def zibawa_password_change(request,
                    template_name='registration/password_change_form.html',
                    post_change_redirect=None,
                    password_change_form=PasswordChangeForm,
                    extra_context=None):
    '''warnings.warn("The password_change() view is superseded by the "
                  "class-based PasswordChangeView().",
                  RemovedInDjango21Warning, stacklevel=2)'''
    if post_change_redirect is None:
        post_change_redirect = reverse('password_change_done')
    else:
        post_change_redirect = resolve_url(post_change_redirect)
    if request.method == "POST":
        form = password_change_form(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            # Updating the password logs out all other sessions for the user
            # except the current one.
           
            #ZIBAWA MODIFICATIONS START HERE
            user_dn= "cn="+str(request.user.username)+","+settings.AUTH_LDAP_USERS_OU_DN
            new_password = form.cleaned_data['new_password1']
            result= resetLDAPpassword(user_dn,new_password)
            try:
                #ldap should return empty array in position 1 if successful
                if result[1]==[]:
                    LOGGER.debug('reset LDAP password %s,', result)  
                    update_session_auth_hash(request, form.user)
                    return HttpResponseRedirect(post_change_redirect)
                                            
            except:
                result=None
                pass
            #if result from LDAP is not what we expect, or if no result
            LOGGER.warning('couldnt reset LDAP password %s,', result)  
            
            context = {
                 'form': form,
                 'title': _('Could not reset LDAP password'),
                 }
            return TemplateResponse(request, template_name, context)
            #ZIBAWA MODIFICATIONS END HERE
                
                               
            
    else:
        form = password_change_form(user=request.user)
    context = {
        'form': form,
        'title': _('Password change'),
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


