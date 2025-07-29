from stoepsel import Plugin, entrymethod, threaded
import time

class MyPlugin(Plugin):
    name = 'simple_plugin'
    version = '0.0.1'
    dependencies = []

    @entrymethod(Plugin.PGM_MAIN)
    @threaded
    def main1(self):
        print('thread 1 running around...')
        time.sleep(.51)
        print("thread 1 ended")

    @entrymethod(Plugin.PGM_MAIN)
    @threaded
    def main2(self):
        print('thread 2 unning around...')
        time.sleep(1)
        print("thread 2 ended")


