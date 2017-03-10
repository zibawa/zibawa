from django.contrib import admin

# Register your models here.
from .models import simulation,thing,User


class FilterUserAdmin(admin.ModelAdmin): 
    #this class is used to filter objects by user(account)
    def save_model(self, request, obj, form, change):
        obj.account = request.user
        obj.save()

    def get_queryset(self, request): 
        # For Django < 1.6, override queryset instead of get_queryset
        qs = super(FilterUserAdmin, self).get_queryset(request) 
        return qs.filter(account=request.user)

    def has_change_permission(self, request, obj=None):
        if not obj:
            # the changelist itself
            return True
        return obj.account == request.user

class simulationAdmin(FilterUserAdmin):
    
  
        
    pass   # (replace this with anything else you need)    

class sectionAdmin(FilterUserAdmin):
    
    pass   # (replace this with anything else you need)    




admin.site.register(simulation,simulationAdmin)
admin.site.register(thing)