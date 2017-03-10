from __future__ import unicode_literals

from django.db import models

from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import RegexValidator


# Create your models here.


class section(models.Model):
    account = models.ForeignKey(User, on_delete=models.CASCADE,editable=False)
    section_desc = models.CharField(max_length=50)
    
    def __str__(self):
        return self.section_desc

alphanumeric = RegexValidator(r'^[0-9a-zA-Z]*$', 'Only alphanumeric characters are allowed.')
     
class device(models.Model):
    account = models.ForeignKey(User, on_delete=models.CASCADE,editable=False)
    device_id=models.CharField(unique=True,max_length=50,validators=[alphanumeric],help_text="device should publish to mqtt on account_name/deviceID/appID/channelID")
    device_desc = models.CharField(max_length=50,blank=True)
    section = models.ForeignKey(section, on_delete=models.CASCADE)
    group=models.CharField(max_length=50,blank=True)
    subgroup=models.CharField(max_length=50,blank=True)
    latitude=models.FloatField(blank=True,null=True)
    longitude=models.FloatField(blank=True,null=True)
    model_name = models.CharField(max_length=50,blank=True)
    install_date = models.DateTimeField('install_date',default=timezone.now)


    def __str__(self):
        return self.device_desc
    
   
   
class channel_tag(models.Model):
    account = models.ForeignKey(User, on_delete=models.CASCADE,editable=False)
    name=models.CharField(max_length=20)
       
    pass
    def __str__(self):
        return self.name 
    

class channel(models.Model):
    device = models.ForeignKey(device, on_delete=models.CASCADE)
    channel_id=models.CharField(max_length=50,validators=[alphanumeric],help_text="device should publish to mqtt on account_name/deviceID/appID/channelID")
    channel_desc = models.CharField(max_length=50,blank=True)
    channel_tags = models.ManyToManyField(channel_tag,blank=True)
    time_tag_year=models.BooleanField(default=False,help_text="tags the channel data with year (eg.\'2015\')")
    time_tag_month=models.BooleanField(default=False,help_text="tags the channel data with month")
    time_tag_day=models.BooleanField(default=False,help_text="tags the channel data with day of week")
    time_tag_hour=models.BooleanField(default=False,help_text="tags the channel data with hour (eg.\'2015\')")
    elapsed_since_same_ch=models.BooleanField(default=False,help_text="tags the channel data with seconds since any data was received on SAME channel(eg.cycle time)')")
    elapsed_since_diff_ch=models.BooleanField(default=False,help_text="tags the channel data with seconds since HOOK was received on DIFFERENT channel(for TIME betwen different processes typically RFID')")
    
    upper_warning=models.FloatField(blank=True,null=True)
    lower_warning=models.FloatField(blank=True,null=True)
    alarm_logs=models.BooleanField(default=False)
    alarm_email=models.BooleanField(default=False,help_text="alarms will be sent to user who owns device (not active)")
    alarm_raised=models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.channel_desc
     
    


    

    
    
