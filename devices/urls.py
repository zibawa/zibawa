from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^testMessage/$', views.testMessage, name='test_message'),
    url(r'^(?P<device_id>[0-9]+)/resetPsw/$', views.resetPsw, name='resetPsw'),
]
