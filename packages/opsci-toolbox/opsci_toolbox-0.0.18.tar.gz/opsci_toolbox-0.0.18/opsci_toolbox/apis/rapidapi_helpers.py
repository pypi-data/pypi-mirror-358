import requests
import pandas as pd
from tqdm import tqdm
import re
from datetime import datetime,timedelta
from opsci_toolbox.helpers.dates import str_to_datetime
from opsci_toolbox.helpers.common import write_jsonl

def create_queries_per_period(
    query: dict, 
    publishedAfter: str, 
    publishedBefore: str, 
    col_publishedAfter: str = "start_date", 
    col_publishedBefore: str = "end_date", 
    date_format: str = '%Y-%m-%d', 
    rolling_days: int = 7
) -> list:
    """
    Generates a list of query dictionaries with date ranges for a rolling period.

    Args:
        query (dict): The base query dictionary to be modified with date ranges.
        publishedAfter (str): The start date in string format.
        publishedBefore (str): The end date in string format.
        col_publishedAfter (str, optional): The key name for the start date in the query dictionary. Defaults to "start_date".
        col_publishedBefore (str, optional): The key name for the end date in the query dictionary. Defaults to "end_date".
        date_format (str, optional): The format of the input date strings. Defaults to '%Y-%m-%d'.
        rolling_days (int, optional): The number of days for each rolling period. Defaults to 7.

    Returns:
        list: A list of query dictionaries with updated date ranges.
    """
    datetime_publishedAfter = datetime.strptime(publishedAfter, date_format)
    datetime_publishedBefore = datetime.strptime(publishedBefore, date_format)
    
    queries = []

    end = datetime_publishedBefore 

    while end > datetime_publishedAfter:
        
        start = end - timedelta(days=rolling_days)
        # print(end_date, start_date)
        if start < datetime_publishedAfter :
            start = datetime_publishedAfter

        query_copy = query.copy()
        start_str = start.strftime(date_format)
        end_str = end.strftime(date_format)
        query_copy[col_publishedAfter] = start_str
        query_copy[col_publishedBefore] = end_str
        
        queries.append(query_copy)
        end = start
    
    return queries


def remove_extra_spaces(text: str) -> str:
    """
    Removes extra spaces from the input text, including leading and trailing spaces.

    Args:
        text (str): The input text from which extra spaces should be removed.

    Returns:
        str: The cleaned text with extra spaces removed.
    """
    cleaned_text = re.sub(r'\s+', ' ', text)
    return cleaned_text.strip()


def query_rapidAPI(url: str, query_dict: dict, host: str)-> requests.Response:
    """
    Function to query RapidAPI.

    Args:
        url (str): The URL for the RapidAPI endpoint.
        query_dict (dict): A dictionary containing query parameters.
        host (str): The RapidAPI host.

    Returns:
        requests.Response: The response object from the RapidAPI request, or None if an error occurs.
    """

    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": "0a9e6c6285msh97d69db920dc8dcp1d9cadjsndd16a1cfb894",
        "X-RapidAPI-Host": host
    }

    try:
        response = requests.get(url, headers=headers, params=query_dict)
    except Exception as e:
        pass
        print(e)

    return response


def response_header(response: requests.Response) -> dict:
    """
    Retrieves the headers from an HTTP response object.

    Args:
        response: The HTTP response object from which headers are to be retrieved.

    Returns:
        dict: The headers of the HTTP response.
    """
    return response.headers

##################################################################################################
# TWITTER API - PARSING
# https://rapidapi.com/omarmhaimdat/api/twitter154
##################################################################################################

