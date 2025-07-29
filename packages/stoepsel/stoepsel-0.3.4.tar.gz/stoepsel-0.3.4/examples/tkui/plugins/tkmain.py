from stoepsel import Plugin
import tkinter as tk

class TkMain(Plugin):
    name = 'tkmain'
    version = '0.0.1'
    dependencies = []

    def setup(self):
        # todo setup
        self.register('__main__', self.main)

    def create_menu(self, root, items):
        for name, value in items.items():
            if isinstance (value, dict):
                self.logger.debug(f'Creating menu {name}')
                submenu = tk.Menu(root)
                root.add_cascade(label=name, menu=submenu)
                self.create_menu(submenu, value)
            else:
                self.logger.debug(f'Creating action {name}')
                root.add_command(label=name, command=value)

    def init_menu(self):
        menu_items = self.get_item('menu')
        self.logger.debug(f'got menu items {menu_items}')

        menu = tk.Menu(self.tk)
        self.tk.config(menu=menu)
        self.create_menu(menu, menu_items)


    def main(self, **kwargs):
        self.tk = tk.Tk()
        self.mainview = tk.Frame(self.tk)
        self.init_menu()

        self.logger.debug('running')
        self.tk.mainloop()

    def button_hit(self, **kwargs):
        self


export = TkMain
