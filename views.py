import json
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django_nodefs.selectors import ModelSelector, ModelFileSelector
from django.shortcuts import render_to_response
from django.template import RequestContext

from nodefs.lib.model import NodeManager
from nodefs.lib import conf

from contas.conf import nodefs_schema
from contas.controle.models import Conta, Controle


def tree_widget(request):
    return render_to_response('django_nodefs/tree_widget.html', {
        'tree': tree(request)
    }, RequestContext(request))


def tree_json(request):
    data = tree(request)

    return HttpResponse(json.dumps(data['children']), mimetype='application/json')


def tree(request):
    conf.node_profiles = nodefs_schema.schema
    root_node = NodeManager().search_by_path('/')

    return build_tree(root_node, request.GET.get('current_url', ''))


def build_tree(node, current_url=None):
    tree = {'id': node.id, 'label': node.pattern, 'children': []}
    nodeselector = node.abstract_node.selector

    if isinstance(nodeselector, ModelSelector):
        obj = nodeselector.get_object(node)
        url = None

        if issubclass(nodeselector.model_class, Controle):
            url = reverse('controle.views.editar', kwargs={'mes': obj.mes, 'ano': obj.ano})

        elif issubclass(nodeselector.model_class, Conta) and isinstance(nodeselector, ModelFileSelector):
            url = obj.arquivo.url

        if url:
            tree['label'] = "<a href='%s'>%s</a>" % (url, node.pattern)

            if current_url and url in current_url:
                tree['selected'] = True

    for cnode in node.children:
        tree['children'].append(build_tree(cnode, current_url))

    if not tree['children']:
        del tree['children']

    return tree
