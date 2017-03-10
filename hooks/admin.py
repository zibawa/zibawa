from django.contrib import admin
from .models import hook,product,place,person,User
# Register your models here.
 
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
    
class hookAdmin(FilterUserAdmin):
    
       
    
    list_display = ('hook_id', 'hook_desc')
    search_fields = ['hook_id','hook_desc']
    
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        #this function restricts choice of foreign key to those belonging to user/account
        if db_field.name == "place":
            kwargs["queryset"] = place.objects.filter(account=request.user)
        
        
        return super(hookAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    
    
    pass   # (replace this with anything else you need)    

class productAdmin(FilterUserAdmin):
    pass

class placeAdmin(FilterUserAdmin):
    pass

class personAdmin(FilterUserAdmin):
    pass




admin.site.register(hook,hookAdmin)
admin.site.register(product,productAdmin)
admin.site.register(place,placeAdmin)
admin.site.register(person,personAdmin)
