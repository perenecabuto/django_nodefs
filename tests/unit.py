# -*- coding: utf-8 -*-

from django.test import TestCase
from django.db import connection
from mock import mocksignature
from selectors import ModelSelector
from node_fs.lib.model import AbstractNode
from fixtures.models import Thing


class TestModelSelector(TestCase):
    fixtures = ['tests/fixtures/things']
    multi_db = True

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
        self.assertGreater(len(nodes), 1)
