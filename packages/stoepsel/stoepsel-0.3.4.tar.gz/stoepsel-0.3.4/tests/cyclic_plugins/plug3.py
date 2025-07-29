from stoepsel import Plugin
import tkinter as tk

class MyPlugin(Plugin):
    name = 'cyclic3'
    version = '0.0.1'
    dependencies = ['cyclic1##0.0.1']

    def setup(self):
        self.logger.info("this wil never run. really!   ")


export = MyPlugin
