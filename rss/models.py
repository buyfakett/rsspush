from django.db import models


class Rss(models.Model):
    user_id = models.IntegerField(help_text="user_id")
    push_id = models.IntegerField(help_text="push_id")
    rss_uri = models.CharField(max_length=20, help_text="用户名")
    detection_time = models.IntegerField(help_text="检测的时间(分钟）")
    timestamp = models.CharField(max_length=20, help_text="上次更新的时间戳")

    class Meta:
        db_table = "rss"
        verbose_name = "rss表"
        verbose_name_plural = "rss表"

    def __str__(self):
        return '%s | %s | %s | %s | %s'%(self.user_id, self.push_id, self.rss_uri, self.detection_time, self.timestamp)
