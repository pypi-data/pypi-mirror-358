#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  cyclic_plugins.py
#
#  Copyright 2021 Jens Rapp <tecdroid@tecdroid>
#
#
#
import logging
import unittest
from stoepsel.stoepsel import PluginManager,  PluginError, PluginVersion

class VersionTest(unittest.TestCase):
    def setUp(self):
        self.version = PluginVersion('1.0.3')

    def test_similar_version(self):
        self.assertTrue(self.version.match('1.0.3'))

    def test_not_similar_version(self):
        self.assertFalse(self.version.match('==1.0.2'))
        self.assertFalse(self.version.match('!=1.0.3'))

    def test_version_bigger_smaller(self):
        self.assertFalse(self.version.match('<1.0.2'))
        self.assertFalse(self.version.match('>1.1.2'))
        self.assertTrue(self.version.match('>=1.0.2'))
        self.assertTrue(self.version.match('>=1.0.3'))

    def test_version_range(self):
        self.assertTrue(self.version.match('>=1.0;<2.0'))


class StoepselTest(unittest.TestCase):

    def test_stoepsel_run(self):
        config = {}
        config['plugin_path'] = 'simple_plugins'
        config['plugin_config'] = {}

        pm = PluginManager(config)
        self.assertIsNotNone(pm)
        main = pm.get_item(PluginManager.PGM_MAIN)
        self.assertIsNotNone(main)
        main()

    def test_cyclic_import(self):
        config = {}
        config['plugin_path'] = 'cyclic_plugins'
        config['plugin_config'] = {}

        with self.assertRaises(PluginError):
            pm = PluginManager(config)
            pm.get_item('__main__')()

    def test_unresolved_import(self):
        config = {}
        config['plugin_path'] = 'unresolved_plugins'
        config['plugin_config'] = {}

        with self.assertRaises(PluginError):
            pm = PluginManager(config)
            pm.get_item('__main__')()

    def test_unmatched_version_import(self):
        config = {}
        config['plugin_path'] = 'unmatched_plugins'
        config['plugin_config'] = {}

        with self.assertRaises(PluginError):
            pm = PluginManager(config)
            pm.get_item('__main__')()

    def test_threaded_plugin(self):
        config = {}
        config['plugin_path'] = 'unmatched_plugins'
        config['plugin_config'] = {}

        with self.assertRaises(PluginError):
            pm = PluginManager(config)
            pm.get_item('__main__')()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()

