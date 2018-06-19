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

import pyrogram
import threading
import os
import os.path

from pathlib import Path

from pyrogram.api import functions, types
#from pyrogram import Client, Filters

from .dialog import *

class Singleton(object):
    __singleton_lock = threading.Lock()
    __singleton_instance = None

    @classmethod
    def instance(cls):
        if not cls.__singleton_instance:
            with cls.__singleton_lock:
                if not cls.__singleton_instance:
                    cls.__singleton_instance = cls()
        return cls.__singleton_instance

class Universe(Singleton):
    app = None
    loggedin = False

    def __init__(self):
        print("global init")

    def is_loggedin(self):
        if os.path.isfile(str(Path.home()) + "/cablegram.session") and os.path.isfile(str(Path.home())+"/.config/cablegram.ini"):
            return True
        else:
            return False

    def login(self, api_id, api_hash, phone_nr, callback):

        try:
            self.app = pyrogram.Client("cablegram", api_id=api_id, api_hash=api_hash, phone_number=phone_nr, phone_code=callback)
            self.app.start()

            return None
        except pyrogram.api.errors.exceptions.flood_420.FloodWait as error:
            #Flood error
            return error
        except pyrogram.api.errors.exceptions.bad_request_400.PhoneNumberInvalid as error:
            #Invalid number
            return error
        except pyrogram.api.errors.exceptions.bad_request_400.ApiIdInvalid as error:
            #Invalid API
            #TODO: Pyrogram goes crazy here so uh don't enter the wrong api key please
            return error
        except pyrogram.api.errors.exceptions.bad_request_400.PhoneCodeInvalid as error:
            #Invalid phone code
            return error

    def get_dialogs(self):
        return fetch_dialogs(self.app)

    def get_history(self, user_id):
        try:
            history = self.app.get_history(user_id)
            return history
        except pyrogram.api.errors.exceptions.flood_420.FloodWait as error:
            #Flood error
            return error
        except pyrogram.api.errors.exceptions.bad_request_400.PhoneNumberInvalid as error:
            #Invalid number
            return error
        except pyrogram.api.errors.exceptions.bad_request_400.ApiIdInvalid as error:
            #Invalid API
            #TODO: Pyrogram goes crazy here so uh don't enter the wrong api key please
            return error
        except pyrogram.api.errors.exceptions.bad_request_400.PhoneCodeInvalid as error:
            #Invalid phone code
            return error 