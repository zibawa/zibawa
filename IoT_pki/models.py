from __future__ import unicode_literals
from django.db import models
from django.utils import timezone
from django.contrib.admin.utils import help_text_for_field
from django.contrib.auth.models import User
# Create your models here.


class Cert_request (models.Model):
    
    #account = models.ForeignKey(User, on_delete=models.CASCADE,editable=False)#this is the administrative user that can approve request. Not used.
    country_name = models.CharField(max_length=2,blank=True )#obligatory must be 2 letter country code
    state_or_province_name=models.CharField(max_length=50, blank=True)
    locality_name=models.CharField(max_length=50,blank=True)
    organization_name=models.CharField(max_length=50,blank=True)
    organization_unit_name=models.CharField(max_length=50,blank=True)
    email_address=models.CharField(max_length=50,blank=True)
    user_id=models.CharField(max_length=50,blank=True)
    dns_name=models.CharField(max_length=250,blank=True)
    common_name=models.CharField(max_length=50)
    dn_qualifier=models.CharField(max_length=250,blank=True)
    approved=models.BooleanField(default=False)
    issued=models.BooleanField(default=False)#to prevent same cert being downloaded twice
    request_time=models.DateTimeField(default=timezone.now)#
    token=models.CharField(max_length=50)#token to allow cert collection
    
    
    
    def __str__(self):
        return self.common_name

    
class Certificate (models.Model):
    
    #account = models.ForeignKey(User, on_delete=models.CASCADE,editable=False)
    country_name = models.CharField(max_length=2)
    state_or_province_name=models.CharField(max_length=50, blank=True)
    locality_name=models.CharField(max_length=50,blank=True)
    organization_name=models.CharField(max_length=50,blank=True)
    organization_unit_name=models.CharField(max_length=50,blank=True)
    email_address=models.CharField(max_length=50,blank=True)
    user_id=models.CharField(max_length=50,blank=True)
    dns_name=models.CharField(max_length=250,blank=True)
    common_name=models.CharField(max_length=50,blank=True)
    dn_qualifier=models.CharField(max_length=250,blank=True)
    not_valid_before=models.DateTimeField()
    not_valid_after=models.DateTimeField()
    serial_number=models.CharField(max_length=250)
    revoked=models.BooleanField(default=False)
    
    def __str__(self):
        return self.common_name
    