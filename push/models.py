from django.db import models


class Push(models.Model):
    push_type = models.CharField(max_length=20, help_text="钉钉推送还是微信测试号推送(钉钉：ding，微信测试号：wechat)")
    ding_access_token = models.CharField(max_length=100, help_text="钉钉参数", null=True)
    ding_keyword = models.CharField(max_length=255, help_text="钉钉自定义关键词", null=True)
    wechat_template_id = models.CharField(max_length=100, help_text="微信模板id", null=True)
    wechat_app_id = models.CharField(max_length=100, help_text="微信appId", null=True)
    wechat_to_user_ids = models.TextField(help_text="微信发送的用户们", null=True)

    class Meta:
        db_table = "push"
        verbose_name = "push表"
        verbose_name_plural = "push表"

    def __str__(self):
        return '%s | %s | %s | %s | %s | %s'%(self.push_type, self.ding_access_token, self.ding_keyword, self.wechat_template_id, self.wechat_app_id, self.wechat_to_user_ids)
