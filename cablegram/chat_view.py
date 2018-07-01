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

from gi.repository import Gtk, Gdk, GLib, GObject, Pango
import math

class ChatView(Gtk.TextView):

    __gtype_name__ = 'ChatView'

    longest_name = -1

    name_tag = None
    msg_tag = None

    messages_list = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.init_template()

        self.setup_tags()

        self.set_vexpand(True)
        self.set_wrap_mode(Gtk.WrapMode.WORD)

    def do_get_preferred_width(self):
        return 1

    def setup_tags(self):

        #self.name_tag = self.ctx.create_tag("name", weight=Pango.Weight.BOLD, left_margin=5, left_margin_set=True)
        #self.name_tag = self.get_buffer().create_tag("name", weight=Pango.Weight.BOLD)
        #self.msg_tag = self.get_buffer().create_tag("msg")
        #self.msg_tag.indent = 20
        #self.msg_tag.indent_set = True

        tag_table = self.get_buffer().get_tag_table()

        tags = [
            {
                "name": "name",
                "weight": Pango.Weight.BOLD
            },
            {
                "name": "msg",
                "indent": 20
            }
        ]

        for tag in tags:
            tag_table.add(Gtk.TextTag(tag))

    def setup_indent(self):

        self.tabs = None
        ctx = self.get_pango_context()
        metrics = ctx.get_metrics(None, None)
        char_width = max(metrics.get_approximate_char_width(), metrics.get_approximate_digit_width())
        pixel_width = Pango.units_to_double(char_width)

        tabs_array = Pango.TabArray(1, True)
        tabs_array.set_tab(0, Pango.TabAlign.LEFT, 100)

        self.set_tabs(tabs_array)

    def clear(self):
        self.get_buffer().set_text("")

    def draw_messages(self):

        if not self.messages_list:
            return

        self.setup_indent()
        self.clear()

        ctx = self.get_pango_context()
        metrics = ctx.get_metrics(None, None)
        char_width = max(metrics.get_approximate_char_width(), metrics.get_approximate_digit_width())
        pixel_width = Pango.units_to_double(char_width)

        tv_w = self.get_allocated_width()
        cpl = int(tv_w / pixel_width)

        for item in self.messages_list:

            sender = item["sender"]
            msg = item["msg"]

            if not item["msg"]:
                #Other type of msg (i.e. image)
                msg = ""

            self.get_buffer().insert_with_tags(self.get_buffer().get_end_iter(), sender+"\t", self.name_tag)
            self.get_buffer().insert_with_tags(self.get_buffer().get_end_iter(), msg, self.msg_tag)

            self.get_buffer().insert(self.get_buffer().get_end_iter(), "\n")

    def add_message(self, sender, msg):

        self.messages_list.append({"sender":sender, "msg":msg})

        try:
            if len(sender) > self.longest_name:
                self.longest_name = len(sender)
        except TypeError as e:
            print("error inserting message: ")
            print(e)
