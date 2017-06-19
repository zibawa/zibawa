import sys
from opcua.ua.uaprotocol_auto import AnonymousIdentityToken
sys.path.insert(0, "..")
import logging
import time
from django.core.management.base import BaseCommand

try:
    from IPython import embed
except ImportError:
    import code

    def embed():
        vars = globals()
        vars.update(locals())
        shell = code.InteractiveConsole(vars)
        shell.interact()


from opcua import Client
from opcua import ua



class Command(BaseCommand):
    help = 'listens to rabbitMQ, decodes json, enriches the data and loads to elasticsearch'
    
    
    def handle(self, *args, **options):
        
        main()


class SubHandler(object):

    """
    Subscription Handler. To receive events from server for a subscription
    data_change and event methods are called directly from receiving thread.
    Do not do expensive, slow or network operation there. Create another 
    thread if you need to do such a thing
    """

    def datachange_notification(self, node, val, data):
        print("Python: New data change event", node, val)

    def event_notification(self, event):
        print("Python: New event", event)


def main():

#if __name__ == "__main__":
    logging.basicConfig(level=logging.WARN)
    #logger = logging.getLogger("KeepAlive")
    #logger.setLevel(logging.DEBUG)

    #client = Client("opc.tcp://localhost:4840/freeopcua/server/")
    #client=Client("opc.tcp://opcua.demo-this.com:51210/UA/SampleServer")
    #UaServer@ works for john..
    #client=Client("opc.tcp://UaServerC@192.168.1.12:48020") 
    client=Client("opc.tcp://192.168.1.12:49320")
    result=client.connect_and_get_server_endpoints()
    #print(result)
    #result=client.server_policy_id('Anonymous', 'Anonymous')
    #print (result)
    client.load_client_certificate("/etc/ssl/opcclient2.crt")
    client.load_private_key("/etc/ssl/opcclient2key.pem")
    client.set_security_string("Basic256,SignAndEncrypt,/etc/ssl/opcclient2.crt,/etc/ssl/opcclient2key.pem,/home/jmm/Documents/smartfactory/certs/kepservercert1.der")
    #client.set_user('john')
    #client.set_password('master')
    # client = Client("opc.tcp://admin@localhost:4840/freeopcua/server/") #connect using a user
    try:
        client.connect()

        # Client has a few methods to get proxy to UA nodes that should always be in address space such as Root or Objects
        root = client.get_root_node()
        print("Root node is: ", root)
        objects = client.get_objects_node()
        print("Objects node is: ", objects)

        # Node objects have methods to read and write node attributes as well as browse or populate address space
        print("Children of root are: ", root.get_children())
        #my code
        objectNodes=root.get_children()
        for mynode in objectNodes:
            print (mynode)
            print ("browse name:",mynode.get_browse_name())
            print ("display name",mynode.get_display_name())
            nextLevel=mynode.get_children()
            for mynode2 in nextLevel:
                print (mynode2)
                print ("browse name2:",mynode2.get_browse_name())
                print ("display name2",mynode2.get_display_name())
                    
            

        # get a specific node knowing its node id
        #var = client.get_node(ua.NodeId(1002, 2))
        var = client.get_node("ns=4;i=1285")
        print("var - get node",var)
        val=var.get_data_value() # get value of node as a DataValue object
        
        print ("val",val)
        print (type(val))
        print (dir (val))
        print ("value", val.Value)
        print (type(val.Value))
        print (dir(val.Value))
        print (val.Value.Value)
        print (val.Value.VariantType.name)
        print (type(val.Value.VariantType))
        print (val.SourceTimestamp)
        print ("getdatatype", val.get_data_type())
        print ("getvalue",var.get_value())
        var.get
        
        
        #var.get_value() # get value of node as a python builtin
        #var.set_value(ua.Variant([23], ua.VariantType.Int64)) #set node value using explicit data type
        #var.set_value(3.9) # set node value using implicit data type

        # Now getting a variable node using its browse path
        
        #matt= client.get_node(ua.NodeId())
        
        myvar = root.get_child(["0:Objects", "2:MyObject", "2:MyVariable"])
        obj = root.get_child(["0:Objects", "2:MyObject"])
        print("myvar is: ", myvar)

        # subscribing to a variable node
        handler = SubHandler()
        sub = client.create_subscription(500, handler)
        handle = sub.subscribe_data_change(myvar)
        time.sleep(0.1)

        # we can also subscribe to events from server
        sub.subscribe_events()
        # sub.unsubscribe(handle)
        # sub.delete()

        # calling a method on server
        res = obj.call_method("2:multiply", 3, "klk")
        print("method result is: ", res)

        embed()
    finally:
        client.disconnect()