def parse_user(user: dict) -> tuple:
    """
    Parse the subdict related to user data.

    Args:
        user (dict): Dictionary containing user data.

    Returns:
        tuple: A tuple containing parsed user data fields.
    """
    if user:
        user_creation_date=user.get("creation_date","")
        user_creation_date=str_to_datetime(user_creation_date, format = '%a %b %d %H:%M:%S %z %Y')
        user_id=user.get("user_id","")
        user_username=user.get("username","")
        user_name=user.get("name","")
        user_follower_count=user.get("follower_count",0)
        user_following_count=user.get("following_count",0)
        user_favourites_count=user.get("favourites_count",0)
        user_is_private=user.get("is_private",False)
        user_is_verified=user.get("is_verified",False)
        user_is_blue_verified=user.get("is_blue_verified",False)
        user_location=user.get("location","")
        user_profile_pic_url=user.get("profile_pic_url","")
        user_profile_banner_url=user.get("profile_banner_url","")
        user_description=user.get("description","")
        user_description= remove_extra_spaces(user_description)
        user_external_url=user.get("external_url","")
        user_number_of_tweets=user.get("number_of_tweets",0)
        user_bot=user.get("bot",False)
        user_timestamp=user.get("timestamp",0)
        user_has_nft_avatar=user.get("has_nft_avatar",False)
        user_category=user.get("category","")
        user_default_profile=user.get("default_profile",False)
        user_default_profile_image=user.get("default_profile_image",False)
        user_listed_count=user.get("listed_count",0)
        user_verified_type=user.get("verified_type","")
    else : 
        user_creation_date = user_id = user_username = user_name = user_location = user_profile_pic_url = user_profile_banner_url = user_description = user_external_url = user_category = user_verified_type = ""
        user_follower_count = user_following_count = user_favourites_count = user_number_of_tweets = user_timestamp = user_listed_count = 0
        user_is_private = user_is_verified = user_is_blue_verified = user_bot = user_has_nft_avatar = user_default_profile = user_default_profile_image = False

    record = (user_creation_date, user_id, user_username, user_name, user_follower_count, user_following_count, user_favourites_count, user_is_private, user_is_verified, user_is_blue_verified, user_location, user_profile_pic_url, user_profile_banner_url, user_description, user_external_url, user_number_of_tweets, user_bot, user_timestamp, user_has_nft_avatar,user_category, user_default_profile, user_default_profile_image, user_listed_count, user_verified_type)
    return record

def parse_retweet(data: dict) -> tuple:
    """
    Parse subdict related to original tweet if the captured tweet is RT.

    Args:
        data (dict): Dictionary containing tweet data.

    Returns:
        tuple: A tuple containing parsed tweet data fields.
    """
    if data:
        tweet_id=data.get("tweet_id", "")
        creation_date = data.get("creation_date", "")
        creation_date = str_to_datetime(creation_date, format = '%a %b %d %H:%M:%S %z %Y')
        text=data.get("text", "")
        text= remove_extra_spaces(text)
        media_url=data.get("media_url", "")
        video_url=data.get("video_url", "")
        language=data.get("language", "")
        favorite_count=data.get("favorite_count", 0)
        retweet_count=data.get("retweet_count", 0)
        reply_count=data.get("reply_count", 0)
        quote_count=data.get("quote_count", 0)
        retweet=data.get("retweet", False)
        views=data.get("views", 0)
        timestamp=data.get("timestamp", 0)
        video_view_count=data.get("video_view_count", 0)
        in_reply_to_status_id=data.get("in_reply_to_status_id", "")
        quoted_status_id=data.get("quoted_status_id", "")
        # binding_values=data.get("binding_values", "")
        expanded_url=data.get("expanded_url", "")
        retweet_tweet_id=data.get("retweet_tweet_id", "")
        conversation_id=data.get("conversation_id", "")
        # retweet_status=data.get("retweet_status", "")
        # quoted_status=data.get("quoted_status", "")
        bookmark_count=data.get("bookmark_count", 0)
        source=data.get("source", "")
        community_note=data.get("community_note", "")
    else : 
        tweet_id= text= media_url= video_url= language= in_reply_to_status_id= quoted_status_id= expanded_url= retweet_tweet_id= conversation_id= source= community_note = ""
        # binding_values
        retweet=False
        favorite_count= retweet_count= reply_count= quote_count= views= video_view_count= timestamp= bookmark_count = 0
        creation_date=datetime(1900,1,1,00,00,00)
    record=(tweet_id, creation_date, text,media_url, video_url, language, favorite_count, retweet_count, reply_count, quote_count, retweet, views, timestamp, video_view_count,in_reply_to_status_id, quoted_status_id, expanded_url, retweet_tweet_id,conversation_id,bookmark_count, source,community_note)
    return record

