from builtins import str
from builtins import range
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_list_or_404
from django.shortcuts import render
from .forms import TestMessageForm
from .models import Device
from django.conf import settings
from django.contrib.auth.decorators import login_required
#from stack_configs.models import connectToLDAP,resetLDAPpassword, simpleLDAPQuery,addToLDAPGroup
from stack_configs.stack_functions import constructStatusList
from stack_configs.mqtt_functions import MqttData,TopicData,processMessages
from stack_configs.ldap_functions import createLDAPDevice,getLDAPConn,addToLDAPGroup


import string
import random
import logging
logger = logging.getLogger(__name__)


@login_required(login_url='/admin/login/?next=/admin/')
def index(request):
    #test ldap auth
    con=getLDAPConn()
    con.search(settings.AUTH_LDAP_USERS_OU_DN, '(&(objectclass=inetOrgPerson)(uid=rtamudo))', attributes=['sn'])
    print(con.entries[0].entry_to_ldif())
    #search group
    #con.search(settings.AUTH_LDAP_GROUPS_OU_DN, '(&(objectclass=posixGroup)(cn=active))',attributes=['gidNumber','memberUid']) 
    con.search(settings.AUTH_LDAP_GROUPS_OU_DN, '(&(objectclass=posixGroup)(cn=active)(memberUid=rtamudo))',attributes=['cn','gidNumber']) 
    
    #dc=test,dc=com" "(&(cn=*)(memberUid=skimeer))
    
    print(con.entries[0].entry_to_ldif())
    #print(con.entries[1].entry_to_ldif())
    print ("using dicts")
    for entry in con.entries:
        #print(entry.dn)
        print(entry.cn)
        
    return HttpResponse("Hello, world. You're at the devices index.")


@login_required(login_url='/admin/login/?next=/admin/')
def resetPsw(request, device_id):
    template = loader.get_template('resetPsw.html')
    my_objects = get_list_or_404(Device,id=device_id, account=request.user)
    mydevice= my_objects[0]
    password= id_generator()
    if(createLDAPDevice(mydevice, password)):
        addToLDAPGroup(mydevice.device_id,'device')
        output=""
        topicFormat= str(mydevice.account.id)+"."+str(mydevice.device_id)+".*.*"
    #except Exception:
    #    output="We were unable to reset your password please contact your administrator"
        context = {
            'content':output,
            'username': mydevice.device_id,
            'password': password,
            'topicFormat': topicFormat,
            'has_permission':request.user.is_authenticated,
            'is_popup':False,
            'title':'Reset device password',
            'site_title':'zibawa',
            'site_url':settings.SITE_URL
         
        }
    else:
        context = {
            'content':"We were unable to create your device password. Try a different device ID or contact your administrator",
            'username': mydevice.device_id,
            'password': "",
            'topicFormat': "",
            'has_permission':request.user.is_authenticated,
            'is_popup':False,
            'title':'Unable to reset device password',
            'site_title':'zibawa',
            'site_url':settings.SITE_URL
         
        }
    return HttpResponse(template.render(context, request))




def id_generator(size=10, chars=string.ascii_uppercase + string.digits):
    
    return ''.join(random.choice(chars) for _ in range(size))


    


@login_required(login_url='/admin/login/?next=/admin/')
def testMessage(request):
    #this allows user to feed messages into the same process
    #functions that we use in the automatic mqtt processing
    status_list=constructStatusList(request)
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = TestMessageForm(request.POST,user=request.user)
        # check whether it's valid:
        if form.is_valid():
            #check that user is sending data on their own account
            logger.debug('form valid, processing message')
            testMsg = MqttData(form.cleaned_data['topic'],form.cleaned_data['message'])
            mqttChecksList=processMessages(testMsg)
            context = {
                
                'has_permission':request.user.is_authenticated,
                'is_popup':False,
                'form':form,
                'mqttChecksList':mqttChecksList,
                'title':'Send test message',
                'site_title':'zibawa',
                'status_list':status_list,
                'site_url':settings.SITE_URL
         
                       }
                        
            return render(request,'devices/testMessageForm.html',context)
        logger.debug('form not valid, reprinting form')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = TestMessageForm(user=request.user)
        logger.debug('no post data received reprinting form')

    context = {
                
                'has_permission':request.user.is_authenticated,
                'is_popup':False,
                'form':form,
                'title':'Send test message',
                'mqttChecksList':None,
                'site_title':'zibawa',
                'status_list':status_list,
                'site_url':settings.SITE_URL
         
                        }
    return render(request, 'devices/testMessageForm.html', context)

    