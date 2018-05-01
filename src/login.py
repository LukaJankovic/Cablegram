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


from gi.repository import Gtk, Gdk, GLib, GObject
from .gi_composites import GtkTemplate

from .universe import Universe
from .universe_window import UniverseWindow

from pathlib import Path

import webbrowser
import configparser
import threading
import os
import re

import pyrogram

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
        def exit_app(bump):
            os._exit(0)

        def api_changed(bump):
            if re.compile('[0-9]+').match(self.api_id.get_text()) and self.api_hash.get_text():
                self.set_page_complete(self.api_page, True)
            else:
                self.set_page_complete(self.api_page, False)

        def phone_changed(bump):
            if re.compile('\+[0-9]+').match(self.phone_entry.get_text()):
                self.set_page_complete(self.phone_page, True)
            else:
                self.set_page_complete(self.phone_page, False)

        def code_changed(bump):
            if self.code_entry.get_text():
                self.set_page_complete(self.code_page, True)

        def open_url(bump):
            webbrowser.open("https://my.telegram.org/apps")

        event = threading.Event()
        GObject.threads_init()

        def code_callback():

            def wait_for_code():
                event.wait()
                return self.code_entry.get_text()

            error = Universe.instance().login(self.api_id.get_text(), self.api_hash.get_text(), self.phone_entry.get_text(), wait_for_code)
            if error:

                def exit_dialog(widget, info, page_index):
                    widget.destroy()
                    if not page_index == -1:
                        self.set_current_page(page_index)

                dialog_message = None
                return_to = 1

                if type(error) is pyrogram.api.errors.exceptions.bad_request_400.PhoneNumberInvalid:
                    dialog_message = "Invalid phone number. Please try again."

                elif type(error) is pyrogram.api.errors.exceptions.flood_420.FloodWait:
                    dialog_message = "You're trying to log in too often. Try again in "+ str(error.x) +" seconds."

                elif type(error) is pyrogram.api.errors.exceptions.bad_request_400.ApiIdInvalid:
                    dialog_message = "Invalid API ID and / or API Hash."

                elif type(error) is pyrogram.api.errors.exceptions.bad_request_400.PhoneCodeInvalid:
                    dialog_message = "Invalid confirmation code."
                    return_to = -1

                def show_error():
                    error_dialog = Gtk.MessageDialog(parent         = self,
                                                     flags          = Gtk.DialogFlags.MODAL,
                                                     type           = Gtk.MessageType.ERROR,
                                                     buttons        = Gtk.ButtonsType.CLOSE,
                                                     message_format = dialog_message)
                    error_dialog.connect("response", exit_dialog, return_to)
                    error_dialog.show()

                GLib.idle_add(show_error)
            else:
                #Apply ini
                config = configparser.ConfigParser()
                config.read(str(Path.home())+"/.config/cablegram.ini")

                if not config.has_section('pyrogram'):
                    config.add_section('pyrogram')
                config.set("pyrogram", "api_id", self.api_id.get_text())
                config.set("pyrogram", "api_hash", self.api_hash.get_text())
                config.set("pyrogram", "phone_number", self.phone_entry.get_text())

                with open(str(Path.home())+"/.config/cablegram.ini", "w+") as config_file:
                    config.write(config_file)

                universe_window = UniverseWindow()
                universe_window.present()

                self.destroy()

        def assistant_prepare(info1, info2):
            if info2 == self.code_page:
                t = threading.Thread(target=code_callback)
                t.start()

        def assistant_apply(info):
            event.set()

        self.connect("cancel", exit_app)
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