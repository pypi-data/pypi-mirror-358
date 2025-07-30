from datetime import datetime
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.errors.rpcerrorlist import ChannelPrivateError, ChannelInvalidError
import pandas as pd
# from telethon.tl.types import ReactionEmoji, ReactionCustomEmoji, PeerUser, PeerChannel
from opsci_toolbox.helpers.common import create_dir, write_pickle, write_json
import os
import nest_asyncio
from telethon.tl.types import Message
import json
from tqdm import tqdm
nest_asyncio.apply()


class JSONEncoder(json.JSONEncoder):
    '''
    JSONEncoder subclass that knows how to encode date/time and bytes.
    '''
    def default(self, o):
        if isinstance(o, datetime) or isinstance(o, bytes):
            return str(o)
        return super().default(o)
    
def dump_jsonl(data: list[dict], path: str, name: str) -> str:
    """
    Write data to a JSON Lines (jsonl) file. Each dictionary in the list represents a single JSON object.

    Args:
        data (list[dict]): The list of dictionaries to be written to the JSON Lines file.
        path (str): The directory path where the JSON Lines file will be saved.
        name (str): The name of the JSON Lines file (without the extension).

    Returns:
        str: The full path to the saved JSON Lines file.
    """
    file_path = os.path.join(path, name + '.jsonl')
    with open(file_path, 'w') as file:
        for entry in data:
            json.dump(entry, file, cls=JSONEncoder)
            file.write('\n')
    return file_path
    
    
def parse_mediafileid(message: Message) -> str:
    """
    Parse the media file ID from a Telegram message.

    Args:
        message (telethon.tl.types.Message): The Telegram message.

    Returns:
        Optional[str]: The media file ID if available, None otherwise.
    """
    data = message.to_dict()
    media = data.get("media", {})
    media_id = parse_media_id(media)

    if media_id:
        message_id = data.get("id")
        peer_id = data.get("peer_id", {})
        if peer_id is None:
            peer_id = {}
        channel_id = parse_from(peer_id)
        grouped_id = data.get("grouped_id")
        if grouped_id:
            grouped_id = grouped_id
        else:
            grouped_id = message_id
    
        media_fileid = str(int(channel_id))+'_'+str(int(grouped_id))+'_'+str(int(media_id))
        return media_fileid
    else:
        return None


def parse_message_entities(messages : list) -> pd.DataFrame:
    """
    Parse Telegram messages entities.

    Args:
        messages : a list of Telegram messages.

    Returns:
        pd.DataFrame : a DataFrame containing the parsed entities.
    """
    all_records = []
    for data in messages:
        # raw_text = message.raw_text

        # data = message.to_dict()

        message_id = data.get("id")

        peer_id = data.get("peer_id", {})
        if peer_id is None:
            peer_id = {}
        channel_id = parse_from(peer_id)

        from_id = data.get("from_id", {})
        if from_id is None :
            from_id = {}
        from_id = parse_from(from_id)
        if from_id is None:
            from_id = channel_id

        grouped_id = data.get("grouped_id")
        if grouped_id:
            grouped_id = grouped_id
        else:
            grouped_id = message_id

        message = data.get("message")

        entities = data.get("entities", [])
        for entity in entities:
            entity_type = entity.get("_")
            offset = entity.get("offset")
            length = entity.get("length")
            url = entity.get("url")
            document_id = entity.get("document_id")

            entity_record = (message_id, channel_id, from_id, grouped_id, message, entity_type, offset, length, url, document_id)
            all_records.append(entity_record)
    
    df = pd.DataFrame.from_records(all_records, columns=["message_id", "channel_id", "from_id", "grouped_id", "message", "entity_type", "offset", "length", "url", "document_id"])
    return df


def parse_messages(messages : list) -> pd.DataFrame:
    """
    Parse Telegram messages.

    Args:
        messages : a list of Telegram messages.

    Returns:
        pd.DataFrame : a DataFrame containing the parsed information from the Telegram messages.
    """
    
    all_records = []
    for message in messages:
        # raw_text = message.raw_text

        data = message

        message_id = data.get("id")

        peer_id = data.get("peer_id", {})
        if peer_id is None:
            peer_id = {}
        channel_id = parse_from(peer_id)

        from_id = data.get("from_id", {})
        if from_id is None :
            from_id = {}
        from_id = parse_from(from_id)
        if from_id is None:
            from_id = channel_id

        date = data.get("date")
        message = data.get("message")
        views = data.get("views", 0)
        forwards = data.get("forwards", 0)
        if forwards is None:
            forwards = 0

        replies = data.get("replies", {})
        if replies:
            replies = replies.get("replies")
        else:
            replies = 0

        grouped_id = data.get("grouped_id")
        if grouped_id:
            grouped_id = grouped_id
        else:
            grouped_id = message_id

        reactions = data.get("reactions", {})
        if reactions:
            total_reactions, reactions_details = parse_reactions(reactions)
        else:
            total_reactions, reactions_details = 0, None


        reply_to = data.get("reply_to", {})
        reply_to_message_id, reply_to_channel_id = parse_reply(reply_to)

        media = data.get("media", {})
        media_record = parse_media(media)
        fwd_from = data.get("fwd_from", {})
        if fwd_from is None:
            fwd_from = {}   
        fwd_record = parse_fwd(fwd_from)
        engagements = forwards + replies + total_reactions


        post_record = (message_id, channel_id, from_id, grouped_id, date, message, views, forwards, replies, total_reactions, reactions_details, engagements, reply_to_message_id, reply_to_channel_id) + media_record + fwd_record
        all_records.append(post_record)

    df = pd.DataFrame.from_records(all_records, columns=["message_id", "channel_id", "from_id", "grouped_id", "date", "message", "views", "forwards", "replies", "reactions", "details_reactions", "engagements", "reply_to_message_id", "reply_to_channel_id",
                                            "media_id", "media_date", "media_mime_type", "media_size", "media_filename", "duration", "width", "height", 
                                            "webpage_id", "webpage_url", "webpage_type", "webpage_site_name", "webpage_title", "webpage_description",
                                            "fwd_date", "fwd_from_id", "fwd_from_post_id", "fwd_from_from_name"])
                                                
    return df

def parse_reply(reply:dict) -> tuple:
    """
    Parse reply object from a Telegram message.

    Args:
        reply : a dict corresponding to the reply object.

    Returns:
        Tuple of reply_to_message_id, reply_to_channel_id
    """
    reply_to_message_id, reply_to_channel_id = None, None
    if reply:
        reply_to_message_id = reply.get("reply_to_msg_id")
        reply_to_peer_id = reply.get("reply_to_peer_id", {})
        if reply_to_peer_id is None:
            reply_to_peer_id = {}
        reply_to_channel_id = parse_from(reply_to_peer_id)
    
    return reply_to_message_id, reply_to_channel_id

