
import push.views
from django.urls import path

urlpatterns = [
    path('push', push.views.RssView.push),
]