def parse_entities(extended_entities: dict) -> tuple:
    """
    Parse the subdict related to extended entities (image, video, tags...).

    Args:
        extended_entities (dict): Dictionary containing extended entities data.

    Returns:
        tuple: A tuple containing parsed extended entities data fields.
    """
    id_str, indices, media_key, media_url, media_type, original_info, height, width, ext_alt_text, monetizable, aspect_ratio, duration_millis = [], [], [], [], [], [], [], [], [], [], [], []
    all_x, all_y, all_h, all_w =[], [], [], []
    all_tag_user_id, all_tag_user_screenname, all_tag_user_type=[], [], []
    all_variants_url, all_variants_bitrate, all_variants_content_type =[], [], []

    if extended_entities:
        media_list = extended_entities.get('media', [])
        if len(media_list)>0:
            for media_item in media_list:
                id_str.append(media_item.get("id_str", ""))
                indices.append(media_item.get("indices", []))
                media_key.append(media_item.get("media_key", ""))
                media_url.append(media_item.get("media_url_https", ""))
                media_type.append(media_item.get("type", ""))
                ext_alt_text.append(media_item.get("ext_alt_text", ""))

                monetizable.append(media_item.get("additional_media_info",{}).get("monetizable", False))
                aspect_ratio.append(media_item.get("video_info",{}).get("aspect_ratio", []))
                duration_millis.append(media_item.get("video_info",{}).get("duration_millis", 0))

                variants = media_item.get("variants",[])
                variants_url, variants_bitrate, variants_content_type = [], [], []
                if len(variants)>0:
                    variants_url= [variant.get('url',"") for variant in variants]
                    variants_bitrate = [variant.get("bitrate", 0) for variant in variants]
                    variants_content_type = [variant.get("content_type", "") for variant in variants]
                all_variants_url.append(variants_url)
                all_variants_bitrate.append(variants_bitrate)
                all_variants_content_type.append(variants_content_type)

                # Extract sizes information
                x, y, h, w = [], [], [], []
                tag_user_id, tag_user_screenname, tag_user_type = [], [], []
                features = media_item.get("features")
                if features : 
                    features_large = features.get("large")
                    if features_large :
                        faces = features_large.get("faces", [])
                        if len(faces)>0:
                            x = [face.get("x",0) for face in faces]
                            y = [face.get("y",0) for face in faces]
                            h = [face.get("h",0) for face in faces]
                            w = [face.get("w",0) for face in faces]

                    features_all = features.get("all")
                    if features_all : 
                        tags = features_all.get("tags")
                        if tags :
                            tag_user_id = [tag.get("user_id","") for tag in tags]
                            tag_user_screenname = [tag.get("screen_name","") for tag in tags]
                            tag_user_type = [tag.get("type","") for tag in tags]
                            
                all_x.append(x)
                all_y.append(y)
                all_h.append(h)
                all_w.append(w)
                all_tag_user_id.append(tag_user_id)
                all_tag_user_screenname.append(tag_user_screenname)
                all_tag_user_type.append(tag_user_type)

                # Extract original_info
                original_info = media_item.get("original_info", {})
                height = original_info.get("height", 0)
                width = original_info.get("width", 0)
    
    record = (id_str, indices, media_key, media_url, media_type, all_x, all_y, all_h, all_w, height, width, ext_alt_text, all_tag_user_id, all_tag_user_screenname, all_tag_user_type, monetizable, aspect_ratio, duration_millis, all_variants_url, all_variants_bitrate, all_variants_content_type)
    return record

