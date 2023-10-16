"""rsspush URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import path, include, re_path
from django.contrib import admin
from django.views.static import serve
from django.conf import settings

from rest_framework import permissions
from drf_yasg2.views import get_schema_view
from drf_yasg2 import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="rsspush API文档",
        default_version='v1',
        description="rsspush API文档",
        terms_of_service="https://blog.buyfakett.top",
        contact=openapi.Contact(email="buyfakett@vip.qq.com",),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^api/doc(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),  # <-- 这里
    path('api/push/', include('push.urls')),
    path('api/rss/', include('rss.urls')),
    path('api/user/', include('user.urls')),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]


