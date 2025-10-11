"""
URL configuration for web project.

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
import web.settings as sett
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ckeditor',include('ckeditor_uploader.urls')),
    path('',include('apps.main.urls',namespace='main')),
    path('accounts/',include('apps.user.urls',namespace='account')),
    path('file/',include('apps.file.urls',namespace='file')),
    path('order/',include('apps.order.urls',namespace='order')),
    path('discounts/',include('apps.discount.urls',namespace='discount')),
    path('peyment/',include('apps.peyment.urls',namespace='peyment')),
    path('panel/',include('apps.panel.urls',namespace='panel')),
    path('search/',include('apps.search.urls',namespace='search')),
    path('',include('apps.blog.urls',namespace='blog')),
    path('course/',include('apps.course.urls',namespace='course')),
    path('ticket/',include('apps.ticket.urls',namespace='ticket')),
]+static(sett.MEDIA_URL,document_root = sett.MEDIA_ROOT)
