
import push.views
from django.urls import path

urlpatterns = [
    path('view', push.views.RssView.view),
    path('edit', push.views.RssView.edit_push),
    path('del', push.views.RssView.delete_push),
    path('add', push.views.RssView.add_push),
    path('refresh', push.views.RssView.refresh_push),
]
