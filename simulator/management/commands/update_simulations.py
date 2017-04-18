'''
Created on Dec 9, 2016

@author: julimatt
'''
'''
Created on Nov 23, 2016

@author: julimatt
this file is designed to run as cronjob. it collects all simulations from database and
calculates new values for all things in database related to that simulation.
Simulated values are sent to rabbitMQ

RabbitMQ listener needs to be setup to process the format specified (in this case format 2)

IMPORTANT: TIME FORMAT IN JSON MUST BE EXACTLY THAT SHOWN 
body='{"timestamp":"2016-11-25T14:38:00.000000+00:00", "value":"float"}' 
this is to enable elasticsearch to dynamically detect that it is a date field when
creating new index. 

THE DEVICE AND CHANNEL MUST COME FROM THE second and fourth PARAMETER OF TOPIC (this is for security otherwise we cannot guarantee the 
data is written by who we think

'''
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from simulator.models import simulation,thing
from devices.models import Device,Channel,Section
from stack_configs.models import sendToRabbitMQ
from django.contrib.auth.models import User
import datetime
import time
from random import randint
import random
import json
import string
import logging
logger = logging.getLogger(__name__)

global month_profile
global hour_profile
month_profiles=[10,15,5,0,-5,-10,-15,-15,-5,0,5,5]
hour_profiles=[-50,-50,-55,-50,-40,-30,-20,0,5,6,10,10,10,20,20,15,10,10,20,20,10,0,-10,-20]

#objects will be created for user who owns the simulation
#however, topic will be simulation.*.*.* 
#this could cause problems if more than one user has simulations
#because they can conflict

global simulation_account
try:
    simulation_account=User.objects.filter(username='simulation')[0]
    
except:
    logger.info('no user account named simulation found, aborting')
    raise SystemExit(0)


#global simulationAccount


class Command(BaseCommand):
    help = 'updates all simulations and sends to rabbitMQ'

       
    
    def handle(self, *args, **options):
                    
            
        logger.info('starting handle update simulation')
        while True:
            output=getAllSims()
            time.sleep(100)
            logger.info('simulation completed, sleeping')
           
def getAllSims():
#get all simulation objects and calculate from last start time up till now 
    #try:
    sims=simulation.objects.all()
    for sim in sims:
        print(" sim %r" % (sim.start_time))
        logger.info('starting simulation at %s,', sim.start_time)
        sim_time= sim.start_time
        while sim_time< timezone.now():
            #simulationAccount=sim.account
            sim_time=sim_time+datetime.timedelta(seconds=sim.period)
            calculateAll(sim, sim_time)
            sim.start_time= sim_time                  
            sim.save()
    
    return 


def calculateAll(sim,sim_time):
    global month_profiles
    global hour_profiles
    
    things=sim.thing_set.all()
    
    if not things.exists():
        logger.info('no things found in this simulation, creating things')
        things=createNewThings(sim, sim_time)
        
    for thing in things:
        #every X cycles update long wave with extra random factor
        logger.info('starting to create data')
        if random.randint(0,thing.longwave_k)<2:
            thing.d_delta_v= (random.randint(0,1000)*0.002)-1
        
        #centering factor -0.2, target is zero..to be modified.
        target=thing.target*(100+thing.month_k*month_profiles[(sim_time.month)-1]+thing.hour_k*hour_profiles[sim_time.hour])/100
        #q=(random.randint(0,1000))
        #print "random %r"% (q)
        #w= q*0.002
        #print "w %r"% (w)
        #x= w-1
        thing.delta_v=(random.randint(0,1000)*0.002)-1-((thing.last_v-target))+thing.longwave_a*thing.d_delta_v
        #print "lastv %r" %(thing.last_v)
        #print "deltav %r" %(thing.delta_v)
        
        v= thing.last_v+thing.delta_v
        #print "v %r" %(v)
        data={}
        data['timestamp']=sim_time      
        data['value']=v
        
        
        json_data = json.dumps(data,default=date_handler)
        topic= str(simulation_account.id)+"."+thing.device.device_id+".2.1"
        #topic format - account.deviceID.appID(messageformat).channel  format2 defined as timestamp + value (format1= rfid tag)
        logger.info('trying to send to topic %s, message: %s',topic,json_data)       
        try: 
            sendToRabbitMQ(topic,json_data)
            
            #print(" sent %r:%r" % (topic, json_data)) 
        except:
            raise CommandError("failed to connect to Rabbit")
        thing.last_v=v
        thing.save()
    return


