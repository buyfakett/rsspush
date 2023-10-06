from django.contrib import admin
from .models import Push


class PushManager(admin.ModelAdmin):
    list_display = ['id', 'push_type', 'ding_access_token', 'ding_keyword', 'wechat_template_id', 'wechat_app_id', 'wechat_to_user_ids']
    # 点击哪个进入编辑页
    list_display_list = ['id']
    # 过滤
    list_filter = ['push_type', 'ding_access_token', 'ding_keyword', 'wechat_template_id', 'wechat_app_id']
    # 搜索框
    search_fields = ['push_type', 'ding_access_token', 'ding_keyword', 'wechat_template_id', 'wechat_app_id']
    # 可在列表页编辑的字段
    list_editable = ['push_type', 'ding_access_token', 'ding_keyword', 'wechat_template_id', 'wechat_app_id', 'wechat_to_user_ids']


admin.site.register(Push, PushManager)