def parse_from(data : dict) -> int:
    """
    Parse a peer object from Telegram message.

    Args:
        data : a dict corresponding to the peer object.

    Returns:
        int : the channel_id or user_id.
    """
    if data.get("_"):
        if data.get("_")=="PeerChannel":
            channel_id = data.get('channel_id')
        elif data.get("_")=="PeerUser":
            channel_id = data.get('user_id')
        else:
            print("PEER not referenced", data.get('_'))
            channel_id = None
    else:
        channel_id = None
    return channel_id


def parse_fwd(forward : dict) -> tuple:
    """
    Parse a forward object from Telegram message.

    Args:
        forward : a dict corresponding to the forward object.

    Returns:
        tuple containing, date, post id, channel id and name related to the forward.
    """
    fwd_from_date, from_id, fwd_from_channel_post_id, fwd_from_from_name = None, None, None, None
    if forward:
        fwd_from_date = forward.get("date")
        fwd_from_channel_post_id = forward.get("channel_post")
        fwd_from_from_name = forward.get("from_name")
        fwd_from_id = forward.get("from_id", {})
        if fwd_from_id is None :
            fwd_from_id = {}    
        from_id = parse_from(fwd_from_id)

    fwd_record = (fwd_from_date, from_id, fwd_from_channel_post_id, fwd_from_from_name)
    return fwd_record

def parse_reactions(reactions: dict) -> tuple:
    """
    Parse reactions from Telegram message.

    Args:
        reactions : a dict corresponding to the reactions object.

    Returns:
        tuple containing the total number of reactions and the details of each reaction.
    """
    # details = dict()
    details=[]
    results = reactions.get("results", [])
    total_reactions = 0
    for res in results:
        count = res.get("count", 0)
        total_reactions += count
        reaction = res.get("reaction",{})
        if reaction.get("_")=="ReactionEmoji":
            emoticon = reaction.get("emoticon", "")
        else :
            emoticon =  str(reaction.get("document_id",""))

        # details[emoticon] = count
        details.append((emoticon, count))

    return total_reactions, details

def parse_media(media : dict) -> tuple:
    """
    Parse medias from Telegram message. Currently it supports photo, document and webpage.

    Args:
        media : a dict corresponding to the media object.

    Returns:
        tuple containing media metadata.
    """
    webpage_id, webpage_url, webpage_type, webpage_site_name, webpage_title, webpage_description =  None, None, None, None, None, None
    media_id, media_date, media_mime_type, media_size, media_filename, duration, width, height = None, None, None, 0, None, 0, 0, 0
    if media : 
        if media.get("_") == "MessageMediaPhoto":
            photo = media.get("photo", {})
            media_id = photo.get("id")
            if media_id:
                media_id = str(int(media_id))
            media_date = photo.get("date")
            media_mime_type = "photo"
            
        elif media.get("_") == "MessageMediaDocument":
            document = media.get("document", {})
            media_id = document.get("id")
            if media_id:
                media_id = str(int(media_id))
            media_date = document.get("date")
            media_mime_type = document.get("mime_type")
            media_size = document.get("size")
            attributes = document.get("attributes", [])
            for attr in attributes:
                if attr.get("_") == "DocumentAttributeFilename":
                    media_filename = str(attr.get("file_name", ""))
                elif attr.get("_") == "DocumentAttributeVideo":
                    duration = attr.get("duration")
                    width = attr.get("w")
                    height = attr.get("h")
        elif media.get("_") == "MessageMediaWebPage":
            webpage = media.get("webpage", {})
            webpage_id = webpage.get("id")
            webpage_url = webpage.get("url")
            webpage_type = webpage.get("type")
            webpage_site_name = webpage.get("site_name")
            webpage_title = webpage.get("title")
            webpage_description = webpage.get("description")

        else :
            print("MEDIA not referenced", media.get('_'))
    
    media_record = (media_id, media_date, media_mime_type, media_size, media_filename, duration, width, height, webpage_id, webpage_url, webpage_type, webpage_site_name, webpage_title, webpage_description)
    return media_record

def parse_media_id(media : dict) -> int:
    """
    Parse media id from Telegram message.

    Args:
        media : a dict corresponding to the media object.

    Returns:
        int : the media_id.
    """
    media_id = None
    if media : 
        if media.get("_") == "MessageMediaPhoto":
            photo = media.get("photo", {})
            media_id = photo.get("id")
            
        elif media.get("_") == "MessageMediaDocument":
            document = media.get("document", {})
            media_id = document.get("id")

        else :
            media_id = None
    return media_id


class JSONEncoder(json.JSONEncoder):
    '''
    JSONEncoder subclass that knows how to encode date/time and bytes.
    '''
    def default(self, o):
        if isinstance(o, datetime) or isinstance(o, bytes):
            return str(o)
        return super().default(o)
    
def dump_jsonl(data: list[dict], path: str, name: str) -> str:
    """
    Write data to a JSON Lines (jsonl) file. Each dictionary in the list represents a single JSON object.

    Args:
        data (list[dict]): The list of dictionaries to be written to the JSON Lines file.
        path (str): The directory path where the JSON Lines file will be saved.
        name (str): The name of the JSON Lines file (without the extension).

    Returns:
        str: The full path to the saved JSON Lines file.
    """
    file_path = os.path.join(path, name + '.jsonl')
    with open(file_path, 'w') as file:
        for entry in data:
            json.dump(entry, file, cls=JSONEncoder)
            file.write('\n')
    return file_path
    

async def get_forwarded_messages(client: TelegramClient, phone_number: str, channel_username: int, reverse: bool = True, limit: int = None, offset_date: datetime = datetime(1970,1,1), path_file: str = "files"):
    try:
        await client.start(phone_number)

        path_json = create_dir(os.path.join(path_file, "JSON"))    
    
        # Fetch the messages from the channel
        # forwarded_messages = []
        forwarded_messages_dict = []
        new_channels = set()

        async for message in client.iter_messages(channel_username,
                                                  limit=limit,
                                                  offset_date=offset_date,
                                                  reverse=reverse):
            # Check if the message is a forward
            if message.forward and hasattr(message.forward.chat, 'username'):
                # forwarded_messages.append(message)
                forwarded_messages_dict.append(message.to_dict())

                if message.forward.chat:
                    new_channel = message.forward.chat.username
                    if new_channel:
                        new_channels.add(new_channel)
        
        if forwarded_messages_dict:
            dump_jsonl(forwarded_messages_dict, path_json, str(channel_username))
        
    except (ChannelPrivateError, ChannelInvalidError):
        print(f"Cannot access channel: {channel_username}")
    
    return forwarded_messages_dict, new_channels

        