'''
def mytoTest():
    subgroups=['barcelona','valencia','madrid','zaragoza']
    minLat={'barcelona':41346,'valencia':39446,'madrid':40345,'zaragoza':41638}
    maxLat={'barcelona':41354,'valencia':39496,'madrid':40480,'zaragoza':41655}
    minLon={'barcelona':2104,'valencia':-397,'madrid':-3724,'zaragoza':-905}
    maxLon={'barcelona':2122,'valencia':-350,'madrid':-3602,'zaragoza':-879}
      
    subg= random.choice(subgroups)
        
    lat=(minLat[subg]+randint(0,(maxLat[subg]-minLat[subg])))
    lon=(minLon[subg]+randint(0,(maxLon[subg]-minLon[subg])))
    
    latn=lat/float(1000)
    
    exit()
'''

def createNewThings(sim,sim_time):
    
    global simulation_account
    num_devices= 5
    deviceDescs=['energy_meter']
    modelNames= ['enerstar514']
    
    majorGroups=['lighting','refrigeration','heating','pumps','other']
    subgroups=['barcelona','valencia','madrid','zaragoza']
    minLat={'barcelona':41346,'valencia':39446,'madrid':40345,'zaragoza':41638}
    maxLat={'barcelona':41354,'valencia':39496,'madrid':40480,'zaragoza':41655}
    minLon={'barcelona':2104,'valencia':-397,'madrid':-3724,'zaragoza':-905}
    maxLon={'barcelona':2122,'valencia':-350,'madrid':-3602,'zaragoza':-879}
    month_ks={'lighting':'2','refrigeration':-3,'heating':'2','pumps':'1','other':'2'}
    hour_ks={'lighting':'-4','refrigeration':1,'heating':'1','pumps':'2','other':'2'}
    
    #create a new section to house the simulation to cleanly delete the devices
    s= Section(section_desc=sim.description,account=simulation_account)
    s.save()
    
    for x in range(1,num_devices):
        logger.info('creating device %s',x)
        subg= random.choice(subgroups)
        
        lat=(minLat[subg]+randint(0,(maxLat[subg]-minLat[subg])))/float(1000)
        lon=(minLon[subg]+randint(0,(maxLon[subg]-minLon[subg])))/float(1000)
        d= Device (device_id= id_generator(10),device_desc=random.choice(deviceDescs),subgroup=subg,model_name=random.choice(modelNames),section=s,group= random.choice(majorGroups),latitude=lat, longitude=lon,install_date=sim_time,account=simulation_account)
        d.save()
        channelDesc=str(d.device_desc)+str(x)
        c= Channel (device=d, channel_id= "1", channel_desc= channelDesc, time_tag_month=True,time_tag_hour=True)
        c.save()
        tar=randint(50,5000)
        t=thing(simulation=sim,device=d,target=tar,last_v=tar, delta_v=0, d_delta_v=0, ra=1, ce=1,month_k=month_ks[d.group],hour_k=hour_ks[d.group],longwave_k=randint(1000,5000),longwave_a=randint(1,5))
        t.save()
        
    things=thing.objects.filter(simulation=sim)
    
    return things


    


def id_generator(size=10, chars=string.ascii_uppercase + string.digits):
    '''need to add tags to database!!!!'''
    return ''.join(random.choice(chars) for _ in range(size))


def date_handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        raise TypeError

