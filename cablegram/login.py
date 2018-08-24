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

from cablegram.wrapper.universe import Universe

from pathlib import Path

import webbrowser
import configparser
import threading
import os
import re

import pyrogram

@GtkTemplate(ui='/org/gnome/Cablegram/ui/login.ui')
class LoginWindow(Gtk.Dialog):

    __gtype_name__ = 'LoginWindow'

    #api_page = GtkTemplate.Child()
    #phone_page = GtkTemplate.Child()
    #code_page = GtkTemplate.Child()
    api_id = GtkTemplate.Child()
    api_hash = GtkTemplate.Child()
    phone_entry = GtkTemplate.Child()
    code_entry = GtkTemplate.Child()
    get_api_keys = GtkTemplate.Child()

    completion_callback = None

    back_button = GtkTemplate.Child()
    next_button = GtkTemplate.Child()
    login_stack = GtkTemplate.Child()

    intro_page = GtkTemplate.Child()
    api_page = GtkTemplate.Child()
    phone_page = GtkTemplate.Child()
    code_page = GtkTemplate.Child()

    event = None
    done = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.init_template()

        #Apply CSS
        style_provider = Gtk.CssProvider()
        style_provider.load_from_resource("/org/gnome/Cablegram/style/login.css")

        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        self.pages = [self.intro_page, self.api_page, self.phone_page, self.code_page]

        #Close app when ESC key pressed
        def close(self):
            if not self.done:
                os._exit(0)

        self.connect("close", close)

        #Buttons / Connections
        def back_clicked(self, root):

            page = root.login_stack.get_visible_child()

            if root.login_stack.get_visible_child_name() == "intro":
                os._exit(0)

            else:
                root.login_stack.set_visible_child(root.pages[root.pages.index(page)-1])
                root.prepare_page(root.login_stack.get_visible_child_name())

        def next_clicked(self, root):

            page = root.login_stack.get_visible_child()

            # TODO Need to find a way to do page.name...
            page_name = root.login_stack.get_visible_child_name()

            if page_name == "intro":
                root.login_stack.set_visible_child(root.api_page)
                root.prepare_page("api")

            elif page_name == "api":
                root.login_stack.set_visible_child(root.phone_page)
                root.prepare_page("phone")

            elif page_name == "phone":
                root.login_stack.set_visible_child(root.code_page)
                root.prepare_page("code")

                root.event = threading.Event()
                GObject.threads_init()

                # Login...
                def code_callback():

                    def wait_for_code(self):
                        root.event.wait()
                        return root.code_entry.get_text()

                    error = Universe.instance().login(root.api_id.get_text(), root.api_hash.get_text(), root.phone_entry.get_text(), wait_for_code)
                    if error:

                        def exit_dialog(widget, info, page_index):
                            widget.destroy()
                            #if not page_index == -1:
                                #self.set_current_page(page_index)

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
                            error_dialog = Gtk.MessageDialog(parent         = root,
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
                        config.set("pyrogram", "api_id", root.api_id.get_text())
                        config.set("pyrogram", "api_hash", root.api_hash.get_text())
                        config.set("pyrogram", "phone_number", root.phone_entry.get_text())

                        with open(str(Path.home())+"/.config/cablegram.ini", "w+") as config_file:
                            config.write(config_file)

                        universe_window = root.get_transient_for()
                        universe_window.start_main()

                        root.done = True
                        root.hide()
                        #root.destroy()

                t = threading.Thread(target=code_callback)
                t.start()
            elif page_name == "code":
               root.event.set()

        def open_url(sender):
            webbrowser.open("https://my.telegram.org/apps")

        def api_changed(sender):
            if re.compile('[0-9]+').match(self.api_id.get_text()) and self.api_hash.get_text():
                self.next_button.set_sensitive(True)
            else:
                self.next_button.set_sensitive(False)

        def phone_changed(sender):
            if re.compile('\+[0-9]+').match(self.phone_entry.get_text()):
                self.next_button.set_sensitive(True)
            else:
                self.next_button.set_sensitive(False)

        self.back_button.connect("clicked", back_clicked, self)
        self.next_button.connect("clicked", next_clicked, self)
        self.get_api_keys.connect("clicked", open_url)
        self.api_id.connect("changed", api_changed)
        self.api_hash.connect("changed", api_changed)
        self.phone_entry.connect("changed", phone_changed)

        self.prepare_page(self.login_stack.get_visible_child_name())

    def prepare_page(self, page):

        #Fix buttons
        if page == "intro":
            self.back_button.set_label("Quit")
            self.back_button.set_label("Next")
            self.next_button.set_sensitive(True)

        elif page == "code":
            self.back_button.set_label("Back")
            self.next_button.set_label("Finish")
            self.next_button.set_sensitive(True)

        else:
            self.back_button.set_label("Back")
            self.back_button.set_label("Next")

        # Other setup
        if page == "api":

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

            if re.compile('[0-9]+').match(self.api_id.get_text()) and self.api_hash.get_text():
                self.next_button.set_sensitive(True)
            else:
                self.next_button.set_sensitive(False)

        elif page == "phone":
            if re.compile('\+[0-9]+').match(self.phone_entry.get_text()):
                self.next_button.set_sensitive(True)
            else:
                self.next_button.set_sensitive(False)