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
from cablegram.wrapper.universe import Universe

class Application(Gtk.Application):

    def __init__(self):
        super().__init__(application_id='org.gnome.Cablegram',
                         flags=Gio.ApplicationFlags.FLAGS_NONE)

    def do_activate(self):

        #Show main window
        universe_window = UniverseWindow(application=self)
        universe_window.present()

        #Show login dialog if necessary
        if not Universe.instance().is_loggedin():
            loginWin = LoginWindow(application=self, use_header_bar=True)
            loginWin.set_modal(True)
            loginWin.set_transient_for(universe_window)
            loginWin.present()

        #Otherwise load settings and login
        else:
            config = configparser.ConfigParser()
            config.read(str(Path.home())+"/.config/cablegram.ini")

            error = Universe.instance().login(config.get("pyrogram", "api_id"), config.get("pyrogram", "api_hash"), config.get("pyrogram", "phone_number"), None)

            if not error:
                universe_window.present()
                universe_window.start_main()
            else:
                def exit_dialog(widget, info):
                    widget.destroy()
                    os._exit(0)

                dialog_message = None

                if type(error) is pyrogram.api.errors.exceptions.bad_request_400.PhoneNumberInvalid:
                    dialog_message = "Invalid phone number. Please try again."

                elif type(error) is pyrogram.api.errors.exceptions.flood_420.FloodWait:
                    dialog_message = "You're trying to log in too often. Try again in "+ str(error.x) +" seconds."

                elif type(error) is pyrogram.api.errors.exceptions.bad_request_400.ApiIdInvalid:
                    dialog_message = "Invalid API ID and / or API Hash."

                elif type(error) is pyrogram.api.errors.exceptions.bad_request_400.PhoneCodeInvalid:
                    dialog_message = "Invalid confirmation code."

                def show_error():
                    error_dialog = Gtk.MessageDialog(parent         = universe_window,
                                                     flags          = Gtk.DialogFlags.MODAL,
                                                     type           = Gtk.MessageType.ERROR,
                                                     buttons        = Gtk.ButtonsType.CLOSE,
                                                     message_format = dialog_message)
                    error_dialog.connect("response", exit_dialog)
                    error_dialog.show()

def clear_cache(a=None):

    #Clear cache folder
    cache_folder = str(Path.home()) + "/.var/app/org.gnome.Cablegram/cache/tmp/"

    for item in os.listdir(cache_folder):
        item_path = os.path.join(cache_folder, item)
        try:
            os.unlink(item_path)
        except Exception:
            pass

def main(version):
    app = Application()
    app.connect('shutdown', clear_cache)
    return app.run(sys.argv)