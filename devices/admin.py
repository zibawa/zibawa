from django.contrib import admin
from stack_configs.influx_functions import getLastTimeInflux
# Register your models here

from .models import Section,Device,Channel,User,Channel_tag


class channelInline(admin.StackedInline):
    model = Channel
    #fields=['channel_id','last_published']
    readonly_fields=('last_published',)
    extra = 0
    
    fieldsets = (
        (None, {
            'fields': ('channel_id','channel_desc','channel_tags','last_published')
        }),
        ('Time related tags', {
            'description':'Use these to add extra information to analyse your data by day of week or hour of day',
            'classes': ('collapse',),
            'fields': ('time_tag_year','time_tag_month','time_tag_day','time_tag_hour','elapsed_since_same_ch','elapsed_since_diff_ch',),
        }),
        ('Alarms',{
            'description':'Add reference limits to your graphs and set alarms',
            'classes':('collapse',),
            'fields': ('upper_warning','lower_warning','alarm_logs','alarm_email','alarm_raised',),
        }),
    )
    '''
    fieldsets = (
        (None, {
            'fields': ('channel_id', 'channel_desc', 'channel_tags','last_published')
        }),
        ('Channel_tags', {
            'classes': ('collapse',),
            'fields': ('channel_desc','channel_tags'),
        }),
    )
    '''
    
  
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
    
    fieldsets = (
        (None, {
            'fields': ('device_id','device_desc','group','section','subgroup' ,)
        }),
        ('Geo-position',{
            'description':'',
            'classes':('collapse',),
            'fields':('latitude','longitude',),
            }),
        
        ('Installation details',{
            'description':'',
            'classes':('collapse',),
            'fields':('model_name','install_date',),
        }),
        )
    
    
    
    
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        #this function restricts choice of foreign key to those belonging to user/account
        if db_field.name == "section":
            kwargs["queryset"] = Section.objects.filter(account=request.user)
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
