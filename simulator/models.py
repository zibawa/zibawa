from __future__ import unicode_literals
from django.db import models
from django.utils import timezone
from django.contrib.admin.utils import help_text_for_field
from django.contrib.auth.models import User
# Create your models here.

    
class simulation(models.Model):
    
    account = models.ForeignKey(User, on_delete=models.CASCADE,editable=False)
    description= models.CharField(max_length=50, default="")
    process_name =models.CharField(max_length=50,default="")
    start_time=models.DateTimeField()
    end_time=models.DateTimeField(default=timezone.now)
    period=models.IntegerField(default=1,help_text="period between updates in seconds")
    
    def __str__(self):
        return self.description
    
    
class thing (models.Model):
    
    simulation = models.ForeignKey('simulation',on_delete=models.CASCADE)
    device=models.ForeignKey('devices.device',on_delete=models.CASCADE)
    target= models.FloatField(default=0)
    month_k=models.FloatField(default=1,help_text="positive greater in winter")
    hour_k=models.FloatField(default=1,help_text="positive greater in daytime")
    longwave_k=models.FloatField(default=10000,help_text="positive integer large number longer wave")
    longwave_a=models.FloatField(default=1,help_text="positive - higher wave variation")
    last_v=models.FloatField(default=0)
    delta_v=models.FloatField(default=0)
    d_delta_v=models.FloatField(default=0)
    ra=models.FloatField(default=0,help_text="higher number more random")
    ce=models.FloatField(default=0,help_text="higher number more centred")
    
    
        