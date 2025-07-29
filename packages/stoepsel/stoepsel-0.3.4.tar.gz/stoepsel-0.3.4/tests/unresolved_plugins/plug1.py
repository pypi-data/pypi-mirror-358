from stoepsel import Plugin
import tkinter as tk

class MyPlugin(Plugin):
    name = 'resolved1'
    version = '0.0.1'
    dependencies = ['unresolved##>=0.0.1;<1.0']

    def setup(self):
        self.logger.info("this will never run")
        self.register(self.PGM_MAIN,self.main)

    def main(self):
        print('i\'d be scared if this would work')

export = MyPlugin
