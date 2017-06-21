from __future__ import unicode_literals
from django.db import models
from django.utils import timezone
from django.contrib.admin.utils import help_text_for_field
from django.contrib.auth.models import User
# Create your models here.

    
class certificates (models.Model):
    
    account = models.ForeignKey(User, on_delete=models.CASCADE,editable=False)
    description= models.CharField(max_length=50, default="")
    process_name =models.CharField(max_length=50,default="")
    start_time=models.DateTimeField()
    end_time=models.DateTimeField(default=timezone.now)
    period=models.IntegerField(default=1,help_text="period between updates in seconds")
    
    def __str__(self):
        return self.description
    