async def recursive_forward_scraper(seed_channels, depth, client: TelegramClient, phone_number: str,  reverse: bool = True, limit: int = None, offset_date: datetime = datetime(1970,1,1), path_file: str = "files"):
    """
    Recursively collects forwarded messages from channels, starting from the seed channels up to a specific depth.
    """
    all_forwarded_messages = []
    visited_channels = set(seed_channels)
    current_level_channels = set(seed_channels)

    path_json = create_dir(os.path.join(path_file, "CHANNELS"))
    
    for level in range(depth):
        print(level)
        print(f"Processing level {level + 1} with {len(current_level_channels)} channels...")
        next_level_channels = set()
        
        # Iterate through channels at the current level
        for channel in tqdm(current_level_channels, total=len(current_level_channels), desc="get messages"):
            forwarded_msgs, discovered_channels = await get_forwarded_messages(client, phone_number, channel, reverse, limit, offset_date, path_file)

            # Collect forwarded messages
            all_forwarded_messages.extend(forwarded_msgs)
            
            # Add newly discovered channels to the next level, excluding already visited ones
            for new_channel in discovered_channels:
                if new_channel not in visited_channels:
                    next_level_channels.add(new_channel)
                    visited_channels.add(new_channel)
        # Update the set of channels for the next level of recursion
        current_level_channels = next_level_channels
        
        if not current_level_channels:
            break
    
    write_json(visited_channels, path_json, "visited_channels")
    return all_forwarded_messages, visited_channels


def group_by_post(df : pd.DataFrame) -> pd.DataFrame:
    """
    Function to group message by "post". If a post embed multiple media, Telethon returns separate messages for each media. This function groups them together ensuring also type consistency. 

    Args:
        df : dataframe containing messages.

    Returns:
        pd.DataFrame : a DataFrame containing the grouped messages.
    """
    aggregations = {
            'concatenated_message_id': ("message_id",  lambda x: '-'.join(x.dropna().astype(str))),
            'message_id': ("message_id",  lambda x: list(x[x.notna()].astype(int).astype(str))),
            'from_id': ("from_id", lambda x: str(int(x.dropna().max())) if pd.notna(x.dropna().max()) else None),
            "date" : ("date", "max"),
            "message": ("message", "max"), 
            "views": ("views", "max"), 
            "forwards": ("forwards", "max"), 
            "replies": ("replies", "max"), 
            "reactions": ("reactions", "max"), 
            "details_reactions": ("details_reactions", lambda x: x[x.notna()]),
            "engagements": ("engagements", "max"), 
            "reply_to_message_id": ("reply_to_message_id", lambda x: str(int(x.dropna().max())) if pd.notna(x.dropna().max()) else None),
            "reply_to_channel_id": ("reply_to_channel_id", lambda x: str(int(x.dropna().max())) if pd.notna(x.dropna().max()) else None),
            "media_id" : ("media_id", lambda x: list(x[x.notna()].astype(int).astype(str))), 
            "media_date": ("media_date", lambda x: list(x[x.notna()])), 
            "media_mime_type": ("media_mime_type", lambda x: list(x[x.notna()])), 
            "media_size": ("media_size", lambda x: list(x[x.notna()].astype(int).astype(str))), 
            "media_filename": ("media_filename", lambda x: list(x[x.notna()])), 
            "media_fileid": ("media_fileid", lambda x: list(x[x.notna()].astype(str))), 
            "duration": ("duration", lambda x: list(x[x.notna()].astype(int).astype(str))), 
            "width": ("width", lambda x: list(x[x.notna()].astype(int).astype(str))), 
            "height": ("height", lambda x: list(x[x.notna()].astype(int).astype(str))), 
            "webpage_id": ("webpage_id", lambda x: list(x[x.notna()].astype(int).astype(str))), 
            "webpage_url": ("webpage_url", lambda x: list(x[x.notna()])), 
            "webpage_type": ("webpage_type", lambda x: list(x[x.notna()])), 
            "webpage_site_name": ("webpage_site_name", lambda x: list(x[x.notna()])),
            "webpage_title": ("webpage_title", lambda x: list(x[x.notna()])), 
            "webpage_description": ("webpage_description", lambda x: list(x[x.notna()])),
            "fwd_date": ("fwd_date", "max"), 
            "fwd_from_id": ("fwd_from_id", lambda x: str(int(x.dropna().max())) if pd.notna(x.dropna().max()) else None),
            "fwd_from_post_id": ("fwd_from_post_id", lambda x: str(int(x.dropna().max())) if pd.notna(x.dropna().max()) else None),
            "fwd_from_from_name":("fwd_from_from_name", "max")

    }
    df = df.groupby(['channel_id',"grouped_id"]).agg(**aggregations).reset_index()
    return df

# async def get_messages_by_date(client: TelegramClient, phone_number: str, channel_username: int, dl_files: bool = False, reverse: bool = True, limit: int = None, offset_date: datetime = datetime(1970,1,1), ids: list = [], path_file: str = "files", dl_thumbs : bool = False) -> list:
#     """
#     Retrieves messages from a Telegram channel by date.

#     Args:
#         client (TelegramClient): The Telegram client instance.
#         phone_number (str): The phone number associated with the Telegram account.
#         channel_username (str): The username of the channel to retrieve messages from.
#         dl_files (bool, optional): Whether to download media files attached to the messages. Defaults to False.
#         reverse (bool, optional): Whether to retrieve messages in reverse order. Defaults to True.
#         limit (int, optional): The maximum number of messages to retrieve. Defaults to None (retrieve all messages).
#         offset_date (datetime, optional): The starting date to retrieve messages from. Defaults to datetime(1970,1,1).
#         path_file (str, optional): The path to save the downloaded files. Defaults to "files".

#     Returns:
#         list: A list of messages retrieved from the channel.

#     Raises:
#         Exception: If there is an error during the retrieval process.

#     """
#     try:
#         await client.start(phone_number)

#         # current_path_file = create_dir(os.path.join(path_file, "messages"))
#         path_messages = create_dir(os.path.join(path_file, "messages"))
#         path_entities = create_dir(os.path.join(path_file, "entities"))

#         if dl_files:
#             current_path_img = create_dir(os.path.join(path_file, "img", str(channel_username)))
#         if dl_thumbs:
#             current_path_thumbs = create_dir(os.path.join(path_file, "thumbs", str(channel_username)))

