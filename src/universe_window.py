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

from gi.repository import Gtk, Gdk, GLib, GObject
from .gi_composites import GtkTemplate

@GtkTemplate(ui='/org/gnome/Cablegram/universe.ui')
class UniverseWindow(Gtk.ApplicationWindow):

    __gtype_name__ = 'UniverseWindow'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.init_template()

    def present(self, **kwargs):
        super().present(**kwargs)
