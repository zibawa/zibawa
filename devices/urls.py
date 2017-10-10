from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^testMessage/$', views.testMessage, name='test_message'),
    url(r'^api_v1/$', views.testMessage, name='api_v1'),
    url(r'^(?P<device_id>[0-9]+)/resetPsw/$', views.resetPsw, name='resetPsw'),
    url(r'^download_CA_cert/$', views.download_CA_cert, name='download_CA_cert'),
    
]
