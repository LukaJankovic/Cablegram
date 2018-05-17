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

from pyrogram.api import functions, types
#from pyrogram import Client, Filters

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

    def __init__(self):
        print("global init")

    def login(self, api_id, api_hash, phone_nr, callback):
        print("pyrogram login")

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
        try:
            dialogs = self.app.send(functions.messages.GetDialogs(offset_date=0, offset_id=0, offset_peer=types.InputPeerEmpty(), limit=0))

            new_dialogs = []

            for dialog in dialogs["dialogs"]:
                if type(dialog["peer"]) == types.PeerUser:
                    current_user = None
                    for user in dialogs["users"]:
                        if user["id"] == dialog["peer"]["user_id"]:
                            current_user = user

                    if not current_user:
                        print("Something has gone terribly wrong...")

                    new_dialogs.append({"type":"user","user":current_user})

                elif type(dialog["peer"]) == types.PeerChat:
                    current_chat = None
                    for chat in dialogs["chats"]:
                        if chat["id"] == dialog["peer"]["chat_id"]:
                            current_chat = chat

                    if not current_chat:
                        print("Something has gone terribly wrong 2")

                    new_dialogs.append({"type":"chat","chat":current_chat})


                else:
                    print("Other type of chat: ")
                    print(dialog)

            return new_dialogs


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