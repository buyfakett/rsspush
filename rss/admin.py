from django.contrib import admin
from .models import Rss


class RssManager(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'push_id', 'rss_uri', 'detection_time', 'timestamp']
    # 点击哪个进入编辑页
    list_display_list = ['id']
    # 过滤
    list_filter = ['user_id', 'push_id']
    # 搜索框
    search_fields = ['user_id', 'push_id']
    # 可在列表页编辑的字段
    list_editable = ['user_id', 'push_id', 'rss_uri', 'detection_time', 'timestamp']


admin.site.register(Rss, RssManager)
