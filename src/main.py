# main.py
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

import sys
import gi
import os.path
import configparser

from pathlib import Path

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio

from .login import LoginWindow
from .universe_window import UniverseWindow
from .universe import Universe

class Application(Gtk.Application):

    loginWin = None

    def __init__(self):
        super().__init__(application_id='org.gnome.Cablegram',
                         flags=Gio.ApplicationFlags.FLAGS_NONE)

    def hide_login(self, data):
        if self.loginWin:
            self.loginWin.hide()

    def start_universe(self):

        #Show main window
        print("Start main window")
        universe_window = UniverseWindow(application=self)
        universe_window.connect('show', self.hide_login)
        universe_window.present()

    def do_activate(self):

        loggedin = False
        debug = False

        if debug:
            self.start_universe()
            loggedin = True

        if os.path.isfile(str(Path.home()) + "/cablegram.session") and os.path.isfile(str(Path.home())+"/.config/cablegram.ini"):
            loggedin = True

        if loggedin == False:
            self.loginWin = LoginWindow(application=self)
            self.loginWin.completion_callback = self.start_universe
            self.loginWin.present()

        elif debug == False:
            config = configparser.ConfigParser()
            config.read(str(Path.home())+"/.config/cablegram.ini")

            error = Universe.instance().login(config.get("pyrogram", "api_id"), config.get("pyrogram", "api_hash"), config.get("pyrogram", "phone_number"), None)

            if not error:
                self.start_universe()
            else:
                print("==ERROR==")
                print(error)

def main(version):
    app = Application()
    return app.run(sys.argv)
