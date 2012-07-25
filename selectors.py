# -*- coding: utf-8 -*-

from nodefs.lib.selectors import Selector, weights
from nodefs.lib.model import Node
from django.core.files import File
from django.utils.encoding import smart_unicode
from django.db.models.fields.files import FieldFile
import re
import os


class ModelSelector(Selector):
    weight = weights.HEAVY

    def __init__(self, projection, model_class):
        self.model_class = model_class
        self.projection = projection

    def get_nodes(self, child_abstract_node, base_node=None):
        nodes = set()
        query_set = self.get_query_set(base_node)

        for obj in query_set.all():
            projection = self.parse_projection(obj)
            nodes.add(Node(
                abstract_node=child_abstract_node,
                parent=base_node,
                pattern=projection,
            ))

        return list(nodes)

    def get_query_set(self, base_node=None, query_set=None):
        """
            Deve retornar um query set baseado no model_class deste selector
            e filtrado pelos parametros de base_node (recursivamente, considerando os selectors ModelSelector)
        """
        if not query_set:
            query_set = self.model_class.objects.get_query_set()

        if base_node.abstract_node.selector is self:
            query_set = query_set.filter(**self.get_filter(base_node.pattern, query_set))
            base_node = self.get_next_model_selector_node(base_node)

        if base_node and isinstance(base_node.abstract_node.selector, ModelSelector):
            query_set = base_node.abstract_node.selector.get_query_set(base_node, query_set)

        return query_set.only(*self.parse_imediate_fields())

    def get_next_model_selector_node(self, base_node):
        if not base_node:
            return

        node = base_node.parent

        while node and not isinstance(node.abstract_node.selector, ModelSelector):
            node = node.parent

        return node

    def get_filter(self, pattern, query_set):
        filter_query = {}
        parsed_fields = self.parse_fields()
        parsed_values = self.parse_pattern_values(pattern)

        for i in range(len(parsed_fields)):
            if query_set.model is not self.model_class:
                field_names = []
                fname = self.get_query_set_field_name_for_model(query_set, self.model_class)

                if fname:
                    field_names.append(fname)

                if len(field_names) == 1:
                    parsed_fields[i] = field_names[0] + '.' + parsed_fields[i]
                else:
                    raise Exception("more than 1 way to find column")

            elif parsed_fields[i].split('.')[0] not in self.get_model_field_names():
                continue

            field_filter = parsed_fields[i].replace(".", "__")
            filter_query[field_filter] = parsed_values[i]

        return filter_query

    def get_query_set_field_name_for_model(self, query_set, model):
        meta = query_set.model._meta

        for fname in meta.get_all_field_names():
            field = meta.get_field_by_name(fname)[0]

            if hasattr(field, 'model') and field.model == model:
                return fname

            elif hasattr(field, 'rel') and field.rel and field.rel.to == model:
                return fname

    def get_model_field_names(self):
        return self.model_class._meta.get_all_field_names()

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
        field_names = self.get_model_field_names()
        return [f.split(".")[0] for f in self.parse_fields() if f in field_names]

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

            if callable(attr):
                binds[f] = attr()
            else:
                binds[f] = attr

            if isinstance(binds[f], FieldFile):
                binds[f] = os.path.basename(binds[f].name)

        return re.sub(os.sep, "-", smart_unicode(self.projection % binds))


class ModelFileSelector(ModelSelector):
    weight = weights.EXTRA_HEAVY

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

    def get_nodes(self, child_abstract_node, base_node=None):
        nodes = super(ModelFileSelector, self).get_nodes(child_abstract_node, base_node)

        if len(nodes) > 1:
            raise Exception('ModelFileSelector.get_nodes should not return more than 1 node')

        if not nodes or not nodes[0].pattern:
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
            return len(self.get_object_file_name(node))
        except:
            return 0

    def add_node(self, node):
        from tempfile import mkstemp
        from os import remove as rm

        obj = self.get_object(node.parent)
        tmp_f = open(mkstemp()[1])
        f = File(tmp_f)
        f.name = node.pattern

        old_file = getattr(obj, self.file_field_name)

        if old_file:
            try:
                rm(old_file.name)
            except OSError:
                import logging

                logging.warning("%(class)s:%(pattern)s on %(method)s: could not remove file %(file_name)s" % {
                    'pattern': node.pattern,
                    'class': type(self).__module__ + "." + type(self).__name__,
                    'method': 'add_node',
                    'file_name': old_file.name,
                })

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

    def get_object_file_name(self, node):
        return os.path.basename(self.get_object_file_field(node).name)


class QuerySetSelector(ModelSelector):

    def __init__(self, projection, query_set, append=True):

        if hasattr(query_set, 'get_query_set'):
            query_set = query_set.get_query_set()

        self.model_class = query_set.model
        self.custom_query_set = query_set
        self.projection = projection
        self.append_query_set = append

    def get_query_set(self, base_node, query_set=None):
        query_set = super(QuerySetSelector, self).get_query_set(base_node, query_set)
        custom_query_set = self.custom_query_set

        if query_set.model is not custom_query_set.model:
            params = {}
            params[self.get_query_set_field_name_for_model(query_set, custom_query_set.model)] = custom_query_set
            custom_query_set = query_set.filter(**params)

        if self.append_query_set:
            query_set = query_set & custom_query_set
        else:
            query_set = query_set | custom_query_set

        return query_set
