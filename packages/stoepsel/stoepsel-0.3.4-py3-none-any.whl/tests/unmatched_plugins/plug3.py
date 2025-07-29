from stoepsel import Plugin
import tkinter as tk

class MyPlugin(Plugin):
    name = 'resolved3'
    version = '0.0.1'
    dependencies = []

    def setup(self):
        self.logger.info("this wil never run. really!   ")


export = MyPlugin