#         # Get the message history
#         messages = []

#         async for message in client.iter_messages(channel_username,
#                                                   limit=limit,
#                                                   offset_date=offset_date,
#                                                   reverse=reverse):
#             messages.append(message)

#             if dl_files:
                
#                 media_fileid = parse_mediafileid(message)
#                 if media_fileid:
#                     await message.download_media(file=os.path.join(current_path_img, media_fileid))

#             if dl_thumbs:                
#                 media_fileid = parse_mediafileid(message)
#                 if media_fileid:
#                     try:
#                         await message.download_media(file=os.path.join(current_path_thumbs, media_fileid), thumb=-1)
#                     except Exception as e:
#                         pass
#                         print(e)

#         df_exploded = parse_messages(messages)
#         df_exploded.loc[df_exploded['media_id'].notna(), "media_fileid"] = df_exploded['channel_id'].astype(str)+'_'+df_exploded['grouped_id'].astype(str)+'_'+df_exploded['media_id'].astype(str)
#         write_pickle(df_exploded, path_messages, str(channel_username))

#         df_entities = parse_message_entities(messages)
#         write_pickle(df_entities, path_entities, str(channel_username))

#         # df_messages = group_by_post(df_exploded)
#         # df_messages['uniq_id']=df_messages['channel_id'].astype(str)+'_'+df_messages['from_id'].astype(str)+'_'+df_messages['concatenated_message_id'].astype(str)
#         # write_pickle(df_messages, current_path_file, str(channel_username))

#         return messages
#     finally:
#         # Disconnect the client
#         await client.disconnect()

async def get_messages_by_date(client: TelegramClient, phone_number: str, channel_username: int, dl_files: bool = False, reverse: bool = True, limit: int = None, offset_date: datetime = datetime(1970,1,1), path_file: str = "files", dl_thumbs : bool = False) -> list:
    """
    Retrieves messages from a Telegram channel by date.

    Args:
        client (TelegramClient): The Telegram client instance.
        phone_number (str): The phone number associated with the Telegram account.
        channel_username (str): The username of the channel to retrieve messages from.
        dl_files (bool, optional): Whether to download media files attached to the messages. Defaults to False.
        reverse (bool, optional): Whether to retrieve messages in reverse order. Defaults to True.
        limit (int, optional): The maximum number of messages to retrieve. Defaults to None (retrieve all messages).
        offset_date (datetime, optional): The starting date to retrieve messages from. Defaults to datetime(1970,1,1).
        path_file (str, optional): The path to save the downloaded files. Defaults to "files".

    Returns:
        list: A list of messages retrieved from the channel.

    Raises:
        Exception: If there is an error during the retrieval process.

    """
    try:
        await client.start(phone_number)

        # current_path_file = create_dir(os.path.join(path_file, "messages"))
        path_json = create_dir(os.path.join(path_file, "JSON"))
        path_messages = create_dir(os.path.join(path_file, "messages"))
        path_entities = create_dir(os.path.join(path_file, "entities"))

        if dl_files:
            current_path_img = create_dir(os.path.join(path_file, "img", str(channel_username)))
        if dl_thumbs:
            current_path_thumbs = create_dir(os.path.join(path_file, "thumbs", str(channel_username)))

        # Get the message history
        # messages = []
        messages_dict = []

        async for message in client.iter_messages(channel_username,
                                                  limit=limit,
                                                  offset_date=offset_date,
                                                  reverse=reverse):
            # messages.append(message)
            messages_dict.append(message.to_dict())
            

            if dl_files:
                
                media_fileid = parse_mediafileid(message)
                if media_fileid:
                    await message.download_media(file=os.path.join(current_path_img, media_fileid))

            if dl_thumbs:                
                media_fileid = parse_mediafileid(message)
                if media_fileid:
                    try:
                        await message.download_media(file=os.path.join(current_path_thumbs, media_fileid), thumb=-1)
                    except Exception as e:
                        pass
                        print(e)

        dump_jsonl(messages_dict, path_json, str(channel_username))
        df_exploded = parse_messages(messages_dict)
        df_exploded.loc[df_exploded['media_id'].notna(), "media_fileid"] = df_exploded['channel_id'].astype(str)+'_'+df_exploded['grouped_id'].astype(str)+'_'+df_exploded['media_id'].astype(str)
        write_pickle(df_exploded, path_messages, str(channel_username))

        df_entities = parse_message_entities(messages_dict)
        write_pickle(df_entities, path_entities, str(channel_username))

        # df_messages = group_by_post(df_exploded)
        # df_messages['uniq_id']=df_messages['channel_id'].astype(str)+'_'+df_messages['from_id'].astype(str)+'_'+df_messages['concatenated_message_id'].astype(str)
        # write_pickle(df_messages, current_path_file, str(channel_username))

        return messages_dict
    finally:
        # Disconnect the client
        await client.disconnect()

async def get_messages_by_ids(client: TelegramClient, phone_number: str, channel_username:int, dl_files:bool=False, ids:list=[], path_file:str="files")-> list:
    """
    Retrieves messages from a Telegram channel by IDS.

    Args:
        client (TelegramClient): The Telegram client instance.
        phone_number (str): The phone number associated with the Telegram account.
        channel_username (str): The username of the channel to retrieve messages from.
        dl_files (bool, optional): Whether to download media files attached to the messages. Defaults to False.
        ids (list) : list of message ids to retrieve
        path_file (str, optional): The path to save the downloaded files. Defaults to "files".

    Returns:
        list: A list of messages retrieved from the channel.

    Raises:
        Exception: If there is an error during the retrieval process.

    """
    try:
        await client.start(phone_number)
        path_json = create_dir(os.path.join(path_file, "JSON"))
        path_messages = create_dir(os.path.join(path_file, "messages"))
        path_entities = create_dir(os.path.join(path_file, "entities"))

        # Get the message history
        # messages = []
        messages_dict = []

        async for message in client.iter_messages(channel_username,
                                                  ids = ids):
            # messages.append(message)
            messages_dict.append(message.to_dict())

            if dl_files:
                current_path_img = create_dir(os.path.join(path_file, "img", str(channel_username)))
                media_fileid = parse_mediafileid(message)
                if media_fileid:
                    await message.download_media(file=os.path.join(current_path_img, media_fileid))


        dump_jsonl(messages_dict, path_json, str(channel_username))
        df_exploded = parse_messages(messages_dict)
        df_exploded.loc[df_exploded['media_id'].notna(), "media_fileid"] = df_exploded['channel_id'].astype(str)+'_'+df_exploded['grouped_id'].astype(str)+'_'+df_exploded['media_id'].astype(str)
        write_pickle(df_exploded, path_messages, str(channel_username))

        df_entities = parse_message_entities(messages_dict)
        write_pickle(df_entities, path_entities, str(channel_username))


        # df_messages = group_by_post(df_exploded)
        # df_messages['uniq_id']=df_messages['channel_id'].astype(str)+'_'+df_messages['message_id'].astype(str)
        # write_pickle(df_messages, current_path_file, str(channel_username))

        return messages_dict
    finally:
        # Disconnect the client
        await client.disconnect()

