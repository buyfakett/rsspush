
import push.views
from django.urls import path

urlpatterns = [
    path('view', push.views.PushView.view),
    path('edit', push.views.PushView.edit_push),
    path('delete', push.views.PushView.delete_push),
    path('add', push.views.PushView.add_push),
    path('refresh', push.views.PushView.refresh_push),
]
