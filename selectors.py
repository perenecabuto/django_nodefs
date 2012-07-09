# -*- coding: utf-8 -*-

from node_fs.lib.selectors import Selector
from node_fs.lib.model import Node
import re


class ModelSelector(Selector):

    def __init__(self, projection, model_class):
        self.model_class = model_class
        self.projection = projection

    def get_nodes(self, abstract_node, base_node=None):
        nodes = set()
        criteria = self.model_class.objects

        for node in self.get_selector_nodes(base_node):
            criteria = criteria.filter(**node.abstract_node.selector.get_filter(node.pattern, abstract_node))

        #print "\n---->"
        #print criteria.all().query
        #print "<----\n"

        for obj in criteria.only(*self.parse_imediate_fields()).distinct():
            projection = self.parse_projection(obj)
            nodes.add(Node(
                abstract_node=abstract_node,
                parent=base_node,
                pattern=projection,
            ))

        return nodes

    def get_filter(self, pattern, abstract_node=None):
        filter_query = {}
        parsed_fields = self.parse_fields()
        parsed_values = self.parse_pattern_values(pattern)

        for i in range(len(parsed_fields)):
            if abstract_node.selector.model_class is not self.model_class:
                fields = abstract_node.selector.model_class._meta.fields
                f = [f for f in fields if f.rel and f.rel.to == self.model_class]

                if len(f) == 1:
                    parsed_fields[i] = f[0].name + '.' + parsed_fields[i]
                else:
                    raise Exception("more than 1 way to find column")

            field_filter = parsed_fields[i].replace(".", "__")
            filter_query[field_filter] = parsed_values[i]

        return filter_query

    def get_selector_nodes(self, base_node):
        model_selector_nodes = []
        current_node = base_node

        while(current_node):
            if type(current_node.abstract_node.selector) is ModelSelector:
                model_selector_nodes.append(current_node)

            current_node = current_node.parent

        return model_selector_nodes

    def matches_node_pattern(self, abstract_node, pattern):
        return bool(self.parse_pattern_values(pattern))

    def parse_pattern_values(self, pattern):
        parsed_pattern = re.sub(r"%\([^)]+\)(.)", r"#TYPE#\1#TYPE#", self.projection)
        pattern_types = re.findall(r'#TYPE#(.+?)#TYPE#', parsed_pattern)

        type_matchers = {
            's': r'.+',
            'd': r'\d+',
            'f': r'[\d.]+',
        }

        pattern_str = re.sub(r"#TYPE#\w#TYPE#", r"(%s)", parsed_pattern)
        pattern_re = pattern_str % tuple(type_matchers[t] for t in pattern_types)
        pattern_values = re.match(pattern_re, pattern)

        if pattern_values:
            return pattern_values.groups()

        return []

    def parse_imediate_fields(self):
        return [f.split(".")[0] for f in self.parse_fields()]

    def parse_fields(self):
        return re.findall("%\((.*?)\)", self.projection)

    def parse_projection(self, obj):
        obj_fields = self.parse_fields()
        binds = {}

        for f in obj_fields:
            sub_fields = f.split(".")
            attr = getattr(obj, sub_fields[0])

            for sub_f in sub_fields[1:]:
                attr = getattr(attr, sub_f)

            binds[f] = attr

        return self.projection % binds


class ModelFileSelector(Selector):
    pass
