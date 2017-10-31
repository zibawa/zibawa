from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated



from .models import Data_ingest_line
from .serializers import Data_ingest_lineSerializer

from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from stack_configs.mqtt_functions import processHttp



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




    
   