async def get_messages_by_search(client: TelegramClient, phone_number: str, search:str= "SNCF", channel_username:int = None, dl_files:bool=False, limit:int=None, path_file:str="files") -> list:
    """,
    Retrieves messages from a Telegram channel by date.

    Args:
        client (TelegramClient): The Telegram client instance.
        phone_number (str): The phone number associated with the Telegram account.
        search (str): The search term to look for in the messages.
        channel_username (str): The username of the channel to retrieve messages from.
        dl_files (bool, optional): Whether to download media files attached to the messages. Defaults to False.
        limit (int, optional): The maximum number of messages to retrieve. Defaults to None (retrieve all messages).
        path_file (str, optional): The path to save the downloaded files. Defaults to "files".

    Returns:
        list: A list of messages retrieved from the channel.

    Raises:
        Exception: If there is an error during the retrieval process.

    """
    try:
        await client.start(phone_number)

        # current_path_file = create_dir(os.path.join(path_file, "messages"))
        path_json = create_dir(os.path.join(path_file, "JSON"))
        path_messages = create_dir(os.path.join(path_file, "messages"))
        path_entities = create_dir(os.path.join(path_file, "entities"))

        if dl_files:
            current_path_img = create_dir(os.path.join(path_file, "img", str(channel_username)))

        # Get the message history
        # messages = []
        messages_dict = []

        async for message in client.iter_messages(channel_username,
                                                  search=search,
                                                  limit=limit):
            # messages.append(message)
            messages_dict.append(message.to_dict())

            if dl_files:
                
                media_fileid = parse_mediafileid(message)
                if media_fileid:
                    await message.download_media(file=os.path.join(current_path_img, media_fileid))

        
        df_exploded = parse_messages(messages_dict)
        df_exploded['search']=search
        df_exploded.loc[df_exploded['media_id'].notna(), "media_fileid"] = df_exploded['channel_id'].astype(str)+'_'+df_exploded['grouped_id'].astype(str)+'_'+df_exploded['media_id'].astype(str)
        # df_messages = group_by_post(df_exploded)
        # df_messages['uniq_id']=df_messages['channel_id'].astype(str)+'_'+df_messages['concatenated_message_id'].astype(str)
        df_entities = parse_message_entities(messages_dict)

        if channel_username:
            write_pickle(df_exploded, path_messages, str(search)+'_'+str(channel_username))
            write_pickle(df_entities, path_entities, str(search)+'_'+str(channel_username))
        else:
            write_pickle(df_exploded, path_messages, str(search))
            write_pickle(df_entities, path_entities, str(search))

        return messages_dict
    finally:
        # Disconnect the client
        await client.disconnect()

async def download_comments(client: TelegramClient, phone_number: str,channel_entity : int, message_id: int, dl_files:bool = False, limit:int = None, reverse:bool=True, path_file:str ="files")->list:
    try:
        # Connect the client
        await client.start(phone_number)

        # current_path_file = create_dir(os.path.join(path_file, "messages"))
        path_messages = create_dir(os.path.join(path_file, "messages"))
        path_entities = create_dir(os.path.join(path_file, "entities"))

        comments_dict = []
        
        async for comment in client.iter_messages(int(channel_entity), reply_to=int(message_id), limit=limit, reverse=reverse):
            comments_dict.append(comment.to_dict())

        if dl_files:
            current_path_img = create_dir(os.path.join(path_file, "img", str(channel_entity)))
            media_fileid = parse_mediafileid(comment)
            if media_fileid:
                await comment.download_media(file=os.path.join(current_path_img, media_fileid))

        df_comments = parse_messages(comments_dict)
        df_comments.loc[df_comments['media_id'].notna(), "media_fileid"] = df_comments['channel_id'].astype(str)+'_'+df_comments['grouped_id'].astype(str)+'_'+df_comments['media_id'].astype(str)
        write_pickle(df_comments, path_messages, str(channel_entity)+"_"+str(message_id))

        df_entities = parse_message_entities(comments_dict)
        write_pickle(df_entities, path_entities, str(channel_entity)+"_"+str(message_id))
        
        return comments_dict
    
    finally:
        # Disconnect the client
        await client.disconnect()



# def parse_telegram_messages(messages : list) -> pd.DataFrame:
#     """
#     Parses the given list of Telegram messages and returns a DataFrame with the extracted information.

#     Args:
#         messages (list): A list of Telegram messages.

#     Returns:
#         pandas.DataFrame: A DataFrame containing the parsed information from the Telegram messages.

#     """

#     all_records = []
#     for message in messages:

#         peer_id = message.peer_id

#         if peer_id:
#             channel_id = str(peer_id.channel_id)
#         else:
#             channel_id=''
#         if message.id:
#             message_id = str(message.id)
#         else:
#             message_id=''

#         uniq_id = str(channel_id) + "_" + str(message_id)
#         if message.date:
#             message_date = message.date
#         else:
#             message_date=datetime(1970,1,1)
#         if message.text:
#             text = message.text
#         else:
#             text = ''
#         if message.is_reply:
#             is_reply = message.is_reply
#         else:
#             is_reply = False

#         if message.views:
#             views = int(message.views)
#         else:
#             views = 0
#         if  message.forwards:
#             forwards = int(message.forwards)
#         else:
#             forwards = 0

#         ##########################################
#         # REPLIES
#         ##########################################
#         if message.replies :
#             replies = message.replies
#             if replies.replies:
#                 replies_count = int(replies.replies)
#             else:
#                 replies_count = 0
    
#             if replies.channel_id:
#                 replies_channel_id = replies.channel_id
#             else:
#              replies_channel_id = ''
#         else :
#             replies_count, replies_channel_id= 0, ''
        
#         ##########################################
#         # REACTIONS
#         ##########################################
        
#         total_reactions = 0
#         details_reactions=[]
        
#         if message.reactions:
#             reactions = message.reactions
#             reactions_lst = reactions.results
#             for reaction in reactions_lst:
#                 if reaction.count:
#                     count = int(reaction.count)
#                 else:
#                     count = 0
#                 total_reactions += count
#                 r = reaction.reaction

