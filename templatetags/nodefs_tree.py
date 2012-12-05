# -*- coding: utf-8 -*-

from django.template.loader import render_to_string
from django import template

register = template.Library()


@register.simple_tag
def render_nodefs_tree():
    #return mark_safe()
    return render_to_string('django_nodefs/nodefs_tree.html')
