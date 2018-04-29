# login.py
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


from gi.repository import Gtk, Gdk, GObject
from .gi_composites import GtkTemplate

from .universe import Universe

from pathlib import Path

import webbrowser
import configparser
import threading

@GtkTemplate(ui='/org/gnome/Cablegram/login.ui')
class LoginWindow(Gtk.Assistant):

    __gtype_name__ = 'LoginWindow'

    api_page = GtkTemplate.Child()
    phone_page = GtkTemplate.Child()
    code_page = GtkTemplate.Child()
    api_id = GtkTemplate.Child()
    api_hash = GtkTemplate.Child()
    phone_entry = GtkTemplate.Child()
    code_entry = GtkTemplate.Child()
    get_api_keys = GtkTemplate.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.init_template()

        #Apply CSS
        style_provider = Gtk.CssProvider()
        style_provider.load_from_resource("/org/gnome/Cablegram/login.css")

        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        #Connections
        def api_changed(bump):
            if self.api_id.get_text() and self.api_hash.get_text():
                self.set_page_complete(self.api_page, True)

        def phone_changed(bump):
            if self.phone_entry.get_text():
                self.set_page_complete(self.phone_page, True)

        def code_changed(bump):
            if self.code_entry.get_text():
                self.set_page_complete(self.code_page, True)

        def open_url(bump):
            webbrowser.open("https://my.telegram.org/apps")

        event = threading.Event()

        def code_callback():

            def wait_for_code():
                event.wait()
                return self.code_entry.get_text()

            print("starting auth")
            Universe.instance().login(self.api_id.get_text(), self.api_hash.get_text(), self.phone_entry.get_text(), code_callback)
            #print("code "+wait_for_code())

        def assistant_prepare(info1, info2):
            if info2 == self.code_page:
                t = threading.Thread(target=code_callback)
                t.start()

        def assistant_apply(info):
            event.set()

        self.connect("cancel", exit)
        self.connect("prepare", assistant_prepare)
        self.connect("apply", assistant_apply)
        self.api_id.connect("changed", api_changed)
        self.api_hash.connect("changed", api_changed)
        self.phone_entry.connect("changed", phone_changed)
        self.code_entry.connect("changed", code_changed)
        self.get_api_keys.connect("clicked", open_url)

        #Apply ini
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