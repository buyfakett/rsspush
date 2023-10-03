from django.db import models


class User(models.Model):
    username = models.CharField(max_length=20, help_text="用户名")
    phone = models.CharField(max_length=20, help_text="手机号")
    password = models.CharField(max_length=100, help_text="密码")
    is_deleted = models.BooleanField(default=False)
    token=models.CharField(max_length=255, null=True)

    class Meta:
        db_table = "user"
        verbose_name = "用户表"
        verbose_name_plural = "用户表"

    def __str__(self):
        return '%s | %s | %s | %s | %s'%(self.username, self.phone, self.password, self.is_deleted, self.token)