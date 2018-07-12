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

from cablegram.wrapper.universe import Universe

class ChatView(Gtk.TextView):

    __gtype_name__ = 'ChatView'

    longest_name = -1

    name_tag = None
    msg_tag = None

    messages_list = None
    current_id = None
    prev_line_user = -1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.setup_tags()
        self.set_pixels_above_lines(5)

    def do_get_preferred_width(self):
        return 1

    def setup_tags(self):

        self.name_tag = self.get_buffer().create_tag("name", weight=Pango.Weight.BOLD, foreground="#324664", left_margin=20)
        self.msg_tag = self.get_buffer().create_tag("msg")

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

    def draw_message(self, sender, msg):

        if not self.prev_line_user == sender or self.prev_line_user == -1:
            self.get_buffer().insert_with_tags(self.get_buffer().get_end_iter(), sender, self.name_tag)
            self.get_buffer().insert(self.get_buffer().get_end_iter(), "\t")

            self.prev_line_user = sender
        else:
            self.get_buffer().insert_with_tags(self.get_buffer().get_end_iter(), " ", self.name_tag)
            self.get_buffer().insert(self.get_buffer().get_end_iter(), "\t")

        self.get_buffer().insert_with_tags(self.get_buffer().get_end_iter(), msg.replace("\n", " "), self.msg_tag)
        self.get_buffer().insert(self.get_buffer().get_end_iter(), "\n")

        return 0

    def draw_messages(self, revealer=None):

        if not self.messages_list:
            return

        self.setup_indent()
        self.clear()

        for item in self.messages_list:

            sender = item["sender"]
            msg = ""

            if item["msg"]["text"]:
                msg = item["msg"]["text"]
                self.draw_message(sender, msg)

            else:
                #image...
                #print(type(item["msg"]))
                print(Universe.instance().download_file(item["msg"]))

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

        Gdk.threads_add_idle(100, self.draw_message, sender, msg)

    def add_message(self, sender, msg):

        try:
            self.messages_list.append({"sender":sender, "msg":msg})

            if len(sender) > self.longest_name:
                self.longest_name = len(sender)
        except TypeError as e:
            if len(sender["first_name"]) > self.longest_name:
                self.longest_name = len(sender["first_name"])
