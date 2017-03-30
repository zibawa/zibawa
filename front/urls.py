from django.conf.urls import url
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.shortcuts import redirect

extracontext = {
         
         'has_permission':False,
         'is_popup':False,
         'title':'',
         'site_title':'zibawa',
         'site_url':settings.SITE_URL
    }


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^create_account/$', views.create_account, name='create_account'),
    url(r'^thanks/$', views.thanks, name='thanks'),
    url(r'^account_create_error/$', views.account_create_error, name='account_create_error'),
    url(r'^change_password/$', views.zibawa_password_change,name='password_change'),
    url(r'^change_password/done/$', auth_views.password_change_done,{'extra_context':extracontext},name='password_change_done'),
    url(r'^password_reset/$', auth_views.password_reset,{'extra_context':extracontext},name='password_reset'),
    url(r'^password_reset_done/$', auth_views.password_reset_done,{'extra_context':extracontext},name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.zibawa_password_reset_confirm,name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.password_reset_complete,{'extra_context':extracontext},name='password_reset_complete'),
    url(r'^login/$',auth_views.login, {'template_name': 'login.html','extra_context':extracontext },name='login'),
    url(r'^logout/$',auth_views.logout,{'next_page': '/login/','extra_context':extracontext},name='logout')
]
