import paho.mqtt.client as mqtt
from django.conf import settings
import logging
import ssl
import time
logger = logging.getLogger(__name__)


def on_connect(mqttc, obj, flags, rc):
    global loop_flag
    global outputRC
    loop_flag=0
    outputRC=rc
    if rc==0:
        logger.debug("connected OK Returned code:%s")
        
        #mqttc.connected_flag=True #Flag to indicate success
    else:
        pass
    

def on_message(mqttc, obj, msg):
    print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))

def on_publish(mqttc, obj, mid):
    print("mid: "+str(mid))
    pass

def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: "+str(mid)+" "+str(granted_qos))
    


def connectToMqtt(username,password,topic,payload):
    #connects to MQTT (for testing)
    global loop_flag
    global outputRC
    mqttc=mqtt.Client()
    if settings.MQTT['verify_certs']:
        cert_reqs=ssl.CERT_REQUIRED
    else:
        cert_reqs=ssl.CERT_NONE
        mqttc.tls_insecure_set(True)
    
    mqttc.connected_flag=False #
    if settings.MQTT['use_ssl']:
        mqttc.tls_set(ca_certs=settings.MQTT['path_to_ca_cert'], certfile=None, keyfile=None, cert_reqs=cert_reqs,tls_version=ssl.PROTOCOL_SSLv23, ciphers=None)
    else:
        tls=None
    print("username:%s,password:%s",username,password)
    mqttc.username_pw_set(username, password)
    mqttc.on_message = on_message
    mqttc.on_connect = on_connect
    mqttc.on_publish = on_publish
    mqttc.on_subscribe = on_subscribe
    
    loop_flag=1
    
    try:
        mqttc.connect(settings.MQTT['host'], port=settings.MQTT['port'], keepalive=60, bind_address="")
    except Exception as e: 
        logger.error("connection error %s",e)
        loop_flag=0
        outputRC=100
    mqttc.loop_start()#Stop loop     
    #loop until we receive connack
    while (loop_flag==1):
        time.sleep(0.01)
    mqttc.disconnect()
    mqttc.loop_stop()
    
    #infot=mqttc.publish(topic, payload=None, qos=0, retain=False)
    ''' CONNACK CODES
    0    Connection Accepted
    1    Connection Refused, unacceptable protocol version
    2    Connection Refused, identifier rejected
    3    Connection Refused, Server unavailable
    4    Connection Refused, bad user name or password
    5    Connection Refused, not authorized
    '''
    
    return outputRC


