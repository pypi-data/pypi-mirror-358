# stoepsel - a simple plug-in system for python

Stoepsel (pronounce ʃtœpsl̩) is an attempt to create a simple (as in
minimalistic) but flexible and powerful plugin system for python.

Stoepsel gives you the ability to develop flexible and scalable applications.
It doesn't matter if you want to build a UI or console program.
You just need to deploy a plugin class to register your application part.

Plugins can use other plugins. Therefore, you can register objects or functions
in a model tree where other plugins can find them.
To make this as safe as possible, a simple dependency resolving algorithm is
implemented.
Plugins are registered by their name and a version. They also can define
dependencies that have to be resolved. (more on that later)

# using stoepsel

## installing stoepsel

you can install stoepsel by using pip

    python3 -m pip install stoepsel

Or just initialize a virtualenv to install from source

    python3 -m venv env
    source env/bin/activate
    python -m pip install .


## running a stoepsel application

A simple stoepsel application can look like this:

    import logging
    from stoepsel import PluginManager

    def main(args):
        logging.basicConfig(level=logging.DEBUG)

        # instanciate PluginManager
        pm = PluginManager()
        # find main and execute it
        pm.get_item(PluginManager.PGM_MAIN)()

        return 0

    if __name__ == '__main__':
        import sys
        sys.exit(main(sys.argv))

In this case, stoepsel will look for folder named 'plugins' and read any .py-
file into its registry.
One file has to register (see below) the term '__main__' or simply
PluginManager.PGM_MAIN. This is the entry point for our application.

## stoepsel configuration

It's possible to configure stoepsel and stoepsel plugins. Therefore, you can
give a dictionary to PluginManager constructor which at least consists of
'plugin_path', a string which tells a directory where stoepsel looks for
plugins and 'plugin_config' where plugin configuration can be stored.


    config = {}
    config['plugin_path'] = 'simple_plugins'
    config['plugin_config'] = {}

    pm = PluginManager(config)

You could also put this into a json based (or other) config file

    with open('config.json') as fp:
        config = json.load(fp)
        pm = PluginManager(config)

## creating a plugin

a plugin is a class which derives from stoepsel.Plugin. It needs to deploy
static information about it's name, version and dependencies.

    from stoepsel import Plugin, entrymethod

    class MyPlugin(Plugin):
        name = 'simple_plugin'
        version = '0.0.1'
        dependencies = []

        @entrymethod(Plugin.PGM_MAIN)
        def main(self):
            print('Running around...')

It is basically possible to put several plugins into one python script.
Any class which derives from Plugin will be loaded automatically.

you can also declare a method that will always run in an extra thread

    from stoepsel import Plugin, entrymethod, threaded
    import time

    class MyThreadedPlugin(Plugin):
        name = 'threaded_plugin'
        version = '0.0.1'
        dependencies = []

        @entrymethod(Plugin.PGM_MAIN)
        @threaded
        def main(self):
            print('thread started...')
            time.sleep(1)
            print('thread stopped')

### dependencies

a dependency is described by its plugin name and a version expression
with \#\# between:

        dependencies = ['simple_plugin##0.0.1']

A version expression consists of an optional operator and a version number:
 - '>0.1.0' means higher than version 0.1.0. Versions 0.1.1 or 0.2.0 would match
 - '<0.1.0' means lower than version 0.1.0 all versions with 0.0.x would match
 - '==0.1.0' only version 0.1.0 matches (same as 0.1.0)
 - '>=0.1.0' means higher or equal
 - '<=0.1.0' means lower or equal
 - '!=0.1.0' all versions match, except 0.1.0

It is possible to combine version expressions by delimiting them with ;
 - '>=1.0;<2.0' all versions between 1.0 and lower than 2.0 match
 - '>1.0;!=1.0.3' all versions higher than 1.0 but not 1.0.3 (maybe its broken?)

If a dependency version does not match, stoepsel throws an exception.

## registering objects

you can register objects by utilizing the Plugin method 'register'

    def setup(self):
        self.register('myapp/plugins/plg1/sayhi', self.sayhi)

    def sayhi(self):
        print('hello world')

another way is to use the entrymethod decorator.
Attention: Since this is applied in the predefined Plugin_setup(), mixing this
and self.register() does not work unless you add a super().setup().

    @entrymethod
    def sayhi(self):
        print('hello world')

## using registered objects

to use registered objects you fave to find them via get_item method

    def setup(self):
        sayhi = self.get_item('myapp/plugins/plg1/sayhi')
        if sayhi is not None:
            sayhi()

## configuration

The configuration of the PluginManager is also set into the model tree
so you can get it by utilizing get_item

    self.get_item('config:plugin_config/myplugin')

this can be useful to create configuration dialogues. To make it easier
there is a property config set:

    print(self.config['plugin_config/mypath'])

Also a list of plugins can be read by using 'plugins:' as path or just

   print(self.plugins)

# Setting for commandline arguments
To set commandline arguments, you have to override the "get_parser_arguments" method.
If you need one or more arguments your dictionary for one argument have to look's like this:

    arg_parser = {
        'short_key': 'e',
        'long_key': 'example',
        'type': "str", # str, int, bool, float
        'required': "True", # True, False
        'action': "None", # "None" if not needed, a given action like argparse
        'default': "None", # "None" if not needed, a default value like a url
        'help': 'Example for the plugin argument parser'
    }

After creating the argument, you have to put it into a list:

    parser_list = [arg_parser]

The return value is a tupel

    return (self.name, parser_list)

The complete example:

    def get_parser_arguments(self) -> tuple:

        arg_parser = {
            'short_key': 'e',
            'long_key': 'example',
            'type': "str", # str, int, bool, float
            'required': "True", # True, False
            'action': "None", # "None" if not needed, a given action like argparse
            'default': "None", # "None" if not needed, a default value like a url
            'help': 'Example for the plugin argument parser'
        }

        parser_list = [arg_parser]

        return (self.name, parser_list)

# TODOs

- find plugins recursively in plugin dir
