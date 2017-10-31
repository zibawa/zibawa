from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated



from .models import Data_ingest_line
from .serializers import Data_ingest_lineSerializer, Data_ingest_bulkSerializer

from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from stack_configs.mqtt_functions import processHttp

from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import UploadFileForm

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
                result= processHttp(datapoint,request.user)
                logger.info("processHttp result: %s,", result)
            
            #serializer.save()
            return Response(result, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)







def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'])
            return HttpResponseRedirect('/success/url/')
    else:
        form = UploadFileForm()
    return render(request, 'api_v1/fileUploadForm.html', {'form': form})



def handle_uploaded_file(f):
    with open('some/file/name.txt', 'wb+') as destination:
        for chunk in f.chunks():
            #destination.write(chunk)  
            print(chunk)
   