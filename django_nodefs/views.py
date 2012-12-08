# -*- coding: utf-8 -*-

import os
import sys
import re
import json

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings

from django_nodefs.selectors import ModelSelector
from nodefs.lib.model import NodeManager
from nodefs.lib import conf

DEFAULT_PATH = '/'

if hasattr(settings, 'NODEFS_TREE_DEFAULT_PATH'):
    DEFAULT_PATH = settings.NODEFS_TREE_DEFAULT_PATH

if hasattr(settings, 'NODEFS_PROFILE_MODULE') and not os.environ.get('NODEFS_PROFILE_MODULE'):
    os.environ['NODEFS_PROFILE_MODULE'] = settings.NODEFS_PROFILE_MODULE

from nodefs.lib import profile


def tree_widget(request):
    return render_to_response('django_nodefs/tree_widget.html', {
        'tree': tree(request)
    }, RequestContext(request))


def tree_json(request):
    data = tree(request)

    return HttpResponse(json.dumps(data['children']), mimetype='application/json')


def tree(request):
    conf.node_profiles = profile.schema
    root_node = NodeManager().search_by_path(get_default_path())

    return build_tree(root_node, request.GET.get('current_url', ''))


def build_tree(node, current_url=None):
    tree = {'id': node.id, 'label': node.pattern, 'children': []}
    nodeselector = node.abstract_node.selector

    if isinstance(nodeselector, ModelSelector):
        url = get_node_url(node, nodeselector)

        if url:
            tree['label'] = "<a href='%s'>%s</a>" % (url, node.pattern)

            if current_url and url in current_url:
                tree['selected'] = True

    for cnode in node.children:
        tree['children'].append(build_tree(cnode, current_url))

    if len(tree['children']) == 0:
        del tree['children']

    return tree


def get_node_url(node, nodeselector):
    url = None
    callback = get_callback_from_settings('NODEFS_TREE_DISCOVER_URL_CALLBACK')

    if callable(callback):
        url = callback(node, nodeselector)

    return url


def get_default_path():
    path = DEFAULT_PATH
    callback = get_callback_from_settings('NODEFS_TREE_DYNAMIC_PATH_CALLBACK')

    if callback:
        path = callback()

    return path


def get_callback_from_settings(settings_var):
    if hasattr(settings, settings_var):
        callback_path = getattr(settings, settings_var)
        callback_import, callback_function_name = re.findall(r'^([\w.]+?)\.(\w+)$', callback_path)[0]

        __import__(callback_import)
        callback = getattr(sys.modules[callback_import], callback_function_name)

        return callback