def parse_tweet(json_data: list) -> pd.DataFrame:
    """
    Parse a batch of tweets.

    Args:
        json_data (list): List of dictionaries containing tweet data.

    Returns:
        pd.DataFrame: A pandas DataFrame containing parsed tweet data.
    """
    all_records=[]
    for data in json_data:
        tweet_id=data.get("tweet_id", "")
        creation_date = data.get("creation_date", "")
        creation_date = str_to_datetime(creation_date, format = '%a %b %d %H:%M:%S %z %Y')
        text=data.get("text", "")
        text= remove_extra_spaces(text)
        media_url=data.get("media_url", "")
        video_url=data.get("video_url", "")
        language=data.get("language", "")
        favorite_count=data.get("favorite_count", 0)
        retweet_count=data.get("retweet_count", 0)
        reply_count=data.get("reply_count", 0)
        quote_count=data.get("quote_count", 0)
        retweet=data.get("retweet", False)
        views=data.get("views", 0)
        timestamp=data.get("timestamp", 0)
        video_view_count=data.get("video_view_count", 0)
        in_reply_to_status_id=data.get("in_reply_to_status_id", "")
        quoted_status_id=data.get("quoted_status_id", "")
        # binding_values=data.get("binding_values", "")
        expanded_url=data.get("expanded_url", "")
        retweet_tweet_id=data.get("retweet_tweet_id", "")
        conversation_id=data.get("conversation_id", "")
        # quoted_status=data.get("quoted_status", "")
        bookmark_count=data.get("bookmark_count", 0)
        source=data.get("source", "")
        community_note=data.get("community_note", "")

        # on parse les données du user
        user=data.get("user")
        user_record = parse_user(user)

        #on parse les données de retweet
        retweet_status=data.get("retweet_status", "")
        retweet_record = parse_retweet(retweet_status)
        #on parse les données d'entitées
        extended_entities=data.get("extended_entities", "")
        entities_record = parse_entities(extended_entities)

        record = (tweet_id, creation_date, text, media_url, video_url, language, favorite_count, retweet_count, reply_count, quote_count, retweet, views, timestamp, video_view_count, in_reply_to_status_id, quoted_status_id, expanded_url, retweet_tweet_id, conversation_id, bookmark_count, source, community_note) 
        record = record + user_record + retweet_record + entities_record
        all_records.append(record)

    cols_tweet = ["tweet_id", "creation_date", "text", "media_url", "video_url", "language", "favorite_count", "retweet_count", "reply_count", "quote_count", "retweet", "views", "timestamp", "video_view_count", "in_reply_to_status_id", "quoted_status_id", "expanded_url", "retweet_tweet_id", "conversation_id", "bookmark_count", "source", "community_note"]
    cols_user = ["user_creation_date", "user_id", "user_username", "user_name", "user_follower_count", "user_following_count", "user_favourites_count", "user_is_private", "user_is_verified", "user_is_blue_verified", "user_location", "user_profile_pic_url", "user_profile_banner_url", "user_description", "user_external_url", "user_number_of_tweets", "user_bot", "user_timestamp", "user_has_nft_avatar", "user_category", "user_default_profile", "user_default_profile_image", "user_listed_count", "user_verified_type"]
    cols_rt = ["rt_tweet_id", "rt_creation_date", "rt_text", "rt_media_url", "rt_video_url", "rt_language", "rt_favorite_count", "rt_retweet_count", "rt_reply_count", "rt_quote_count", "rt_retweet", "rt_views", "rt_timestamp", "rt_video_view_count", "rt_in_reply_to_status_id", "rt_quoted_status_id", "rt_expanded_url", "rt_retweet_tweet_id", "rt_conversation_id", "rt_bookmark_count", "rt_source", "rt_community_note"]
    cols_entities = ["entities_id_str", "entities_indices", "entities_media_key", "entities_media_url", "entities_media_type", "entities_x", "entities_y", "entities_h", "entities_w", "entities_height", "entities_width", "entities_ext_alt_text", "entities_tag_user_id", "entities_tag_user_screenname", "entities_tag_user_type", "entities_monetizable", "entities_aspect_ratio", "entities_duration_millis", "entities_all_variants_url", "entities_all_variants_bitrate", "entities_all_variants_content_type"]
    all_cols = cols_tweet + cols_user + cols_rt + cols_entities

    df = pd.DataFrame.from_records(all_records, columns = all_cols)
    return df

