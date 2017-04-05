from __future__ import absolute_import

#from urllib.parse import urlparse, urlunparse

from builtins import str
from builtins import range
from django.conf import settings
# Avoid shadowing the login() and logout() views below.
from django.contrib.auth import (
    REDIRECT_FIELD_NAME, get_user_model, login as auth_login,
    logout as auth_logout, update_session_auth_hash,
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import (
    AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm,AdminPasswordChangeForm,
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
import random
import string
#import user

from .forms import UserForm
from stack_configs.stack_functions import createInfluxDB
from stack_configs.ldap_functions import addToLDAPGroup,resetLDAPpassword,createLDAPuser
from stack_configs.grafana_functions import GrafanaUser,testObj

import logging

logger = logging.getLogger(__name__)
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
         'title':'welcome!',
         'site_title':'zibawa',
         'site_url':settings.SITE_URL
    }
    return HttpResponse(template.render(context, request))


   

def create_account(request):
    template = loader.get_template('admin/base_site.html')
    
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            new_user = User.objects.create_user(**form.cleaned_data)
            #new_user.is_staff=True 
            #new_user.save()
            if (createLDAPuser(new_user,password)):
                if (addToLDAPGroup(new_user.username,'active')):
                    if (addToLDAPGroup(new_user.username,'editor')):
                        result=createAndConfigureGrafana(new_user,password)
                        if (result.status):
                            if createInfluxDB(new_user): #creates a user database in influx
                                return HttpResponseRedirect('/thanks/')
            return HttpResponseRedirect('/account_create_error/')
    else:
        form = UserForm() 

        
    context = {
                
        'has_permission':request.user.is_authenticated,
        'is_popup':False,
        'form':form,
        'title':'New User Creation',
        'site_title':'zibawa',
        'site_url':settings.SITE_URL
        }
                        
    return render(request,'form.html',context)
    
    


def thanks(request):
    
    template = loader.get_template('thanks.html')
    
        
    context = {
         'content':'Thanks. Please log in to your dashboard',
         'title':'Your account has been created',
         'is_popup':False,
         'has_permission':request.user.is_authenticated,
         'site_title':'zibawa',
         'site_url':settings.SITE_URL
    }
    return HttpResponse(template.render(context, request))

def account_create_error(request):
    
    template = loader.get_template('admin/base_site.html')
    
        
    context = {
         'content':'Sorry. Something went wrong during the creation of your account. Please contact your administrator',
         'title':'Error',
         'is_popup':False,
         'has_permission':request.user.is_authenticated,
         'site_title':'zibawa',
         'site_url':settings.SITE_URL
    }
    return HttpResponse(template.render(context, request))   

def id_generator(size=10, chars=string.ascii_uppercase + string.digits):
    
    return ''.join(random.choice(chars) for _ in range(size))






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
               
                new_password = form.cleaned_data['new_password1']
                if(resetLDAPpassword(user.username,new_password)):
                    
                    #change Grafana password 
                    grafana_user=GrafanaUser(request.user.id, request.user.username,new_password,request.user.email)
                    logger.debug('resetting Grafana password for %s',request.user.username) 
                    if not (grafana_user.changeGrafanaPassword()):
                        #if fails, currently we log but carry on regardless.
                        logger.warning('couldnt reset Grafana password for %s',request.user.username)
               
                    
                    return HttpResponseRedirect(post_reset_redirect)
                else:              
                #if result from LDAP is not what we expect, or if no result
                    logger.warning('couldnt reset LDAP password')
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
        'is_popup':False,
        'has_permission':request.user.is_authenticated,
        'site_title':'zibawa',
        'site_url':settings.SITE_URL
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
                    password_change_form=SetPasswordForm,
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
            
            new_password = form.cleaned_data['new_password1']
            if(resetLDAPpassword(request.user.username,new_password)):
                logger.debug('reset LDAP password')  
                update_session_auth_hash(request, form.user)
                
                #change Grafana password 
                grafana_user=GrafanaUser(request.user.id, request.user.username,new_password,request.user.email)
                logger.debug('resetting Grafana password for %s',request.user.username) 
                if not (grafana_user.changeGrafanaPassword()):
                    #if fails, currently we carry on regardless.
                    logger.warning('couldnt reset Grafana password for %s',request.user.username)
                
                return HttpResponseRedirect(post_change_redirect)
                                            
            #if result from LDAP is not what we expect, or if no result
            else:
                logger.warning('couldnt reset LDAP password')
            
            context = {
                 'form': form,
                 'title': _('Could not reset LDAP password'),
                 'is_popup':False,
                 'has_permission':request.user.is_authenticated,
                 'site_title':'zibawa',
                 'site_url':settings.SITE_URL
                 }
            return TemplateResponse(request, template_name, context)
            #ZIBAWA MODIFICATIONS END HERE
                             
            
    else:
        form = password_change_form(user=request.user)
    context = {
        'form': form,
        'title': _('Password change'),
        'is_popup':False,
        'has_permission':request.user.is_authenticated,
        'site_title':'zibawa',
        'site_url':settings.SITE_URL
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)



def createAndConfigureGrafana(zibawa_user,password):
    
    grafana_user=GrafanaUser(zibawa_user.id, zibawa_user.username,password,zibawa_user.email)
    result=testObj("GrafanaAccount",True,"Your account already exists on Grafana from a previous installation please contact your administrator")
    if not (grafana_user.exists()):
        result=testObj("GrafanaAccount",False,"We were unable to create your dashboard account on Grafana, please contact your adminitrator")
        logger.info('trying to create grafana user')
        if grafana_user.create():
            result=testObj("GrafanaAccount",True, "Your account has been created, but not configured")
            logger.info("trying to find non grafana admin org")
            if not (grafana_user.get_orgID()):
                grafana_user.add_to_own_org()
            logger.info("running fix permissions for Grafana")
            grafana_user.fix_permissions()
            logger.info("running add datasource for Grafana")
            if (grafana_user.add_datasource()):
                result=testObj("GrafanaAccount",True,"Your account has been created and configured")
                   
    return result