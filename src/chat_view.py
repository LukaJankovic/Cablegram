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

class chat_view_manager:

    ctx = None
    longest_name = -1

    name_tag = None
    msg_tag = None

    def __init__(self, ctx):
        self.ctx = ctx

        self.setup_tags()

    def setup_tags(self):

        self.name_tag = self.ctx.create_tag("name", weight=Pango.Weight.BOLD, left_margin=5, left_margin_set=True)
        self.msg_tag = self.ctx.create_tag("msg")

    def setup_indent(self, text_view):

        #TODO: Make customizable
        tabs = Pango.TabArray(1, True)
        tabs.set_tab(0, Pango.TabAlign.LEFT, 50)
        text_view.tabs = tabs

    def clear(self):
        self.ctx.set_text("")

    def add_message(self, sender, msg):
        if len(sender) > self.longest_name:
            self.longest_name = len(sender)

        self.ctx.insert_with_tags(self.ctx.get_end_iter(), sender, self.name_tag)
        self.ctx.insert_with_tags(self.ctx.get_end_iter(), "\t"+msg, self.msg_tag)
        self.ctx.insert(self.ctx.get_end_iter(), "\n")