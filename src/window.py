# window.py
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

from gi.repository import Gtk
from .gi_composites import GtkTemplate

import webbrowser

@GtkTemplate(ui='/org/gnome/Cablegram/login.ui')
class LoginWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'LoginWindow'

    loading_spinner = GtkTemplate.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.init_template()

    @GtkTemplate.Callback
    def api_clicked(self, widget, user_data):
        webbrowser.open("https://my.telegram.org/apps")

    @GtkTemplate.Callback
    def continue_clicked(self, widget, user_data):
        print("continue clicked")
        self.loading_spinner.start()