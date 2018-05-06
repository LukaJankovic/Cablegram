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

from .sidebar import SidebarChatItem
from .universe import Universe

@GtkTemplate(ui='/org/gnome/Cablegram/universe.ui')
class UniverseWindow(Gtk.ApplicationWindow):

    __gtype_name__ = 'UniverseWindow'

    sidebar_list = GtkTemplate.Child()

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

        def sidebar_clicked(self, row):
            print("sidebar clicked! index: "+str(row.get_index()))

        self.sidebar_list.connect('row-activated', sidebar_clicked)

        for i in Universe.instance().get_contacts()["users"]:
            print(i)
            sidebarItem = SidebarChatItem()
            try:
                sidebarItem.contact_label.set_text(i["first_name"]+" "+i["last_name"])
            except TypeError as e:
                print("Type error @ contact")
                print(i)
            sidebarItem.chat_label.set_text("You: Some message.")

            self.sidebar_list.insert(sidebarItem, -1)