from django.shortcuts import render
from django.http import HttpResponse,HttpResponseNotFound
from .x509_functions import generateNewX509,makeCA
import logging

logger = logging.getLogger(__name__)
# Create your views here.
def new_cert(request):
    print("newcert")
    data={}
    pathTocert=generateNewX509(data)
    
    try:
        file = open(pathTocert, 'r')
        file.seek(0)
        cert = file.read()
        file.close()
        response = HttpResponse(cert, content_type='application/x-pem-file')
        response['Content-Disposition'] = 'attachment; filename="client_cert.pem"'
    
    except:
        response= HttpResponseNotFound('404 - Not found')
    
    
    return response 


def new_ca(request):
    

    print("ouch")
    logger.warning("newCA")
    data={}
    pathTocert=makeCA(500)
    
    try:
        file = open(pathTocert, 'r')
        file.seek(0)
        cert = file.read()
        file.close()
        response = HttpResponse(cert, content_type='application/x-pem-file')
        response['Content-Disposition'] = 'attachment; filename="ca_cert.pem"'
    
    except:
        response= HttpResponseNotFound('404 - Not found')
    
    
    return response 






def renew_cert(request):
    try:
        file = open('path_to_ca_cert', 'r')
        file.seek(0)
        cert = file.read()
        file.close()
        response = HttpResponse(cert, content_type='application/x-pem-file')
        response['Content-Disposition'] = 'attachment; filename="zibawa_mqtt_ca_cert.pem"'
    
    except:
        response= HttpResponseNotFound('404 - Not found')
    
    
    return response 

def index(request):
    return HttpResponse("Hello, world. You're at the pki index.")


