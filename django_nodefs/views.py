import json
import sys
import re

from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django_nodefs.selectors import ModelSelector, ModelFileSelector
from django.shortcuts import render_to_response
from django.template import RequestContext

from nodefs.lib.model import NodeManager
from nodefs.lib import conf

from contas.conf import nodefs_schema
from django.conf import settings

DEFAULT_PATH = '/'

if hasattr(settings, 'DJANGO_NODEFS_TREE_DEFAULT_PATH'):
    DEFAULT_PATH = settings.DJANGO_NODEFS_TREE_DEFAULT_PATH


def tree_widget(request):
    return render_to_response('django_nodefs/tree_widget.html', {
        'tree': tree(request)
    }, RequestContext(request))


def tree_json(request):
    data = tree(request)

    return HttpResponse(json.dumps(data['children']), mimetype='application/json')


def tree(request):
    conf.node_profiles = nodefs_schema.schema
    root_node = NodeManager().search_by_path(get_default_path())

    return build_tree(root_node, request.GET.get('current_url', ''))


def build_tree(node, current_url=None):
    tree = {'id': node.id, 'label': node.pattern, 'children': []}
    nodeselector = node.abstract_node.selector

    if isinstance(nodeselector, ModelSelector):
        url = None

        # Abs
        from contas.controle.models import Conta, Controle

        if 'este_ano' in node.path and issubclass(nodeselector.model_class, Controle):
            obj = nodeselector.get_object(node)
            url = reverse('controle.views.editar', kwargs={'mes': obj.mes, 'ano': obj.ano})

        elif issubclass(nodeselector.model_class, Conta) and isinstance(nodeselector, ModelFileSelector):
            obj = nodeselector.get_object(node)
            url = obj.arquivo.url
        # EndAbs

        if url:
            tree['label'] = "<a href='%s'>%s</a>" % (url, node.pattern)

            if current_url and url in current_url:
                tree['selected'] = True

    for cnode in node.children:
        tree['children'].append(build_tree(cnode, current_url))

    if len(tree['children']) == 0:
        del tree['children']

    return tree


def get_default_path():
    path = DEFAULT_PATH

    if hasattr(settings, 'DJANGO_NODEFS_TREE_DYNAMIC_PATH_CALLBACK'):
        callback_path = settings.DJANGO_NODEFS_TREE_DYNAMIC_PATH_CALLBACK
        callback_import, callback_function_name = re.findall(r'^([\w.]+?)\.(\w+)$', callback_path)[0]

        __import__(callback_import)
        callback = getattr(sys.modules[callback_import], callback_function_name)

        path = callback()

    return path