#                 if isinstance(r, ReactionEmoji):
#                     emoticon = r.emoticon
#                 elif isinstance(r, ReactionCustomEmoji):
#                     emoticon = r.document_id
#                 else:
#                     emoticon = None
#                 details_reactions.append((emoticon, count))
#         else : 
#             count = 0
            
#         ##########################################
#         # FORWARDS
#         ##########################################
        
#         if message.fwd_from  :
#             fwd_from = message.fwd_from  
#             if fwd_from.date:
#                 fwd_from_date = fwd_from.date
#             else : 
#                 fwd_from_date = datetime(1970,1,1)
#             if fwd_from.from_id:
#                 fwd_from_id = fwd_from.from_id
#                 if isinstance(fwd_from_id, PeerUser):
#                     fwd_from_channel_id = fwd_from_id.user_id
#                 elif isinstance(fwd_from_id, PeerChannel):
#                     fwd_from_channel_id = fwd_from_id.channel_id
#                 else:
#                     fwd_from_channel_id = None
#                     print(fwd_from_id, "type not implemented")
#             else : 
#                 fwd_from_channel_id = None
#             if fwd_from.from_name:
#                 fwd_from_name = fwd_from.from_name
#             else:
#                 fwd_from_name = ''
#             if fwd_from.channel_post:
#                 fwd_from_channel_post = str(fwd_from.channel_post)
#             else:
#                 fwd_from_channel_post = ''
#             if fwd_from.post_author:
#                 fwd_from_post_author = fwd_from.post_author
#             else:
#                 fwd_from_post_author=''
#         else : 
#             fwd_from_date, fwd_from_id, fwd_from_channel_id, fwd_from_name, fwd_from_channel_post, fwd_from_post_author = datetime(1970,1,1), '', '', '', '', ''

#         ##########################################
#         # REPLIES
#         ##########################################
        
#         if message.reply_to:
#             reply_to = message.reply_to    
#             if reply_to.quote:
#                 reply_to_quote = reply_to.quote
#             else:
#                 reply_to_quote=False
#             if reply_to.reply_to_msg_id:
#                 reply_to_msg_id = str(reply_to.reply_to_msg_id)
#             else:
#                 reply_to_msg_id = ''
#             if reply_to.reply_to_peer_id:
#                 reply_to_peer_id = str(reply_to.reply_to_peer_id)
#             else:
#                 reply_to_peer_id = ''
#             # reply_from = reply_to.reply_from
#             # reply_media = reply_to.reply_media
#             if reply_to.reply_to_top_id:
#                 reply_to_top_id = str(reply_to.reply_to_top_id)
#             else:
#                 reply_to_top_id = ''
#             if reply_to.quote_text:
#                 reply_to_quote_text = reply_to.quote_text
#             else:
#                 reply_to_quote_text = ''
#         else:
#             reply_to_quote, reply_to_msg_id, reply_to_peer_id, reply_to_top_id, reply_to_quote_text = False, '', '', '', ''

#         ##########################################
#         # FILE
#         ##########################################
#         if message.file:
#             file = message.file
#             if file.id:
#                 file_id = file.id
#             else:
#                 file_id = ''
#             if file.duration:
#                 file_duration = file.duration
#             else:
#                 file_duration = 0
#             if file.emoji:
#                 file_emoji = file.emoji
#             else:
#                 file_emoji = ''
#             if file.ext:
#                 file_ext = file.ext
#             else:
#                 file_ext = ''
#             if file.height:
#                 file_height = int(file.height)
#             else:
#                 file_height = 0
#             if file.mime_type:
#                 file_mime_type = file.mime_type
#             else:
#                 file_mime_type = ''
#             if file.name:
#                 file_name = file.name
#             else:
#                 file_name = ''
#             if file.performer:
#                 file_performer = file.performer
#             else:
#                 file_performer = ''
#             if file.size:
#                 file_size = file.size
#             else:
#                 file_size = 0
#             if file.sticker_set:
#                 file_sticker_set = file.sticker_set
#             else:
#                 file_sticker_set = ''
#             if file.title:
#                 file_title = file.title
#             else :
#                 file_title = ''
#             if file.width:
#                 file_width = int(file.width)
#             else:
#                 file_width = 0
#         else :
#             file_id, file_duration, file_emoji, file_ext, file_height, file_mime_type, file_name, file_performer, file_size, file_sticker_set, file_title, file_width = "", 0, '', '', 0, '', '', '', 0, '', '', 0



#         webpage_record = parse_webpage(message.web_preview)
  
#         current_record = (uniq_id, channel_id, message_id, message_date, text, is_reply, views, forwards, replies_count, replies_channel_id, total_reactions, details_reactions,
#                         fwd_from_date, fwd_from_channel_id,fwd_from_name, fwd_from_channel_post,fwd_from_post_author, 
#                         reply_to_quote, reply_to_msg_id, reply_to_peer_id, reply_to_top_id, reply_to_quote_text,
#                         file_id, file_duration, file_ext, file_height, file_mime_type, file_name, file_size, file_title, file_width)
#         current_record = current_record + webpage_record 

#         all_records.append(current_record)
#     df = pd.DataFrame.from_records(all_records, columns = ['uniq_id', 'channel_id', "message_id", "message_date", "text", "is_reply", "views", "forwards", "replies_count", "replies_channel_id", "total_reactions", "details_reactions",
#                                                             "fwd_from_date", "fwd_from_channel_id","fwd_from_name", "fwd_from_channel_post","fwd_from_post_author", 
#                                                             "reply_to_quote", "reply_to_msg_id", "reply_to_peer_id", "reply_to_top_id", "reply_to_quote_text",
#                                                             "file_id", "file_duration", "file_ext", "file_height", "file_mime_type", "file_name", "file_size", "file_title", "file_width",
#                                                             "webpage_id", "webpage_url", "webpage_type", "webpage_site_name", "webpage_title", "webpage_description", "webpage_embed_url", "webpage_embed_type", "webpage_embed_width", "webpage_embed_height",
#                                                             "webpage_duration", "webpage_author", "webpage_photo_id", "webpage_photo_date"

#                                                            ])
#     return df


# def parse_webpage(webpage):
#     """
#     Parse the given webpage object and extract relevant information.

#     Args:
#         webpage (Webpage): The webpage object to be parsed.

