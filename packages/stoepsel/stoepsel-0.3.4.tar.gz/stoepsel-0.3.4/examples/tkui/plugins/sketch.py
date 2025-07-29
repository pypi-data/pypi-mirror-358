from stoepsel import Plugin
import tkinter as tk

class SketchPlugin(Plugin):
    name = 'sketch'
    version = '0.0.1'
    dependencies = ['tkmain##0.0.1']

    def setup(self):
        self.content = 'Hallo Welt'
        self.register('menu/test/hitme', self.menu_test_hitme)


    def menu_test_hitme(self, **kwargs):
        self.logger.info("You hit me!")

export = SketchPlugin
