# -*- coding: utf-8 -*-

from django.test import TestCase
from django.db import connection
from node_fs.lib.model import NodeManager
from node_fs.lib import conf
from fixtures import profiles

conf.node_profiles = profiles.schema


class FunctionalTest(TestCase):
    fixtures = ['tests/fixtures/things']

    @classmethod
    def setUpClass(cls):
        cls.creator = connection.creation
        cls.creator.create_test_db(2, True)
        cls.node_manager = NodeManager()

    @classmethod
    def tearDownClass(cls):
        cls.creator.destroy_test_db('default')

    def test_should_list_things_on_root_path(self):
        """docstring for test_should_list_nodes_as_in_profile"""
        node = self.node_manager.search_by_path('/')
        self.assertGreater(len(node.children), 0)

    #def test_should_mount_fs(self):
        #"""Mounting fs"""
        #raise NotImplemented()
