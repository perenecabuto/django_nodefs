# -*- coding: utf-8 -*-

from node_fs.lib.selectors import Selector
from node_fs.lib.model import Node
import re


class ModelSelector(Selector):

    def __init__(self, projection, model_class):
        self.model_class = model_class
        self.projection = projection

    def get_nodes(self, abstract_node, base_node=None):
        nodes = []
        objects = self.model_class.objects

        for obj in objects.all():
            projection = self.parse_projection(obj)
            nodes.append(Node(
                abstract_node=abstract_node,
                parent=base_node,
                pattern=projection,
            ))

        return nodes

    def parse_projection(self, obj):
        obj_fields = re.findall("%\((.*?)\)", self.projection)
        binds = dict((f, getattr(obj, f)) for f in obj_fields)

        return self.projection % binds
