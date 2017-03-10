from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models



# Create your models here.



class person(models.Model):
    account = models.ForeignKey(User, on_delete=models.CASCADE,editable=False)
    person_id =models.CharField(max_length=50)
    person_desc = models.CharField(max_length=50)
    person_fam = models.CharField(max_length=50,blank=True)
    def __str__(self):
        return self.person_id
   



class product(models.Model):
    account = models.ForeignKey(User, on_delete=models.CASCADE,editable=False)
    product_id =models.CharField(max_length=50)
    product_desc = models.CharField(max_length=50)
    product_fam = models.CharField(max_length=50,blank=True)
    def __str__(self):
        return self.product_id

class place(models.Model):
    account = models.ForeignKey(User, on_delete=models.CASCADE,editable=False)
    place_id =models.CharField(max_length=50)
    place_desc = models.CharField(max_length=50)
    place_fam = models.CharField(max_length=50,blank=True)
        
    def __str__(self):
        return self.product_id   
    
    
class hook(models.Model):
    account = models.ForeignKey(User, on_delete=models.CASCADE,editable=False)
    hook_id = models.CharField(max_length=20)
    hook_desc = models.CharField(max_length=50)
    product = models.ForeignKey(product,blank=True,null=True,on_delete=models.CASCADE)
    person = models.ForeignKey(person,blank=True,null=True,on_delete=models.CASCADE)
    place = models.ForeignKey(place,blank=True,null=True,on_delete=models.CASCADE)
    # ...
    def __str__(self):
        return self.hook_id
    
    def hook_product_id(self):
        return self.product.product_id

    def hook_person_id(self):
        return self.person.person_id
    
    def hook_place_id(self):
        return self.person.person_id