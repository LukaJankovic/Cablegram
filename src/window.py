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

from gi.repository import Gtk, GObject
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