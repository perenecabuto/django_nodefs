# -*- coding: utf-8 -*-

from django.test import TestCase
from django.db import connection
from nodefs.lib.model import NodeManager
from nodefs.lib import conf
from fixtures import nodefs_schema
from management.commands.nodefs_mount import Command

import shutil
import os

conf.node_profiles = nodefs_schema.schema


class FunctionalTest(TestCase):
    fixtures = ['tests/fixtures/things']

    @classmethod
    def setUpClass(cls):
        cls.creator = connection.creation
        cls.creator.create_test_db(2, True)
        cls.node_manager = NodeManager()

    @classmethod
    def tearDownClass(cls):
        try:
            shutil.rmtree(os.path.join(os.path.dirname(__file__), '..', 'static'))
        except OSError:
            pass

        cls.creator.destroy_test_db('default')

    def test_should_list_root(self):
        node = self.node_manager.search_by_path('/')
        self.assertGreater(len(node.children), 0)

    def test_should_list_things(self):
        node = self.node_manager.search_by_path('/simple_things')
        self.assertGreater(len(node.children), 0)
        self.assertItemsEqual(
            [
                'FirstThingOfBox1', 'SecondThingOfBox1', 'ThirdThingOfBox1', 'RepeatedThingLabel',
                'FirstThingOfBox2', 'SecondThingOfBox2', 'ThirdThingOfBox2'
            ],
            [n.pattern for n in node.children]
        )

    def test_should_get_year_nodes(self):
        node = self.node_manager.search_by_path('/nested_things')
        self.assertEqual(len(node.children), 2)
        self.assertEqual('2011', node.children[0].pattern)
        self.assertEqual('2012', node.children[1].pattern)

    def test_should_get_month_nodes(self):
        node_2011 = self.node_manager.search_by_path('/nested_things/2011/')
        node_2012 = self.node_manager.search_by_path('/nested_things/2012/')
        self.assertEqual(len(node_2012.children), 3)
        self.assertEqual(len(node_2011.children), 1)
        self.assertItemsEqual(['12'], [n.pattern for n in node_2011.children])
        self.assertItemsEqual(['5', '6', '7'], [n.pattern for n in node_2012.children])

    def test_should_get_box_of_things(self):
        node = self.node_manager.search_by_path('/boxes_of_things')
        self.assertEqual(len(node.children), 2)
        self.assertEqual('B1-1234567890', node.children[0].pattern)
        self.assertEqual('B2-1234567890', node.children[1].pattern)

    def test_should_get_things_in_boxes(self):
        box1_node = self.node_manager.search_by_path('/boxes_of_things/B1-1234567890')
        box2_node = self.node_manager.search_by_path('/boxes_of_things/B2-1234567890')

        self.assertItemsEqual(
            ['FirstThingOfBox1', 'SecondThingOfBox1', 'ThirdThingOfBox1', 'RepeatedThingLabel'],
            [n.pattern for n in box1_node.children]
        )

        self.assertItemsEqual(
            ['FirstThingOfBox2', 'SecondThingOfBox2', 'ThirdThingOfBox2', 'RepeatedThingLabel'],
            [n.pattern for n in box2_node.children]
        )

    def test_should_get_filtred_things(self):
        node = self.node_manager.search_by_path('/pre_filtered_things/first_things')

        self.assertItemsEqual(
            ('FirstThingOfBox1', 'FirstThingOfBox2'),
            (n.pattern for n in node.children)
        )

    def test_should_get_the_box_of_filtered_thing(self):
        node = self.node_manager.search_by_path('/pre_filtered_things/first_things/FirstThingOfBox1')

        self.assertIn('_B1-1234567890', [n.pattern for n in node.children])

        node = self.node_manager.search_by_path('/pre_filtered_things/first_things/FirstThingOfBox1/_B1-1234567890')
        self.assertTrue(not node.is_leaf)

    def test_should_get_the_file_of_filtered_thing_of_box1(self):
        node = self.node_manager.search_by_path('/pre_filtered_things/first_things/FirstThingOfBox1')
        file_name = os.path.basename(__file__)

        self.assertIn('passwd', [n.pattern for n in node.children])

        node.create_child_by_pattern(file_name)

        self.assertIn(file_name, [n.pattern for n in node.children])

    def test_should_get_the_file_of_filtered_thing_of_box2(self):
        node = self.node_manager.search_by_path('/pre_filtered_things/first_things/FirstThingOfBox2')
        file_name = os.path.basename(__file__)

        self.assertIn('passwd', [n.pattern for n in node.children])

        node.create_child_by_pattern(file_name)

        self.assertIn(file_name, [n.pattern for n in node.children])

    def test_should_get_contents_of_file_from_filtered_thing_of_box_1(self):
        node = self.node_manager.search_by_path('/pre_filtered_things/repeated_things/box_1/RepeatedThingLabel')
        self.assertIn('passwd', [n.pattern for n in node.children])

        node = self.node_manager.search_by_path('/pre_filtered_things/repeated_things/box_1/RepeatedThingLabel/passwd')
        self.assertTrue(node)

    def test_should_get_related_things_by_its_box(self):
        node = self.node_manager.search_by_path('/pre_filtered_things/first_things/FirstThingOfBox1/_B1-1234567890')

        self.assertItemsEqual(
            ('SecondThingOfBox1', 'ThirdThingOfBox1'),
            (n.pattern for n in node.children)
        )

    #def test_should_mount_fs(self):
        #"""Mounting fs"""
        #raise NotImplemented()


#class TestCommand(TestCase):

    #def test_instance(self):
        #command = Command()
        #self.assertTrue(command)

    #def test_handle_needs_path_on_args(self):
        #import os

        #command = Command()
        #command.handle(os.path.dirname(__file__) + '/../mnt')
