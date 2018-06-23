# dialog.py
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
from pyrogram.api import functions, types

class dialog_item():
    dialog = None
    user = None
    chat = None
    channel = None
    dialog_type = None
    message = None
    from_user = None

def create_dialog_item(dialog_type, message, from_user, dialog, user=None, chat=None, channel=None):
    return_item = dialog_item()

    return_item.dialog = dialog
    return_item.user = user
    return_item.chat = chat
    return_item.channel = channel
    return_item.dialog_type = dialog_type
    return_item.message = message
    return_item.from_user = from_user

    return return_item

def input_peer_from_chat(chat_peer):
    return types.InputPeerChat(chat_id=chat_peer["chat_id"])

def input_peer_from_user(user_peer, a_hash):
    return types.InputPeerUser(user_id=user_peer["user_id"], access_hash=a_hash)

def input_peer_from_channel(channel_peer, a_hash):
    return types.InputPeerChannel(channel_id=channel_peer["channel_id"], access_hash=a_hash)

def download_dialogs_raw(client, o_date, o_id, o_peer):
    try:
        return client.send(functions.messages.GetDialogs(offset_date=o_date, offset_id=o_id, offset_peer=o_peer, limit=0))
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

def parse_dialogs(dialogs):
    new_dialogs = []

    for dialog in dialogs["dialogs"]:

        #TODO: Have a function that creates "return_item"-objects (AKA clean this mess up)

        if type(dialog["peer"]) == types.PeerUser:
            current_user = None
            for user in dialogs["users"]:
                if user["id"] == dialog["peer"]["user_id"]:
                    current_user = user

            if not current_user:
                print("Something has gone terribly wrong...")

            current_message = None
            for message in dialogs["messages"]:
                if message["id"] == dialog["top_message"]:
                    current_message = message

            from_user = ""
            if current_message["from_id"] == current_user["id"]:
                from_user = "remote"

            else:
                from_user = "you"

            return_item = create_dialog_item(dialog=dialog, user=current_user, dialog_type="user", message=current_message, from_user=from_user)

            new_dialogs.append(return_item)

        elif type(dialog["peer"]) == types.PeerChat:
            current_chat = None
            for chat in dialogs["chats"]:
                if chat["id"] == dialog["peer"]["chat_id"]:
                    current_chat = chat

            if not current_chat:
                print("Something has gone terribly wrong 2")

            current_message = None
            for message in dialogs["messages"]:
                if message["id"] == dialog["top_message"]:
                    current_message = message

            from_user = ""
            for user in dialogs["users"]:
                if user["id"] == current_message["from_id"]:
                    from_user = user

            return_item = create_dialog_item(dialog=dialog, chat=current_chat, dialog_type="chat", message=current_message, from_user=from_user)
            new_dialogs.append(return_item)

        elif type(dialog["peer"]) == types.PeerChannel:
            current_channel = None
            for channel in dialogs["chats"]:
                if channel["id"] == dialog["peer"]["channel_id"]:
                    current_channel = channel

            if not current_channel:
                print("if something wrong was so good why isn't there a something wrong 2?")

            current_message = None
            for message in dialogs["messages"]:
                if message["id"] == dialog["top_message"]:
                    current_message = message

            if not current_message:
                print("despacito error")

            return_item = create_dialog_item(dialog=dialog, channel=current_channel, dialog_type="channel", message=message, from_user=current_channel["title"])
            new_dialogs.append(return_item)

        else:
            print("Other type of dialog: ")
            print(dialog)

    return new_dialogs

def fetch_dialogs(client):

    dialogs_complete = parse_dialogs(download_dialogs_raw(client, 0, 0, types.InputPeerEmpty()))

    print(dialogs_complete)

    if len(dialogs_complete) == 20:
        total_dialogs = 20

        while total_dialogs % 20 == 0:
            latest_peer = None
            latest_item = dialogs_complete[total_dialogs-1].dialog.peer

            if isinstance(latest_item, types.PeerUser):
                a_hash = None
                for msg in dialogs_complete:
                    try:
                        if msg.user["id"] == latest_item["user_id"]:
                            a_hash = msg.user["access_hash"]
                    except TypeError:
                        # Just carry on...
                        pass
                latest_peer = input_peer_from_user(latest_item, a_hash)
            elif isinstance(latest_item, types.PeerChat):
                latest_peer = input_peer_from_chat(latest_item)
            elif isinstance(latest_item, types.PeerChannel):
                a_hash = None
                for msg in dialogs_complete["chats"]:
                    try:
                        if msg.channel["id"] == latest_item["channel_id"]:
                            a_hash = msg.channel["access_hash"]
                    except TypeError:
                        #Carry on...
                        pass
                latest_peer = input_peer_from_channel(latest_item, a_hash)
            else:
                print("something has gone horribly wrong: the pre-sequel")

            latest_date = dialogs_complete[total_dialogs-1].message["date"]
            latest_id = dialogs_complete[total_dialogs-1].message["id"]

            n_dialogs = download_dialogs_raw(client, latest_date, latest_id, latest_peer)

            dialogs_complete.extend(parse_dialogs(n_dialogs))
            total_dialogs = len(dialogs_complete)

    return dialogs_complete