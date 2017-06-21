from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^new_cert/$', views.new_cert, name='new_cert'),
    url(r'^renew_cert/$', views.renew_cert, name='renew_cert'),
    url(r'^new_ca/$', views.new_ca, name='new_ca'),
   
]
