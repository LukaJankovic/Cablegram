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

class chat_view_manager:

    ctx = None
    longest_name = -1

    name_tag = None
    msg_tag = None

    messages_list = []

    def __init__(self, ctx):
        self.ctx = ctx

        self.setup_tags()

    def setup_tags(self):

        #self.name_tag = self.ctx.create_tag("name", weight=Pango.Weight.BOLD, left_margin=5, left_margin_set=True)
        self.name_tag = self.ctx.create_tag("name", weight=Pango.Weight.BOLD)
        self.msg_tag = self.ctx.create_tag("msg")

    def setup_indent(self, text_view):

        text_view.tabs = None

        #TODO: Make customizable

        ctx = text_view.get_pango_context()
        metrics = ctx.get_metrics(None, None)
        char_width = max(metrics.get_approximate_char_width(), metrics.get_approximate_digit_width())
        pixel_width = Pango.units_to_double(char_width)

        print(self.longest_name)
        print(pixel_width)

        tabs = Pango.TabArray(1, True)
        tabs.set_tab(0, Pango.TabAlign.LEFT, self.longest_name * pixel_width + 3)
        text_view.set_tabs(tabs)

    def clear(self):
        self.ctx.set_text("")

    def draw_messages(self, text_view):

        self.setup_indent(text_view)
        self.clear()

        ctx = text_view.get_pango_context()
        metrics = ctx.get_metrics(None, None)
        char_width = max(metrics.get_approximate_char_width(), metrics.get_approximate_digit_width())
        pixel_width = Pango.units_to_double(char_width)

        tv_w = text_view.get_allocated_width()
        cpl = int(tv_w / pixel_width)

        for item in self.messages_list:

            sender = item["sender"]
            msg = item["msg"]

            if (len(msg)+(self.longest_name+6)) < cpl:
                self.ctx.insert_with_tags(self.ctx.get_end_iter(), sender+"\t   ", self.name_tag)
                self.ctx.insert_with_tags(self.ctx.get_end_iter(), msg, self.msg_tag)

            else:

                lbsn = int(math.ceil(((len(msg)+(self.longest_name+7))/cpl)))
                nmsg = list(msg)

                print("MSG "+msg)
                print(lbsn)
                print(lbsn*int(cpl-(self.longest_name+7)))
                print(str(len(msg)))

                if lbsn*int(cpl-(self.longest_name+7)) <= len(msg):
                    lbsn = lbsn+1

                for i in range(lbsn):

                    lb = False
                    pos = i*int(cpl-(self.longest_name+7))

                    while lb == False:
                        if msg[pos] == " ":
                            nmsg[int(pos)] = " \n\t   "
                            lb = True
                        pos = pos-1

                msg = "".join(nmsg)
                self.ctx.insert_with_tags(self.ctx.get_end_iter(), sender+"\t   ", self.name_tag)
                self.ctx.insert_with_tags(self.ctx.get_end_iter(), msg, self.msg_tag)

            self.ctx.insert(self.ctx.get_end_iter(), "\n")

    def add_message(self, sender, msg):

        self.messages_list.append({"sender":sender, "msg":msg})

        try:
            if len(sender) > self.longest_name:
                self.longest_name = len(sender)
        except TypeError as e:
            print("error inserting message: ")
            print(e)