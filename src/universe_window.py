# universe_window.py
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

import json
import os

import pyrogram

from gi.repository import Gtk, Gdk, GLib, GObject
from .gi_composites import GtkTemplate

from .sidebar import SidebarChatItem
from .universe import Universe
from .chat_view import *

@GtkTemplate(ui='/org/gnome/Cablegram/universe.ui')
class UniverseWindow(Gtk.ApplicationWindow):

    __gtype_name__ = 'UniverseWindow'

    sidebar_list = GtkTemplate.Child()
    chat_view = GtkTemplate.Child()
    chat_view_buffer = GtkTemplate.Child()

    cvm = None
    contacts = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.init_template()

        #Apply CSS
        style_provider = Gtk.CssProvider()
        style_provider.load_from_resource("/org/gnome/Cablegram/universe.css")

        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        #
        # Sidebar
        #

        def sidebar_clicked(a, row):

            self.cvm.clear()

            history = Universe.instance().get_history(self.contacts[row.get_index()]["user"]["id"])
            print(history)

            for msg in history["messages"]:
                if hasattr(msg, 'text'):
                    self.cvm.add_message(msg["from_user"]["first_name"], msg["text"])

            self.cvm.add_message(row.first_name, "A sample message")

        self.sidebar_list.connect('row-activated', sidebar_clicked)

        self.contacts = Universe.instance().get_dialogs()

        #TODO: Push error handling to other file
        #Error handling start

        dialog_message = None

        def show_error():
            error_dialog = Gtk.MessageDialog(parent         = self,
                                             flags          = Gtk.DialogFlags.MODAL,
                                             type           = Gtk.MessageType.ERROR,
                                             buttons        = Gtk.ButtonsType.CLOSE,
                                             message_format = dialog_message)
            error_dialog.connect("response", exit_dialog)
            error_dialog.show()

        def exit_dialog(widget, info):
            widget.destroy()
            os._exit(0)

        if type(self.contacts) is pyrogram.api.errors.exceptions.bad_request_400.PhoneNumberInvalid:
            dialog_message = "Invalid phone number. Please try again."
            show_error()

        elif type(self.contacts) is pyrogram.api.errors.exceptions.flood_420.FloodWait:
            dialog_message = "You're trying to access Telegram too often. Try again in "+ str(self.contacts.x) +" seconds."
            show_error()

        elif type(self.contacts) is pyrogram.api.errors.exceptions.bad_request_400.ApiIdInvalid:
            dialog_message = "Invalid API ID and / or API Hash."
            show_error()

        elif type(self.contacts) is pyrogram.api.errors.exceptions.bad_request_400.PhoneCodeInvalid:
            dialog_message = "Invalid confirmation code."
            show_error()

        #Error handling done
        else:

            for dialog in self.contacts:

                sidebarItem = SidebarChatItem()

                if dialog["type"] == "user":

                    first = dialog["user"]["first_name"]
                    last = dialog["user"]["last_name"]

                    if not dialog["user"]["first_name"]:
                        first = ""

                    if not dialog["user"]["last_name"]:
                        last = ""

                    sidebarItem.contact_label.set_text(first+" "+last)

                    sidebarItem.first_name = dialog["user"]["first_name"]
                    sidebarItem.last_name = dialog["user"]["last_name"]

                elif dialog["type"] == "chat":
                    sidebarItem.contact_label.set_text(dialog["chat"]["title"])
                    sidebarItem.chat_name = dialog["chat"]["title"]

                try:
                    if dialog["from"] == "you":
                        sidebarItem.chat_label.set_text("You: "+dialog["message"]["message"])
                    elif dialog["type"] == "chat":
                        sidebarItem.chat_label.set_text(dialog["chat_from"]["first_name"]+": "+dialog["message"]["message"])
                    else:
                        sidebarItem.chat_label.set_text(dialog["message"]["message"])
                except AttributeError as e:
                    print("Unexpected message")
                    print("Error:")
                    print(e)
                    print("Item")
                    print(dialog["message"])

                self.sidebar_list.insert(sidebarItem, -1)

        #
        # Chat View
        #

        self.cvm = chat_view_manager(self.chat_view.get_buffer())
        self.cvm.setup_indent(self.chat_view)