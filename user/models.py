from django.db import models


# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=20, help_text="用户名")
    phone = models.CharField(max_length=20, help_text="手机号")
    password = models.CharField(max_length=100, help_text="密码")
    is_deleted = models.BooleanField(default=False)
    token=models.FileField(max_length=255,null=True)