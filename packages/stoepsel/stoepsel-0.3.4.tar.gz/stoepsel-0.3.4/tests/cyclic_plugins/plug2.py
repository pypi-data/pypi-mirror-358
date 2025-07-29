from stoepsel import Plugin
import tkinter as tk

class MyPlugin(Plugin):
    name = 'cyclic2'
    version = '0.0.1'
    dependencies = ['cyclic3##0.0.1']

    def setup(self):
        self.logger.info("this will never run")


export = MyPlugin
