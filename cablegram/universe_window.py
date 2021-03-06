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
from .chat_view import ChatView

from cablegram.wrapper.universe import Universe

@GtkTemplate(ui='/org/gnome/Cablegram/ui/universe.ui')
class UniverseWindow(Gtk.ApplicationWindow):

    __gtype_name__ = 'UniverseWindow'

    sidebar_list = GtkTemplate.Child()
    chat_wrapper = GtkTemplate.Child()
    chat_revealer = GtkTemplate.Child()
    msg_entry = GtkTemplate.Child()
    chat_view = None

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

    def scroll_to_end(self, a=None, b=None):
        adj = self.chat_wrapper.get_vadjustment()
        adj.set_value(adj.get_upper())

    def start_main(self):

        #
        # Sidebar
        #

        def chat_loaded():

            while Gtk.events_pending():
                Gtk.main_iteration_do(False)

            self.chat_revealer.set_reveal_child(False)

            Gdk.threads_add_idle(1000, self.scroll_to_end)

        def sidebar_clicked(a, row):

            while Gtk.events_pending():
                Gtk.main_iteration_do(False)

            self.chat_revealer.set_reveal_child(True)

            dialog_item = self.contacts[row.get_index()]
            history = None

            if dialog_item.dialog_type == "user":
                self.chat_view.load_chat(dialog_item.user["id"], chat_loaded)
            elif dialog_item.dialog_type == "chat":
                self.chat_view.load_chat(dialog_item.chat["id"], chat_loaded)
            # TODO: Add channel support
            #else:
                #history = Universe.instance().get_history(dialog_item.channel["id"])

            self.chat_view.setup_indent()

        self.sidebar_list.connect('row-activated', sidebar_clicked)

        self.setup_sidebar()

        #
        # Chat View
        #

        self.chat_wrapper.hscrollbar_policy = Gtk.PolicyType.NEVER

        dbg = False

        self.chat_view = ChatView(wrap_mode=Gtk.WrapMode.WORD_CHAR,
                editable=dbg,
                cursor_visible=dbg)
        self.chat_wrapper.add(self.chat_view)
        self.chat_wrapper.show_all()

        self.chat_view.setup_indent()

        Universe.instance().incoming_callbacks.append(self.incoming_message)
        Universe.instance().incoming_callbacks.append(self.update_sidebar)

        #
        # Other
        #

        self.msg_entry.connect("activate", self.send_message)

    def update_sidebar(self, msg):

        item = None
        item_id = msg["chat"]["id"]

        if item_id < 0:
            item_id *= -1

        for sidebar_item in self.sidebar_list.get_children():
            if item_id == sidebar_item.element_id:
                item = sidebar_item
                if hasattr(msg, "text"):
                    if msg["from_user"]["id"] == Universe.instance().me["id"]:
                        item.chat_label.set_text("You: "+msg["text"])
                    else:
                        item.chat_label.set_text(msg["text"])

        if item:
            self.sidebar_list.remove(item)
            self.sidebar_list.insert(item, 0)

    def setup_sidebar(self):

        self.contacts = Universe.instance().get_dialogs()

        for child in self.sidebar_list.get_children():
            self.sidebar_list.remove(child)

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
                    sidebarItem.element_id = dialog.dialog["peer"]["user_id"]

                elif dialog.dialog_type == "chat":
                    sidebarItem.contact_label.set_text(dialog.chat["title"])
                    sidebarItem.chat_name = dialog.chat["title"]
                    sidebarItem.element_id = dialog.dialog["peer"]["chat_id"]

                elif dialog.dialog_type == "channel":
                    sidebarItem.contact_label.set_text(dialog.from_user)
                    sidebarItem.channel_name = dialog.from_user
                    sidebarItem.element_id = dialog.dialog["peer"]["channel_id"]

                try:

                    message = dialog.message["message"]
                    if not message:
                        if dialog.message["media"]:
                            if isinstance(dialog.message["media"], pyrogram.api.types.MessageMediaPhoto):
                                message = "Photo"

                            elif isinstance(dialog.message["media"], pyrogram.api.types.MessageMediaGeo) or isinstance(dialog.message["media"], pyrogram.api.types.MessageMediaGeoLive):
                                message = "Location"

                            elif isinstance(dialog.message["media"], pyrogram.api.types.MessageMediaContact):
                                message = "Contact"

                            elif isinstance(dialog.message["media"], pyrogram.api.types.MessageMediaDocument):
                                message = "File"

                            elif isinstance(dialog.message["media"], pyrogram.api.types.MessageMediaGame):
                                message = "Game"

                            elif isinstance(dialog.message["media"], pyrogram.api.types.MessageMediaInvoice):
                                message = "Invoice"

                            elif isinstance(dialog.message["media"], pyrogram.api.types.MessageMediaVenue):
                                message = "Venue"

                            elif isinstance(dialog.message["media"], pyrogram.api.types.MessageMediaWebPage):
                                message = "Web Page"

                    if dialog.dialog_type == "user" and dialog.from_user == "you":
                        if dialog.from_user == "you":
                            sidebarItem.chat_label.set_text("You: "+message.replace("\n", " "))
                    elif dialog.dialog_type == "chat":
                        if dialog.from_user["id"] == Universe.instance().me["id"]:
                            sidebarItem.chat_label.set_text("You: "+message.replace("\n", " "))
                        else:
                            sidebarItem.chat_label.set_text(dialog.from_user["first_name"]+": "+message.replace("\n", " "))
                    else:
                        sidebarItem.chat_label.set_text(message.replace("\n", " "))
                except AttributeError as e:
                    print("Unexpected message")
                    print("Error:")
                    print(e)
                    print("Item")
                    print(dialog.message)

                self.sidebar_list.insert(sidebarItem, -1)

    def incoming_message(self, msg):

        if not msg:
            return

        chat_id = msg["chat"]["id"]

        if not abs(chat_id) == abs(self.chat_view.current_id):
            return

        self.chat_view.draw_message(msg)
        Gdk.threads_add_idle(1000, self.scroll_to_end)

    def send_message(self, sender):
        sent_msg = Universe.instance().send_message(self.msg_entry.get_text(), self.chat_view.current_id)

        if sent_msg:
            self.chat_view.draw_message(sent_msg)
            self.update_sidebar(sent_msg)
            self.msg_entry.set_text("")

        Gdk.threads_add_idle(1000, self.scroll_to_end)