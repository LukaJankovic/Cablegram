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

class chat_view_manager:

    ctx = None
    longest_name = -1

    def __init__(self, ctx):
        self.ctx = ctx

    def add_message(self, sender, msg):
        print("add msg")

        if len(sender) > self.longest_name:
            self.longest_name = len(sender)

        self.ctx.insert(self.ctx.get_end_iter(), sender.ljust(30-len(sender)) + "    " + msg+"\n")