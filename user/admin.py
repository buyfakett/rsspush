from django.contrib import admin
from .models import User


class UserManager(admin.ModelAdmin):
    list_display = ['id', 'username', 'phone', 'password', 'is_deleted', 'token']
    # 点击哪个进入编辑页
    list_display_list = ['id']
    # 过滤
    list_filter = ['username']
    # 搜索框
    search_fields = ['username', 'phone']
    # 可在列表页编辑的字段
    list_editable = ['username', 'phone', 'password', 'is_deleted', 'token']


admin.site.register(User, UserManager)
