from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from django.conf import settings

from .models import Data_ingest_line
from .serializers import Data_ingest_lineSerializer, Data_ingest_bulkSerializer

from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from stack_configs.mqtt_functions import processHttp
from stack_configs.elastic_functions import sendToElasticBulk

from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import UploadFileForm

import csv
import json
import requests


import logging
logger = logging.getLogger(__name__)
# Create your views here.

class Data_ingest(APIView):
    """
    List all snippets, or create a new snippet.
    """
    permission_classes = (IsAuthenticated,)
    def get(self, request, format=None):
        snippets = Data_ingest_line.objects.all()
        serializer = Data_ingest_lineSerializer(snippets, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        
        
        serializer = Data_ingest_lineSerializer(data=request.data)
        
        logger.debug (request.data)
        
        
        if serializer.is_valid():
            logger.debug("valid serializer")
            logger.debug("user is %s",request.user)
            result= processHttp(serializer.data,request.user)
            logger.info("processHttp result: %s,", result)
            #serializer.save()
            return Response(result, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Data_ingest_bulkOld(APIView):
    """
    List all snippets, or create a new snippet.
    """
    permission_classes = (IsAuthenticated,)
    def get(self, request, format=None):
        snippets = Data_ingest_line.objects.all()
        serializer = Data_ingest_lineSerializer(snippets, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        
        
        serializer = Data_ingest_bulkSerializer(data=request.data)
        
        logger.debug (request.data)
        
        
        if serializer.is_valid():
            logger.debug("valid serializer")
            logger.debug("user is %s",request.user)
            logger.debug("firstline of serializer data is %s", serializer.data['datapoints'][0])
            datapoints = serializer.data['datapoints']
            for datapoint in datapoints:
                result= processHttp(datapoint,request.user)
                logger.info("processHttp result: %s,", result)
            
            #serializer.save()
            return Response(result, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class Data_ingest_bulk(APIView):
    """
    List all snippets, or create a new snippet.
    """
    
    
    permission_classes = (IsAuthenticated,)
    def get(self, request, format=None):
        snippets = Data_ingest_line.objects.all()
        serializer = Data_ingest_lineSerializer(snippets, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        
        
        serializer = Data_ingest_bulkSerializer(data=request.data)
        
        logger.debug (request.data)
        
        
        if serializer.is_valid():
            logger.debug("valid serializer")
            logger.debug("user is %s",request.user)
            logger.debug("firstline of serializer data is %s", serializer.data['datapoints'][0])
            datapoints = serializer.data['datapoints']
            for datapoint in datapoints:
                datapoint['upload_ref_ID']=serializer.data['upload_ref_ID']
           
            #we oblige index naming function to prevent any user sending
            #to any index to replace this would need to think about security
            indexname= "dab"+str(request.user).lower()
            
            jsonData= serializer.data
            result=sendToElasticBulk(indexname,datapoints)
                
                
            logger.info("processHttp result: %s,", result)
            
            #serializer.save()
            return Response(result, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    






def upload_file(request):
    if request.method == 'POST':
        logger.info("request is post")
        form = UploadFileForm(request.POST,request.FILES)
        if form.is_valid():
            upload_ref_ID=form.cleaned_data['upload_ref_ID']
            result=handle_uploaded_file(request.FILES['file'],request,upload_ref_ID)
            logger.debug ("result status code: %s",result.status_code)
            if (result.status_code==201):
                success=True
                failure=False
                lines=result.text
            else:
                success=False
                failure=True    
                lines=0
            context = {
                
                'has_permission':request.user.is_authenticated,
                'is_popup':False,
                'form':form,
                'title':'Send test message',
                'site_title':'zibawa',
                'status_code':result.status_code,
                'success':success,
                'failure':failure,
                'lines': lines,
                'error_message': result.text,
                'site_url':settings.SITE_URL
         
                        }
            
            
            return render(request, 'api_v1/fileUploadForm.html',context)
        
    else:
        
        form = UploadFileForm()
    return render(request, 'api_v1/fileUploadForm.html', {'form': form})



def handle_uploaded_file(f,request,upload_ref_ID):

    with open('/tmp/upload.txt', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    
    with open('/tmp/upload.txt', 'r') as f:
    
        reader = csv.reader(f, delimiter='\t')
        data_list = list()
        
        
        
        for row in reader:
            data_list.append(row)
            data = [dict(zip(data_list[0],row)) for row in data_list]
            data.pop(0)
            
        dataWrapper={}
        dataWrapper['datapoints']=data
        dataWrapper['upload_ref_ID']=upload_ref_ID    
        s = json.dumps(dataWrapper)
       

        url = 'http://localhost:8000/api_v1/bulk'
        headers = {'Content-Type': 'application/json'}
        

        username=settings.APIUSER['user']
        password= settings.APIUSER['password']

        result = requests.post(url, data=s, auth=(username,password), headers=headers)
        
        
        
        return result
#print(r.content)
   