from django.contrib import admin

# Register your models here

from .models import Section,Device,Channel,User,Channel_tag


class channelInline(admin.StackedInline):
    model = Channel
    extra = 1

  
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

class deviceAdmin(FilterUserAdmin):
    
    def resetPasswordLink(self, obj):
        return u"<a href='/devices/%d/resetPsw'>Reset password</a>" % obj.id
    
    resetPasswordLink.short_description = ''
    resetPasswordLink.allow_tags = True
    #list_display = ('id', view_link) 
    
    
    list_display = ('device_id', 'device_desc','resetPasswordLink')
    search_fields = ['device_id','device_desc','model_name']
    inlines = [channelInline]
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        #this function restricts choice of foreign key to those belonging to user/account
        if db_field.name == "section":
            kwargs["queryset"] = section.objects.filter(account=request.user)
        return super(deviceAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    
    
    pass   # (replace this with anything else you need)    

class sectionAdmin(FilterUserAdmin):
    
    pass   # (replace this with anything else you need)    

class channel_tagAdmin(FilterUserAdmin):
    list_display=('id','name')
    pass   # (replace this with anything else you need)    


class UserAdmin(admin.ModelAdmin):
    list_display = ('id','username','email', 'first_name', 'last_name')
    

#in case of user must unregister first
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


admin.site.register(Section,sectionAdmin)
admin.site.register(Device,deviceAdmin)
admin.site.register(Channel_tag,channel_tagAdmin)
