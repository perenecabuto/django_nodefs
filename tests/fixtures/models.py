# -*- coding: utf-8 -*-

from django.db import models
from datetime import datetime


class BoxOfThings(models.Model):
    serial_number = models.CharField(max_length=128)


class Thing(models.Model):
    label = models.CharField(max_length=128)
    create_date = models.DateTimeField(default=datetime.now)
    box = models.ForeignKey(BoxOfThings)
