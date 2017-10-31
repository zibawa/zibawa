from django.conf.urls import url
from . import views



urlpatterns = [
    
    url(r'^api_v1/$', views.Data_ingest.as_view()),
    url(r'^api_v1/bulk$', views.Data_ingest_bulk.as_view()),
    url(r'^api_v1/upload_file$',views.upload_file, name='upload_file'),
    
]