from django.conf.urls import url
from . import views



urlpatterns = [
    
    url(r'^api_v1/$', views.SnippetList.as_view()),
    
]