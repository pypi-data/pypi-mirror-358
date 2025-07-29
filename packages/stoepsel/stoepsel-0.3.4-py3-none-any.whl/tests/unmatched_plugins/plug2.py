from stoepsel import Plugin
import tkinter as tk

class MyPlugin(Plugin):
    name = 'resolved2'
    version = '0.1.0'
    dependencies = ['resolved3##>=0.1.0']

    def setup(self):
        self.logger.info("this will never run")


export = MyPlugin
