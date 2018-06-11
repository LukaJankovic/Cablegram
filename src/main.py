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
import os
import os.path
import configparser

import pyrogram

from pathlib import Path

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Gio

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
        universe_window = UniverseWindow(application=self)
        universe_window.connect('show', self.hide_login)

        if not Universe.instance().is_loggedin():
            loginWin = LoginWindow(application=self)
            loginWin.set_type_hint(Gdk.WindowTypeHint.DIALOG)
            loginWin.set_modal(True)
            loginWin.set_transient_for(universe_window)
            loginWin.present()

        universe_window.present()

    def do_activate(self):

        debug = False

        if debug:
            self.start_universe()
            loggedin = True

        #if os.path.isfile(str(Path.home()) + "/cablegram.session") and os.path.isfile(str(Path.home())+"/.config/cablegram.ini"):
        #    loggedin = True

        self.start_universe()

#        if loggedin == False:
#            self.loginWin = LoginWindow(application=self)
#            self.loginWin.completion_callback = self.start_universe
#            self.loginWin.present()
#
#        elif debug == False:
#            config = configparser.ConfigParser()
#            config.read(str(Path.home())+"/.config/cablegram.ini")
#
#            error = Universe.instance().login(config.get("pyrogram", "api_id"), config.get("pyrogram", "api_hash"), config.get("pyrogram", "phone_number"), None)
#
#            if not error:
#                self.start_universe()
#            else:
#                def exit_dialog(widget, info):
#                    widget.destroy()
#                    os._exit(0)
#
#                dialog_message = None
#
#                if type(error) is pyrogram.api.errors.exceptions.bad_request_400.PhoneNumberInvalid:
#                    dialog_message = "Invalid phone number. Please try again."
#
#                elif type(error) is pyrogram.api.errors.exceptions.flood_420.FloodWait:
#                    dialog_message = "You're trying to log in too often. Try again in "+ str(error.x) +" seconds."
#
#                elif type(error) is pyrogram.api.errors.exceptions.bad_request_400.ApiIdInvalid:
#                    dialog_message = "Invalid API ID and / or API Hash."
#
#                elif type(error) is pyrogram.api.errors.exceptions.bad_request_400.PhoneCodeInvalid:
#                    dialog_message = "Invalid confirmation code."
#
#                def show_error():
#                    error_dialog = Gtk.MessageDialog(parent         = self,
#                                                     flags          = Gtk.DialogFlags.MODAL,
#                                                     type           = Gtk.MessageType.ERROR,
#                                                     buttons        = Gtk.ButtonsType.CLOSE,
#                                                     message_format = dialog_message)
#                    error_dialog.connect("response", exit_dialog)
#                    error_dialog.show()

def main(version):
    app = Application()
    return app.run(sys.argv)
