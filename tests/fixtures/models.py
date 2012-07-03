# -*- coding: utf-8 -*-

from django.db import models
from datetime import datetime


class Thing(models.Model):
    label = models.CharField(max_length=128)
    create_date = models.DateTimeField(default=datetime.now)
