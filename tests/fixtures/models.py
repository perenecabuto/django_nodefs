# -*- coding: utf-8 -*-

from django.db import models
from datetime import datetime


class BoxOfThings(models.Model):
    serial_number = models.CharField(max_length=128)


class Thing(models.Model):
    label = models.CharField(max_length=128)
    content_file = models.FileField(upload_to='static/%d', blank=True, null=True)
    create_date = models.DateTimeField(default=datetime.now)
    box = models.ForeignKey(BoxOfThings)
