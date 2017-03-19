from django.conf.urls import url
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^createAccount/$', views.createAccount, name='create_account'),
    url(r'^thanks/$', views.thanks, name='thanks'),
    url(r'^accountCreateError/$', views.thanks, name='thanks'),
    url(r'^change_password/$', views.zibawa_password_change,name='password_change'),
    url(r'^change_password/done/$', auth_views.password_change_done,name='password_change_done'),
    url(r'^password_reset/$', auth_views.password_reset,name='password_reset'),
    url(r'^password_reset_done/$', auth_views.password_reset_done,name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.zibawa_password_reset_confirm,name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.password_reset_complete,name='password_reset_complete'),
    url(r'^login/$',auth_views.login, {'template_name': 'login.html' },name='login'),
    url(r'^logout/$',auth_views.logout,{'next_page': '/login/'},name='logout')
]