def parse_twitter_list_details(json_data : dict) -> pd.DataFrame:
    """
    Parse list results from https://rapidapi.com/omarmhaimdat/api/twitter154.

    Args:
        json_data (dict): Dictionary containing list details data.

    Returns:
        pd.DataFrame: A pandas DataFrame containing parsed list details.
    """
    list_id = json_data.get("list_id", "")
    list_id_str = json_data.get("list_id_str", "")
    member_count = json_data.get("member_count", 0)
    name = json_data.get("name", "")
    suscriber_count = json_data.get("subscriber_count", 0)
    creation_date = json_data.get("creation_date", 0)
    mode = json_data.get("mode", "0")

    user_record = parse_user(json_data.get("user", {}))
    record = (list_id, list_id_str, member_count, name, suscriber_count, creation_date, mode) + user_record
    cols = ["list_id", "list_id_str", "member_count", "name", "suscriber_count", "creation_date", "mode", "user_creation_date", "user_id", "user_username", "user_name", "user_follower_count", "user_following_count", "user_favourites_count", "user_is_private", "user_is_verified", "user_is_blue_verified", "user_location", "user_profile_pic_url", "user_profile_banner_url", "user_description", "user_external_url", "user_number_of_tweets", "user_bot", "user_timestamp", "user_has_nft_avatar", "user_category", "user_default_profile", "user_default_profile_image", "user_listed_count", "user_verified_type"]

    df = pd.DataFrame.from_records(record, cols)
    return df

######################################################################################
# function to parse Instagram data
# https://rapidapi.com/JoTucker/api/instagram-scraper2
# https://instagram-scraper2.p.rapidapi.com/hash_tag_medias_v2
######################################################################################

def instagram_parse_hashtag_data(hashtag_data: dict)-> pd.DataFrame:
    """
    Parse Instagram hashtag data into a DataFrame.

    Args:
        hashtag_data (dict): Dictionary containing Instagram hashtag data.

    Returns:
        pd.DataFrame: A pandas DataFrame containing parsed hashtag data.
    """
    hashtag_id =  hashtag_data.get("id") 
    hashtag_name =  hashtag_data.get("name") 
    allow_following =  hashtag_data.get("allow_following")
    is_following =  hashtag_data.get("is_following")
    is_top_media_only =  hashtag_data.get("is_top_media_only")
    profile_pic_url =  hashtag_data.get("profile_pic_url")

    count =  hashtag_data.get("edge_hashtag_to_ranked_media", {}).get("count", 0)

    edges=  hashtag_data.get("edge_hashtag_to_ranked_media", {}).get("edges", [])

    all_records = []
    for edge in edges : 
        node = edge.get('node', {})
        comments_disabled = node.get("comments_disabled")
        type_content = node.get("__typename")
        node_id = node.get("id")
        shortcode = node.get("shortcode")
        comment = node.get("edge_media_to_comment", {}).get("count", 0)
        taken_at_timestamp = node.get("taken_at_timestamp")
        width = node.get("dimensions", {}).get("width", 0)
        height = node.get("dimensions", {}).get("height", 0)
        display_url = node.get("display_url")
        likes =node.get("edge_liked_by", {}).get("count",0)
        preview_likes =node.get("edge_media_preview_like", {}).get("count",0)
        owner_id =node.get("owner", {}).get("id", None)
        thumbnail_src = node.get("thumbnail_src")
        is_video = node.get("is_video")
        video_view_count = node.get("video_view_count",0)
        accessibility_caption = node.get("accessibility_caption")
        edge_media_to_caption=node.get("edge_media_to_caption", {}).get("edges", [])
        if len(edge_media_to_caption)>0:
            text = edge_media_to_caption[0].get("node", {}).get("text")
        else:
            text = ''

        text = remove_extra_spaces(text)

        record = (node_id, shortcode, taken_at_timestamp, owner_id, text, accessibility_caption, type_content, comment, likes, preview_likes, video_view_count, display_url, width, height, thumbnail_src, is_video, comments_disabled, hashtag_id, hashtag_name, allow_following, is_following, is_top_media_only, profile_pic_url, count)
        all_records.append(record)

    df = pd.DataFrame.from_records(all_records, columns = ["post_id", "shortcode", "taken_at_timestamp", "owner_id", "text", "accessibility_caption", "type_content", "comment", "likes", "preview_likes", "video_view_count", "display_url", "width", "height", "thumbnail_src", "is_video", "comments_disabled", "hashtag_id", "hashtag_name", "allow_following", "is_following", "is_top_media_only", "profile_pic_url", "count"])
    return df


