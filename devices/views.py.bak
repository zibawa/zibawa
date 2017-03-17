from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_list_or_404
from django.shortcuts import render
from .forms import TestMessageForm
from .models import device
from django.conf import settings
from django.contrib.auth.decorators import login_required
from stack_configs.models import connectToLDAP,resetLDAPpassword, simpleLDAPQuery,addToLDAPGroup
from stack_configs.stack_functions import constructStatusList
from stack_configs.mqtt_functions import MqttData,TopicData,processMessages

import ldap.modlist

import string
import random
import logging
logger = logging.getLogger(__name__)


@login_required(login_url='/admin/login/?next=/admin/')
def index(request):
        
    return HttpResponse("Hello, world. You're at the devices index.")


@login_required(login_url='/admin/login/?next=/admin/')
def resetPsw(request, device_id):
    template = loader.get_template('resetPsw.html')
    my_objects = get_list_or_404(device,id=device_id, account=request.user)
    mydevice= my_objects[0]
    password= id_generator()
    response= initializeDeviceLDAP(mydevice,password)
    output=""
    topicFormat= str(mydevice.account.id)+"/"+str(mydevice.device_id)+"/*/*"
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
         
    }
    return HttpResponse(template.render(context, request))




def id_generator(size=10, chars=string.ascii_uppercase + string.digits):
    
    return ''.join(random.choice(chars) for _ in range(size))


def initializeDeviceLDAP(device,password):
             
    #deviceID is unique to database. (as defined in models.devices
    #deviceID could colide with (human) userNames.at present this will
    #cause failure.
    #uid is autonumeric id field from device table (not same as device id)
    #add 1000000 so as not to colide with people uids.
    
    username=str(device.device_id)
    
    dn= str("cn="+str(username)+","+settings.AUTH_LDAP_USERS_OU_DN)
    #check if entry already exists
    result =simpleLDAPQuery(username)
    
    if (result==[]):
        #create device in LDAP    
        uidNumber= str(device.id + 1000000)
    
        con=connectToLDAP() 
          
        modlist={}
        modlist['objectClass']=["inetOrgPerson", "posixAccount", "shadowAccount"]
        modlist['sn']=str("lastname")
        modlist['givenName']=str("first_name")
        modlist['mail']= str("dontuse@mail.com")
        modlist['cn']=str(username)
        modlist['displayName']=str(username)
        modlist['uid']=str(username)
        modlist['uidNumber']=str(uidNumber)
        modlist['gidNumber']=str(settings.AUTH_LDAP_DEVICES_DEFAULT_GID)
        modlist['homeDirectory']=str("/home/zibawa/"+str(username))
        modlist['userPassword']=str(password)
    
        
# addModList transforms your dictionary into a list that is conform to ldap input.
        result = con.add_s(dn, ldap.modlist.addModlist(modlist))
                
        addToLDAPGroup(username,'active')
        addToLDAPGroup(username,'device') 
    
        return result
    else:
        #if doesnt exist we just reset password
        result= resetLDAPpassword(dn,password)
    return result 
    


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
            
            testMsg = MqttData(form.cleaned_data['topic'],form.cleaned_data['message'])
            mqttChecksList=processMessages(testMsg)
            context = {
                
                'has_permission':request.user.is_authenticated,
                'is_popup':False,
                'form':form,
                'mqttChecksList':mqttChecksList,
                'title':'Send test message',
                'status_list':status_list
         
                       }
                        
            return render(request,'devices/testMessageForm.html',context)
        

    # if a GET (or any other method) we'll create a blank form
    else:
        form = TestMessageForm(user=request.user)
    context = {
                
                'has_permission':request.user.is_authenticated,
                'is_popup':False,
                'form':form,
                'title':'Send test message',
                'status_list':status_list
         
                        }
    return render(request, 'devices/testMessageForm.html', context)

    