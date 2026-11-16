"""
URL configuration for Managementsystem project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from core.views import health_check

urlpatterns = [
    path('healthz/', health_check, name='health_check'),
    path('admin/', admin.site.urls),
    path('api/core/', include('core.urls')),
    path('api/accounts/', include('accounts.urls')),
    path('api/academics/', include('academics.urls')),
    path('api/students/', include('students.urls')),
    path('api/examinations/', include('examinations.urls')),
    path('api/attendance/', include('attendance.urls')),
    path('api/finance/', include('finance.urls')),
]

# Uploaded files (student photos, documents, school logos). Django serves these
# in every environment: WhiteNoise only handles collected static files, so without
# this every uploaded file 404s once DEBUG is off. Fine for this deployment's
# scale; move MEDIA_ROOT to object storage before uploads need to be durable.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
