"""
URL configuration for DjangoDisability project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/assets/', include('asset.urls', namespace='assets')),
    path('api/categories/', include('category.urls',namespace='categories')),
    path('api/locations/', include('location.urls',namespace='locations')),
    path('api/assetitems/', include('assetitem.urls', namespace='assetitems')),
    path('api/vendors/',include('vendor.urls',namespace='vendors')),
    path('api/users/', include('users.urls')),
    path('api/transfers/', include('transfer.urls', namespace='transfers')),
]
