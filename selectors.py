# -*- coding: utf-8 -*-

from nodefs.lib.selectors import Selector
from nodefs.lib.model import Node
from django.core.files import File
import re


class ModelSelector(Selector):

    def __init__(self, projection, model_class):
        self.model_class = model_class
        self.projection = projection

    def get_nodes(self, abstract_node, base_node=None):
        nodes = set()
        query_set = self.get_query_set(base_node, abstract_node)

        for obj in query_set.all():
            projection = self.parse_projection(obj)
            nodes.add(Node(
                abstract_node=abstract_node,
                parent=base_node,
                pattern=projection,
            ))

        return list(nodes)

    def get_query_set(self, base_node, abstract_node=None):
        criteria = self.model_class.objects

        if not abstract_node:
            abstract_node = base_node.abstract_node

        #if base_node and 'first_things/FirstThingOfBox1' in base_node.path:
            #import ipdb; ipdb.set_trace()

        for node in self.get_selector_nodes(base_node):
            criteria = criteria.filter(**node.abstract_node.selector.get_filter(node.pattern, abstract_node))

        criteria.only(*self.parse_imediate_fields()).distinct()

        if hasattr(criteria, 'get_query_set'):
            criteria = criteria.get_query_set()

        return criteria

    def get_filter(self, pattern, abstract_node):
        filter_query = {}
        parsed_fields = self.parse_fields()
        parsed_values = self.parse_pattern_values(pattern)

        for i in range(len(parsed_fields)):
            if abstract_node.selector.model_class is not self.model_class:
                field_names = []
                meta = abstract_node.selector.model_class._meta

                for fname in meta.get_all_field_names():
                    field = meta.get_field_by_name(fname)[0]

                    if hasattr(field, 'field') and field.model == self.model_class:
                        field_names.append(fname)

                    elif hasattr(field, 'rel') and field.rel and field.rel.to == self.model_class:
                        field_names.append(fname)

                if len(field_names) == 1:
                    parsed_fields[i] = field_names[0] + '.' + parsed_fields[i]
                else:
                    raise Exception("more than 1 way to find column")

            field_filter = parsed_fields[i].replace(".", "__")
            filter_query[field_filter] = parsed_values[i]

        return filter_query

    def get_selector_nodes(self, base_node):
        model_selector_nodes = []
        current_node = base_node

        while(current_node):
            if isinstance(current_node.abstract_node.selector, ModelSelector):
                model_selector_nodes.append(current_node)

            current_node = current_node.parent

        return model_selector_nodes

    def matches_node_pattern(self, parent_node, pattern):
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


class ModelFileSelector(ModelSelector):
    """
    Mostra o arquivo do nó selecionado.
    Este arquivo será o único filho gerado por este seletor.

    Ex.:
        boxes_of_things/ <--- StaticSelector - Gera somente este nó
            B1-1234567890/ <--- ModelSelector - Gera N nós
                FirstThingOfBox1/ <--- ModelSelector - Gera N nós
                    arquivo.txt <--- ModelFileSelector - Gera somente este nó,
                                     que é o arquvio do Thing(label=FirstThingOfBox1)
    """

    file_field_name = None
    is_leaf_generator = True

    def __init__(self, projection, file_field_name, model_class):
        self.projection = projection
        self.model_class = model_class
        self.file_field_name = file_field_name

    def get_nodes(self, abstract_node, base_node=None):
        nodes = super(ModelFileSelector, self).get_nodes(abstract_node, base_node)

        if len(nodes) > 1:
            raise Exception('ModelFileSelector.get_nodes should not return more than one node')

        if not nodes[0].pattern:
            return []

        nodes[0].is_leaf = True

        from os.path import basename

        nodes[0].pattern = basename(nodes[0].pattern)

        return nodes

    def read_node_contents(self, node, size=-1, offset=0):
        return self.get_object_file_field(node).read()

    def write_node_contents(self, node, data, reset=False):
        mode = reset and 'w' or 'a'

        with open(self.get_object_file_field(node).path, mode) as f:
            f.write(data)
            f.close()

    def node_contents_length(self, node):
        try:
            return len(self.get_object_file_field(node))
        except:
            return 0

    def add_node(self, node):
        from tempfile import mkstemp
        from os import remove as rm

        obj = self.get_object(node)
        tmp_f = open(mkstemp()[1])
        f = File(tmp_f)
        f.name = node.pattern

        old_file = getattr(obj, self.file_field_name)

        if old_file:
            rm(old_file.name)

        setattr(obj, self.file_field_name, f)
        obj.save()

        tmp_f.close()
        rm(tmp_f.name)

    def get_filter(self, pattern, abstract_node):
        """Overriden method to avoid to use this projection as a search pattern"""
        return {}

    def get_object(self, node):
        return self.get_query_set(node).all()[0]

    def get_object_file_field(self, node):
        return getattr(self.get_object(node), self.file_field_name)


class QuerySetSelector(ModelSelector):

    def __init__(self, projection, query_set, append=True):

        if hasattr(query_set, 'get_query_set'):
            query_set = query_set.get_query_set()

        self.model_class = query_set.model
        self.custom_query_set = query_set
        self.projection = projection
        self.append_query_set = append

    def get_query_set(self, base_node, abstract_node=None):
        criteria = super(QuerySetSelector, self).get_query_set(base_node, abstract_node)

        if self.append_query_set:
            criteria = criteria & self.custom_query_set
        else:
            criteria = criteria | self.custom_query_set

        return criteria
