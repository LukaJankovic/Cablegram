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

from .login import LoginWindow
from .sidebar import SidebarChatItem
from .chat_view import *

from cablegram.wrapper.universe import Universe

@GtkTemplate(ui='/org/gnome/Cablegram/ui/universe.ui')
class UniverseWindow(Gtk.ApplicationWindow):

    __gtype_name__ = 'UniverseWindow'

    sidebar_list = GtkTemplate.Child()
    chat_view = GtkTemplate.Child()

    cvm = None
    contacts = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.init_template()

        #Apply CSS
        style_provider = Gtk.CssProvider()
        style_provider.load_from_resource("/org/gnome/Cablegram/style/universe.css")

        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def start_main(self):

        #
        # Sidebar
        #

        def sidebar_clicked(a, row):

            self.cvm.clear()

            dialog_item = self.contacts[row.get_index()]
            history = None

            if dialog_item.dialog_type == "user":
                history = Universe.instance().get_history(dialog_item.user["id"])
            elif dialog_item.dialog_type == "chat":
                history = Universe.instance().get_history(dialog_item.chat["id"])
            # TODO: Add channel support
            #else:
                #history = Universe.instance().get_history(dialog_item.channel["id"])
            #print(history)

            self.cvm.messages_list = []

            for msg in history["messages"]:
                if hasattr(msg, 'text'):
                    self.cvm.add_message(msg["from_user"]["first_name"], msg["text"])

            self.cvm.setup_indent(self.chat_view)
            self.cvm.draw_messages(self.chat_view)

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

                if dialog.dialog_type == "user":

                    first = dialog.user["first_name"]
                    last = dialog.user["last_name"]

                    if not dialog.user["first_name"]:
                        first = ""

                    if not dialog.user["last_name"]:
                        last = ""

                    sidebarItem.contact_label.set_text(first+" "+last)

                    sidebarItem.first_name = dialog.user["first_name"]
                    sidebarItem.last_name = dialog.user["last_name"]

                elif dialog.dialog_type == "chat":
                    sidebarItem.contact_label.set_text(dialog.chat["title"])
                    sidebarItem.chat_name = dialog.chat["title"]

                elif dialog.dialog_type == "channel":
                    sidebarItem.contact_label.set_text(dialog.from_user)
                    sidebarItem.channel_name = dialog.from_user

                try:
                    if dialog.dialog_type == "user" and dialog.from_user == "you":
                        if dialog.from_user == "you":
                            sidebarItem.chat_label.set_text("You: "+dialog.message["message"])
                    elif dialog.dialog_type == "chat":
                        if dialog.from_user["id"] == Universe.instance().me["id"]:
                            sidebarItem.chat_label.set_text("You: "+dialog.message["message"])
                        else:
                            sidebarItem.chat_label.set_text(dialog.from_user["first_name"]+": "+dialog.message["message"])
                    else:
                        sidebarItem.chat_label.set_text(dialog.message["message"])
                except AttributeError as e:
                    print("Unexpected message")
                    print("Error:")
                    print(e)
                    print("Item")
                    print(dialog.message)

                self.sidebar_list.insert(sidebarItem, -1)

        #
        # Chat View
        #

        self.cvm = chat_view_manager(self.chat_view.get_buffer())
        self.cvm.setup_indent(self.chat_view)