#     Returns:
#         tuple: A tuple containing the parsed information from the webpage.
#                The tuple contains the following elements:
#                - webpage_id (str): The ID of the webpage.
#                - webpage_url (str): The URL of the webpage.
#                - webpage_type (str): The type of the webpage.
#                - webpage_site_name (str): The name of the site.
#                - webpage_title (str): The title of the webpage.
#                - webpage_description (str): The description of the webpage.
#                - webpage_embed_url (str): The embed URL of the webpage.
#                - webpage_embed_type (str): The embed type of the webpage.
#                - webpage_embed_width (int): The embed width of the webpage.
#                - webpage_embed_height (int): The embed height of the webpage.
#                - webpage_duration (int): The duration of the webpage.
#                - webpage_author (str): The author of the webpage.
#                - webpage_photo_record (tuple): A tuple containing the parsed photo information from the webpage.
#     """
    
#     if webpage : 
#         if webpage.id:
#             webpage_id = str(webpage.id)
#         else:
#             webpage_id = ''
#         if webpage.url:
#             webpage_url = webpage.url
#         else:
#             webpage_url = ''
#         # if webpage.display_url:
#         #     webpage_display_url = webpage.display_url
#         # else:
#         #     webpage_display_url = ''
#         # # webpage_hash = webpage.hash
#         # if webpage.has_large_media:
#         #     webpage_has_large_media = webpage.has_large_media
#         # else:
#         #     webpage_has_large_media = False
#         if webpage.type:
#             webpage_type = webpage.type
#         else:
#             webpage_type = ''
#         if webpage.site_name:
#             webpage_site_name = webpage.site_name
#         else:
#             webpage_site_name = ''
#         if webpage.title:
#             webpage_title = webpage.title
#         else:
#             webpage_title = ''
#         if webpage.description:
#             webpage_description = webpage.description
#         else:
#             webpage_description = ''
#         if webpage.embed_url:
#             webpage_embed_url = webpage.embed_url
#         else:
#             webpage_embed_url = ''
#         if webpage.embed_type:
#             webpage_embed_type = webpage.embed_type
#         else:
#             webpage_embed_type = ''
#         if webpage.embed_width:
#             webpage_embed_width = int(webpage.embed_width)
#         else:
#             webpage_embed_width = 0
#         if webpage.embed_height:
#             webpage_embed_height = int(webpage.embed_height)
#         else:
#             webpage_embed_height = 0
#         if webpage.duration:
#             webpage_duration = int(webpage.duration)
#         else:
#             webpage_duration = 0
#         if webpage.author :
#             webpage_author = webpage.author
#         else :
#             webpage_author = ''
            
#         webpage_photo_record = parse_photo(webpage.photo)
#         # webpage_document = webpage.document
#         # webpage_cached_page = webpage.cached_page
#         # webpage_attributes = webpage.attributes
#     else : 
#         webpage_id, webpage_url, webpage_type, webpage_site_name, webpage_title, webpage_description, webpage_embed_url, webpage_embed_type, webpage_embed_width, webpage_embed_height, webpage_duration, webpage_author, webpage_photo_record = "", "", "", "", "", "", "", "", 0, 0, 0, "", ('', datetime(1970,1,1))        
#     record = (webpage_id, webpage_url, webpage_type, webpage_site_name, webpage_title, webpage_description, webpage_embed_url, webpage_embed_type, webpage_embed_width, webpage_embed_height, webpage_duration, webpage_author) + webpage_photo_record
#     return record

# def parse_photo(photo):
#     """
#     Parses the given photo object and returns a tuple containing the photo ID and date.
    
#     Args:
#         photo: The photo object to be parsed.
        
#     Returns:
#         A tuple containing the photo ID and date.
#     """
    
#     if photo:
#         if photo.id:
#             photo_id = str(photo.id)
#         else:
#              photo.id = ''
#         if photo.date:
#             photo_date = photo.date
#         else : 
#             photo_date = datetime(1970,1,1)
        
#         # photo_access_hash = photo.access_hash
#         # photo_file_reference = photo.file_reference
#         # photo_dc_id = photo.dc_id
#         # photo_sizes = photo.sizes #### A PARSER
#     else : 
#         photo_id, photo_date = '', datetime(1970,1,1)
    
#     record = (photo_id, photo_date)
#     return record


# async def get_messages_by_date(client, phone_number, channel_username, dl_files=False, reverse=True, limit=None, offset_date=datetime(1970,1,1), path_file="files"):
#     """
#     Retrieves messages from a Telegram channel by date.

#     Args:
#         client (TelegramClient): The Telegram client instance.
#         phone_number (str): The phone number associated with the Telegram account.
#         channel_username (str): The username of the channel to retrieve messages from.
#         dl_files (bool, optional): Whether to download media files attached to the messages. Defaults to False.
#         reverse (bool, optional): Whether to retrieve messages in reverse order. Defaults to True.
#         limit (int, optional): The maximum number of messages to retrieve. Defaults to None (retrieve all messages).
#         offset_date (datetime, optional): The starting date to retrieve messages from. Defaults to datetime(1970,1,1).
#         path_file (str, optional): The path to save the downloaded files. Defaults to "files".

#     Returns:
#         list: A list of messages retrieved from the channel.

#     Raises:
#         Exception: If there is an error during the retrieval process.

#     """
#     try:
#         await client.start(phone_number)

#         current_path_file = create_dir(os.path.join(path_file, "messages"))

#         if dl_files:
#             current_path_img = create_dir(os.path.join(path_file, "img", str(channel_username)))

#         # Get the message history
#         messages = []

#         async for message in client.iter_messages(channel_username,
#                                                   limit=limit,
#                                                   offset_date=offset_date,
#                                                   reverse=reverse):
#             messages.append(message)

#             if dl_files:
#                 if message.peer_id:
#                     channel_id = str(message.peer_id.channel_id)
#                 else:
#                     channel_id=''
#                 if message.id:
#                     message_id = str(message.id)
#                 else:
#                     message_id=''
#                 if message.file:
#                     file_id = str(message.file.id)
#                 else:
#                     file_id=''
#                 await message.download_media(file=os.path.join(current_path_img, channel_id+"_"+message_id+"_"+file_id))

#         df_messages = parse_telegram_messages(messages)
#         write_pickle(df_messages, current_path_file, str(channel_username))

#         return messages
#     finally:
#         # Disconnect the client
#         await client.disconnect()

# async def get_channel_info(api_id : int, api_hash : str, phone_number : str, channel_username : str, path_img :str) -> dict:
#     """
#     Retrieves information about a Telegram channel.

#     Args:
#         api_id (int): The API ID of the Telegram application.
#         api_hash (str): The API hash of the Telegram application.
#         phone_number (str): The phone number associated with the Telegram account.
#         channel_username (str): The username of the channel.

#     Returns:
#         dict: A dictionary containing the full information of the channel.