######################################################################################
# function to parse Twitter data
# https://rapidapi.com/twttrapi-twttrapi-default/api/twttrapi
######################################################################################
def compile_list_entries(json_data: dict, path_json: str, filename: str)-> tuple:
    """
    Function to process list entries from Twitter API response and write to JSONL file. https://twttrapi.p.rapidapi.com/list-members

    Args:
        json_data (dict): JSON response data from Twitter API.
        path_json (str): Path to directory where JSONL file will be saved.
        filename (str): Name of the JSONL file.

    Returns:
        tuple: A tuple containing a list of results (user legacy data) and next cursor (str or None).
    """
    results = []
    next_cursor = None
    entries = json_data.get('data', {}).get('list', {}).get('timeline_response', {}).get("timeline", {}).get("instructions", [{}])[-1].get('entries',[])
    if len(entries)>0:
        for entry in entries:
            content = entry.get("content")
            if (content.get("__typename") == "TimelineTimelineCursor") & (content.get("cursorType") =="Bottom"):
                next_cursor = content.get("value", None)
                if next_cursor:
                    if next_cursor.split('|')[0]=="0":
                        next_cursor = None
            if content.get("__typename") != "TimelineTimelineCursor":
                legacy = content.get("content", {}). get('userResult', {}).get("result", {}).get("legacy", {})
                results.append(legacy)

    write_jsonl(results, path_json, filename)
    return results, next_cursor


def parse_list_entries(jsonl_data: list)-> pd.DataFrame:
    """
    Parse list details from JSONL data obtained from the Twitter API.

    Args:
        jsonl_data (list): List of dictionaries containing JSON data.

    Returns:
        pd.DataFrame: DataFrame containing parsed list details.
    """
    all_records=[]
    for data in jsonl_data:
        id_str = data.get("id_str","")
        name = data.get("name","")
        screen_name = data.get("screen_name", "")
        created_at = data.get("created_at")
        description = data.get("description")
        statuses_count = data.get("statuses_count", 0)
        followers_count = data.get("followers_count",0)
        friends_count = data.get("friends_count",0)
        favourites_count = data.get("favourites_count",0)
        media_count = data.get("media_count",0)
        protected = data.get("protected", False)
        verified = data.get("verified", False)
        verified_type = data.get("verified_type", "")
        entities = data.get("entities", {})
        urls = [url.get("expanded_url","") for url in entities.get('url', {}).get("urls",[])]
        user_mentions = [um.get("screen_name","") for um in entities.get('description', {}).get('user_mentions', [])]
        user_mentions_indices = [um.get("indices",[]) for um in entities.get('description', {}).get('user_mentions', [])]
        hashtags = [um.get("text","") for um in entities.get('description', {}).get('hashtags', [])]
        hashtags_indices = [um.get("indices",[]) for um in entities.get('description', {}).get('hashtags', [])]
        record = (id_str, name, screen_name, created_at, description, statuses_count, followers_count, friends_count, favourites_count, media_count, protected, verified, verified_type, urls, user_mentions, user_mentions_indices, hashtags, hashtags_indices)
        all_records.append(record)
    df = pd.DataFrame.from_records(all_records, columns = ["id_str", "name", "screen_name", "created_at", "description", "statuses_count", "followers_count", "friends_count", "favourites_count", "media_count", "protected", "verified", "verified_type", "urls", "user_mentions", "user_mentions_indices", "hashtags", "hashtags_indices"])
    return df