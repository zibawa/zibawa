from rest_framework import serializers
from .models import Data_ingest_line
from django.utils import timezone


class Data_ingest_lineSerializer(serializers.Serializer):
    channel_id = serializers.CharField(max_length=50)
    value  = serializers.FloatField()
    timestamp = serializers.DateTimeField(default=timezone.now)
   
    

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return Data_ingest_line.objects.create(**validated_data)

class Data_ingest_bulkSerializer(serializers.Serializer):
    datapoints = Data_ingest_lineSerializer(many=True)
    #edits = EditItemSerializer(many=True)  # A nested list of 'edit' items.
    #content = serializers.CharField(max_length=200)
    #created = serializers.DateTimeField()