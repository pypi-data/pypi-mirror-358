from stoepsel import Plugin
import tkinter as tk

class MyPlugin(Plugin):
    name = 'myplugin'
    version = '0.0.1'
    dependencies = []

    def setup(self):
        self.logger.info("Hello World")


export = MyPlugin
