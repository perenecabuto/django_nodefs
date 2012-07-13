# -*- coding: utf-8 -*-

import shutil
import os

from django.test import TestCase
from django.db import connection
from django.core.files import File
from mock import mocksignature
from selectors import ModelSelector, ModelFileSelector
from nodefs.lib.model import Node, AbstractNode
from fixtures.models import BoxOfThings, Thing
from management.commands.nodefs_actions import Command


class TestModelSelector(TestCase):
    fixtures = ['tests/fixtures/things']

    @classmethod
    def setUpClass(cls):
        cls.creator = connection.creation
        cls.creator.create_test_db(2, True)

    @classmethod
    def tearDownClass(cls):
        cls.creator.destroy_test_db('default')

    def test_instance(self):
        selector = ModelSelector(projection="%(label)s", model_class=Thing)

        self.assertTrue(selector)

    def test_parse_projection(self):
        selector = ModelSelector(projection="%(label)s", model_class=Thing)
        thing = Thing(label='Test')

        self.assertEqual(selector.parse_projection(thing), thing.label)

    def test_get_nodes(self):
        selector = ModelSelector(projection="%(label)s", model_class=Thing)

        abstract_node_class = mocksignature(AbstractNode, AbstractNode)
        abstract_node = abstract_node_class(self)
        nodes = selector.get_nodes(abstract_node)

        self.assertIsInstance(nodes, list)
        self.assertGreater(len(nodes), 0)


class TestModelFileSelector(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.creator = connection.creation
        cls.creator.create_test_db(2, True)

    @classmethod
    def tearDownClass(cls):
        cls.creator.destroy_test_db('default')

    def setUp(self):
        self.thing = Thing.objects.create(
            label='test_thing',
            content_file=File(open(__file__)),
            box=BoxOfThings.objects.create(serial_number='1234')
        )

    def tearDown(self):
        shutil.rmtree(os.path.join(os.path.dirname(__file__), '..', 'static'))

    def test_instance(self):
        selector = ModelFileSelector(projection='%(content_file)s', file_field_name='content_file', model_class=Thing)
        self.assertTrue(selector)

    def test_get_nodes(self):
        from os.path import basename

        selector = ModelFileSelector(projection='%(content_file)s', file_field_name='content_file', model_class=Thing)
        nodes = selector.get_nodes(AbstractNode(selector))

        expected_cotent_file_name = basename(__file__)

        self.assertIsInstance(nodes, list)
        self.assertEqual(len(nodes), 1)
        self.assertEqual(basename(nodes[0].pattern), expected_cotent_file_name)

    def test_read_node_contents(self):
        selector = ModelFileSelector(projection='%(content_file)s', file_field_name='content_file', model_class=Thing)
        node = selector.get_nodes(AbstractNode(selector))[0]

        expected_contents = open(__file__).read()

        self.assertEqual(selector.read_node_contents(node), expected_contents)

    def test_write_node_contents(self):
        selector = ModelFileSelector(projection='%(content_file)s', file_field_name='content_file', model_class=Thing)
        node = selector.get_nodes(AbstractNode(selector))[0]

        expected_contents = 'Blah blah blah'

        node.write_contents(expected_contents, reset=True)
        self.assertEqual(selector.read_node_contents(node), expected_contents)

        node.write_contents(expected_contents, reset=False)
        self.assertEqual(selector.read_node_contents(node), expected_contents * 2)

    def test_node_contents_length(self):
        selector = ModelFileSelector(projection='%(content_file)s', file_field_name='content_file', model_class=Thing)
        node = selector.get_nodes(AbstractNode(selector))[0]

        with open(__file__) as f:
            f.seek(0, 2)
            expected_file_size = f.tell()
            f.close()

        self.assertEqual(selector.node_contents_length(node), expected_file_size)

    def test_add_node(self):
        selector = ModelFileSelector(projection='%(content_file)s', file_field_name='content_file', model_class=Thing)
        abs_node = AbstractNode(selector)
        new_node = Node(abstract_node=abs_node, pattern='text_file.txt')

        selector.add_node(new_node)

        node = selector.get_nodes(abs_node)[0]

        self.assertEqual(node.pattern, new_node.pattern)


class TestCommand(TestCase):

    def test_instance(self):
        command = Command()
        self.assertTrue(command)

    def test_handle_needs_path_on_args(self):
        command = Command()
        command.handle('mnt/')
