from django.db import models

# Create your models here.
from django.db import models


class hotNewsTable(models.Model):
    title = models.CharField('名称', max_length=512, help_text='热点新闻')
    objects = models.Manager()

    class Meta:
        db_table = "hotnewstable"
