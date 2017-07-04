"""zibawa URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin

from django.conf.urls import url, include
from rest_framework import routers
from rest_framework.documentation import include_docs_urls
from IoT_pki import views

router = routers.DefaultRouter()

#router.register(r'cert_request', views.cert_request)
#router.register(r'get_approved_cert',views.get_approved_cert)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]


urlpatterns = [
    
    url(r'^devices/', include('devices.urls',namespace='devices')),
    url(r'^front/', include('front.urls',namespace='front')),
    url(r'^admin/', admin.site.urls),
    url(r'^IoT_pki/', include('IoT_pki.urls',namespace='IoT_pki')),
    url(r'^', include('front.urls')),
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^docs/', include_docs_urls(title='My API title'))
    
    
    
]