#     Raises:
#         Exception: If there is an error during the retrieval of channel information.
#     """
#     client = TelegramClient('session_name', api_id, api_hash)
#     try:
#         await client.start(phone_number)
#         channel_full_info = await client(GetFullChannelRequest(channel=channel_username))
#         channel_full_info_json = channel_full_info.to_dict()
#         img_path = await client.download_profile_photo(channel_full_info.chats[0], download_big=False, file = path_img)
#     finally:
#         # Disconnect the client
#         await client.disconnect()

#     return channel_full_info_json


# async def get_channel_info(api_id : int, api_hash : str, phone_number : str, channel_username : str, path_project :str, DL_profile_pic : bool = False) -> dict:
#     """
#     Retrieves information about a Telegram channel.

#     Args:
#         api_id (int): The API ID of the Telegram application.
#         api_hash (str): The API hash of the Telegram application.
#         phone_number (str): The phone number associated with the Telegram account.
#         channel_username (str): The username of the channel.

#     Returns:
#         dict: A dictionary containing the full information of the channel.

#     Raises:
#         Exception: If there is an error during the retrieval of channel information.
#     """
#     client = TelegramClient('session_name', api_id, api_hash)
#     path_img = create_dir(os.path.join(path_project, "THUMBNAILS"))
#     path_json = create_dir(os.path.join(path_project, "JSON"))
    
#     try:
#         await client.start(phone_number)
#         try:
#             channel_full_info = await client(GetFullChannelRequest(channel=channel_username))

#             if channel_full_info:
#                 channel_full_info_dict = channel_full_info.to_dict()
#                 channel_full_info_json = JSONEncoder().encode(channel_full_info_dict)
#             else:
#                 channel_full_info_dict = {'_': 'Channel', 'id': channel_username, 'title':'private_channel'}
#             write_json(channel_full_info_json, path_json, f"{str(channel_username)}")

#             if DL_profile_pic:
#                 img_path = await client.download_profile_photo(channel_full_info.chats[0], download_big=False, file = path_img)

#         except Exception as e:
#             pass
#             print(channel_username, e)
#     finally:
#         # Disconnect the client
#         await client.disconnect()

#     return channel_full_info_dict

def dump_json(json_dict: dict, path: str, name: str) -> str:
    """
    Write a dictionary to a JSON file.

    Args:
        json_dict (dict): The dictionary to be written to the JSON file.
        path (str): The directory path where the JSON file will be saved.
        name (str): The name of the JSON file (without the extension).

    Returns:
        str: The full path to the saved JSON file.
    """
    file_path = os.path.join(path, name + '.json')
    with open(file_path, 'w') as outfile:
        json.dump(json_dict, outfile, cls=JSONEncoder)
    return file_path

async def get_channel_info(api_id: int, api_hash: str, phone_number: str, channel_username: str, path_project: str, DL_profile_pic: bool = False) -> dict:
    """
    Retrieves information about a Telegram channel.

    Args:
        api_id (int): The API ID of the Telegram application.
        api_hash (str): The API hash of the Telegram application.
        phone_number (str): The phone number associated with the Telegram account.
        channel_username (str): The username of the channel.

    Returns:
        dict: A dictionary containing the full information of the channel.

    Raises:
        Exception: If there is an error during the retrieval of channel information.
    """
    client = TelegramClient('session_name', api_id, api_hash)
    path_img = create_dir(os.path.join(path_project, "THUMBNAILS"))
    path_json = create_dir(os.path.join(path_project, "JSON"))

    try:
        await client.start(phone_number)
        try:
            # Fetch full channel info
            channel_full_info = await client(GetFullChannelRequest(channel=channel_username))

            # If channel info is retrieved
            if channel_full_info:
                channel_full_info_dict = channel_full_info.to_dict()
            else:
                channel_full_info_dict = {'_': 'ChatFull',
                                      'full_chat': {'_': 'ChannelFull',
                                                    'id': channel_username,
                                                    },
                                        'chats': [{'_': 'Channel', 'id': channel_username, 'title': 'private'}]
                                    }

            # Save the dictionary as JSON (no need to pre-encode it to a string)
            dump_json(channel_full_info_dict, path_json, f"{str(channel_username)}")

            # Optionally download profile picture
            if DL_profile_pic:
                img_path = await client.download_profile_photo(channel_full_info.chats[0], download_big=False, file=path_img)

        except Exception as e:
            print(channel_username, e)
            channel_full_info_dict = {'_': 'ChatFull',
                                      'full_chat': {'_': 'ChannelFull',
                                                    'id': channel_username,
                                                    },
                                        'chats': [{'_': 'Channel', 'id': channel_username, 'title': 'private'}]
                                    }
            dump_json(channel_full_info_dict, path_json, f"{str(channel_username)}")
            return {'_': 'Channel', 'id': channel_username, 'title': 'private_channel'}

    finally:
        # Disconnect the client
        await client.disconnect()

    return channel_full_info_dict

def parse_channel(channel : dict) -> pd.DataFrame:
    """
    Parses the given channel data and returns a DataFrame with the parsed information.

    Args:
        channel (dict): The channel data to be parsed.

    Returns:
        pandas.DataFrame: A DataFrame containing the parsed channel information.

    """
    reactions=[]
    channel_title = ''
    creation_date = datetime(1970,1,1)
    fc = channel.get("full_chat", {})
    channel_id = fc.get("id", "")
    channel_about = fc.get("about", "")
    channel_participants = int(fc.get("participants_count",0))
    linked_chat_id = fc.get("linked_chat_id", "")
    
    ar = fc.get("available_reactions", {})
    if ar:
        reaction = ar.get('reactions', [])
        for r in reaction:
            if r.get('_') == "ReactionEmoji":
                reactions.append(r.get("emoticon"))
            elif r.get('_') == "ReactionCustomEmoji":
                reactions.append(r.get("document_id"))
            else:
                print("Not implemented type", r)
        
    chats = channel.get("chats", [])
    if chats:
        for chat in chats:
            if chat.get("_") == "Channel":
                if chat.get("id") == channel_id:
                    creation_date = chat.get("date", datetime(1970,1,1))
                    channel_title = chat.get("title", "")
                    break
            else:
                print("Not implemented type", chat.get("_"))
    else:
        creation_date = datetime(1970,1,1)
        channel_title = ''


    fc_record = (str(channel_id), channel_title, channel_about, channel_participants, linked_chat_id, reactions, creation_date)

    df = pd.DataFrame.from_records([fc_record], columns = ['channel_id', 'channel_title', 'channel_about', 'channel_participants', "linked_chat_id", 'reactions', 'creation_date'])
    return df