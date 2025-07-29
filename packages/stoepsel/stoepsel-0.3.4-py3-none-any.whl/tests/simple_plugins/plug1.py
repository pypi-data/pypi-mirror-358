from stoepsel import Plugin, entrymethod

class MyPlugin(Plugin):
    name = 'simple_plugin'
    version = '0.0.1'
    dependencies = []

    @entrymethod(Plugin.PGM_MAIN)
    def main(self):
        print('Running around...')

