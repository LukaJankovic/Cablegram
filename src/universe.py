#!@PYTHON@

# universe.py
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

from pyrogram import Client, Filters

class Universe:

    app = None

    def __init__(self):
        print("global init")

    def login(api_id, api_hash, phone_nr, callback):
        app = Client("cablegram", api_id=api_id, api_hash=api_hash, phone_number=phone_nr, phone_code=callback)