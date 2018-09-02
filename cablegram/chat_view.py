# chat_view.py
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

from gi.repository import Gtk, Gdk, GdkPixbuf, GLib, GObject, Pango
import math, threading, re

from cablegram.wrapper.universe import Universe

class ChatView(Gtk.TextView):

    __gtype_name__ = 'ChatView'

    longest_name = -1

    name_tag = None
    msg_tag = None
    url_tag = None

    messages_list = None
    current_id = None
    prev_line_user = None

    images = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.setup_tags()
        self.set_pixels_above_lines(5)

    def do_get_preferred_width(self):
        return 1

    def setup_tags(self):

        #324664
        self.name_tag = self.get_buffer().create_tag("name", weight=Pango.Weight.BOLD, left_margin=20)
        self.msg_tag = self.get_buffer().create_tag("msg")
        self.url_tag = self.get_buffer().create_tag("url", style=Pango.Style.ITALIC, foreground="#324664", underline=Pango.Underline.SINGLE)

        # TODO: make urls clickable (needs buttontag class)

    def setup_indent(self):

        self.tabs = None
        ctx = self.get_pango_context()
        metrics = ctx.get_metrics(None, None)
        char_width = max(metrics.get_approximate_char_width(), metrics.get_approximate_digit_width())
        pixel_width = Pango.units_to_double(char_width)

        indent = self.longest_name * pixel_width + 20

        tabs_array = Pango.TabArray(1, True)
        tabs_array.set_tab(0, Pango.TabAlign.LEFT, indent)

        self.set_tabs(tabs_array)
        self.set_left_margin(indent)
        self.set_indent(-indent)

    def clear(self):
        self.get_buffer().set_text("")
        self.longest_name = -1
        self.images = []

    def draw_image_marker(self, position, name):
        anchor = self.get_buffer().create_child_anchor(position)
        self.get_buffer().insert(self.get_buffer().get_end_iter(), "\n")

        spinner = Gtk.Spinner()
        self.add_child_at_anchor(spinner, anchor)

        spinner.show_all()
        spinner.start()

        self.images.append({"anchor":anchor, "id":name, "spinner":spinner})

    def draw_image(self, img_path, msg):

        if not abs(msg["chat"]["id"]) == abs(self.current_id):
            print("Invalid ID:")
            print(abs(msg["chat"]["id"]))
            print(abs(self.current_id))
            return

        if not img_path:
            print("Empty path")
            return

        anchor = None
        for i in self.images :
            if i["id"] == msg["message_id"]:
                anchor = i["anchor"]
                i["spinner"].destroy()

        if anchor == None:
            print("anchor none")
            return

        img = Gtk.Image()
        pix = None
        try:
            pix = GdkPixbuf.Pixbuf.new_from_file_at_scale(img_path, 300, 300, True)
        except GLib.GError as e:
            print("img error")
            print(e.message)

            itr = self.get_buffer().get_iter_at_child_anchor(anchor)
            self.get_buffer().insert_with_tags(itr, e.message, self.msg_tag)

        if pix:
            img.set_from_pixbuf(pix)

            self.add_child_at_anchor(img, anchor)
            img.show_all()

    def draw_message(self, message):

        # TODO: get_sender separate function (username, bot, etc.)
        sender = message["from_user"]["first_name"]

        if message["text"]:
            # Normal message, display it
            text = message["text"]

            if self.prev_line_user == sender:
                self.get_buffer().insert_with_tags(self.get_buffer().get_end_iter(), " ", self.name_tag)
            else:
                self.get_buffer().insert_with_tags(self.get_buffer().get_end_iter(), sender, self.name_tag)
                self.prev_line_user = sender

            self.get_buffer().insert(self.get_buffer().get_end_iter(), "\t")

            # TODO: Implement newlines better
            self.get_buffer().insert_with_tags(self.get_buffer().get_end_iter(), text.replace("\n", " "), self.msg_tag)
            self.get_buffer().insert(self.get_buffer().get_end_iter(), "\n")

        elif hasattr(message, 'photo'):
            # Message is a photo
            # Display loading indicator until image is downloaded

            self.get_buffer().insert(self.get_buffer().get_end_iter(), "\n")
            self.get_buffer().insert_with_tags(self.get_buffer().get_end_iter(), sender, self.name_tag)
            self.get_buffer().insert(self.get_buffer().get_end_iter(), "\t")

            self.prev_line_user = sender

            self.draw_image_marker(self.get_buffer().get_end_iter(), message["message_id"])

            dl_thread = threading.Thread(target=Universe.instance().download_file, args=(message, self.draw_image, ))
            dl_thread.daemon = True
            dl_thread.start()

        else:
            print("Other type of message")
            print(message)

    def load_chat(self, chat_id, revealer=None):

        self.clear()

        self.messages_list = Universe.instance().get_history(chat_id)
        self.current_id = chat_id

        for message in self.messages_list:

            if len(message["from_user"]["first_name"]) > self.longest_name:
                self.longest_name = len(message["from_user"]["first_name"])

            self.setup_indent()
            self.draw_message(message)

        # Hide loading indicator
        if revealer:
            while Gtk.events_pending():
                Gtk.main_iteration_do(False)

            revealer.set_reveal_child(False)

    def append_message(self, item, msg_id):

        if msg_id < 0:
            msg_id *= -1

        if not item:
            return

        if not msg_id == self.current_id:
            return

        sender = item["sender"]["first_name"]
        msg = item["msg"]

        self.add_message(item["sender"], item["msg"])
        self.draw_message(sender, msg)

    def add_message(self, sender, msg):

        try:
            self.messages_list.append({"sender":sender, "msg":msg})

            if len(sender) > self.longest_name:
                self.longest_name = len(sender)
        except TypeError as e:
            if len(sender["first_name"]) > self.longest_name:
                self.longest_name = len(sender["first_name"])
