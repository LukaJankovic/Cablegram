# window.py
#
# Copyright 2018 LukaJankovic
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from gi.repository import Gtk
from .gi_composites import GtkTemplate

from pathlib import Path
from time import sleep

import webbrowser
import configparser
import threading
import functools

from .universe import Universe

@GtkTemplate(ui='/org/gnome/Cablegram/login.ui')
class LoginWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'LoginWindow'

    loading_spinner = GtkTemplate.Child()
    api_id = GtkTemplate.Child()
    api_hash = GtkTemplate.Child()
    phone_nr = GtkTemplate.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.init_template()

        config = configparser.ConfigParser()
        config.read(str(Path.home())+"/.config/cablegram.ini")

        try:
            if config.get("pyrogram", "api_id"):
                self.api_id.set_text(config.get("pyrogram", "api_id"))
        except configparser.NoSectionError:
            print("api_id empty")
        try:
            if config.get("pyrogram", "api_hash"):
                self.api_hash.set_text(config.get("pyrogram", "api_hash"))
        except configparser.NoSectionError:
            print("api_hash empty")

    @GtkTemplate.Callback
    def api_clicked(self, widget, user_data):
        webbrowser.open("https://my.telegram.org/apps")

    @GtkTemplate.Callback
    def continue_clicked(self, widget, user_data):

        if self.api_id.get_text() and self.api_hash.get_text() and self.phone_nr.get_text():

            self.loading_spinner.start()

            config = configparser.ConfigParser()

            config.add_section("pyrogram")
            config.set("pyrogram", "api_id", self.api_id.get_text())
            config.set("pyrogram", "api_hash", self.api_hash.get_text())
            config.set("pyrogram", "phone_nr", self.phone_nr.get_text())

            ini_file = open(str(Path.home())+"/.config/cablegram.ini", "w+")

            config.write(ini_file)
            ini_file.close()

            window = Gtk.Window()
            window.set_title("Confirmation Code")
            window.set_default_size(300, 0)
            window.set_modal(True)
            window.set_transient_for(self)
            window.set_resizable(False)
            window.connect('destroy', self.destroy)

            code_entry = Gtk.Entry()
            code_entry.set_hexpand(True)

            def confirm_callback(event):
                event.set()

            event = threading.Event()

            confirm_button = Gtk.Button.new_with_label("Confirm")
            confirm_button.set_hexpand(True)
            confirm_button.set_halign(Gtk.Align.END)
            confirm_button.connect("clicked", confirm_callback, event)

            grid = Gtk.Grid()
            grid.set_margin_left(12)
            grid.set_margin_right(12)
            grid.set_margin_top(12)
            grid.set_margin_bottom(12)
            grid.set_row_spacing(12)
            grid.set_hexpand(True)

            grid.attach(code_entry, 0, 0, 1, 1)
            grid.attach(confirm_button, 0, 1, 1, 1)

            window.add(grid)
            window.show_all()

            def code_callback():
                event.wait()
                print(code_entry.get_text())

            code_callback()
            #Universe.instance().login(self.api_id.get_text(), self.api_hash.get_text(), self.phone_nr.get_text(), code_callback)

        else:
            print("empty fields!")
                