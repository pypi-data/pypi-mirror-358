import praw
import datetime 
import pandas as pd
from tqdm import tqdm
import time

def check_limit(reddit_client : praw.Reddit) -> tuple:
    """
    Check Reddit Client rate limit and wait if necessary.

    Args:
        reddit_client (praw.Reddit): current reddit client

    Returns:
        tuple containing the following information:
            - remaining: remaining queries.
            - reset_timestamp: time before reset.
            - used: number of sent queries.

    """
    headers = reddit_client.auth.limits
    remaining = headers.get('remaining')
    reset_timestamp = headers.get('reset_timestamp')
    used = headers.get('used')

    if remaining and reset_timestamp :
        if remaining <= 10:
            # Calculate the time to wait until reset
            current_time = time.time()
            wait_time = reset_timestamp - current_time

            if wait_time > 0:
                # Convert wait_time to seconds and wait
                print(f"Waiting for {wait_time:.2f} seconds until the next reset...")
                time.sleep(wait_time)
            else:
                print("Reset time is in the past. No need to wait.")
        # else:
        #     print(f"{remaining} requests remaining. No need to wait.")
    else : 
        print("Missing required header information. Cannot determine wait time.")

    return remaining, reset_timestamp, used


def get_subreddit_info(reddit_client : praw.Reddit, lst_ids: list) -> pd.DataFrame:
    """
    Retrieves information about subreddits based on a list of subreddit IDs.

    Args:
        reddit_client (praw.Reddit): current reddit client
        lst_ids (list): A list of subreddit IDs.

    Returns:
        pd.DataFrame: A DataFrame containing the following information for each subreddit:
            - subreddit_id: The ID of the subreddit.
            - name: The name of the subreddit.
            - display_name: The display name of the subreddit.
            - subscribers: The number of subscribers to the subreddit.
            - date: The creation date of the subreddit.
            - description: The description of the subreddit.
            - public_description: The public description of the subreddit.
            - over18: Indicates if the subreddit is for users over 18 years old.
            - spoilers_enabled: Indicates if spoilers are enabled in the subreddit.
            - can_assign_user_flair: Indicates if users can assign their own flair in the subreddit.
            - can_assign_link_flair: Indicates if users can assign flair to links in the subreddit.
    """
    all_records = []
    for reddit_id in lst_ids:
        remaining, reset_timestamp, used = check_limit(reddit_client)
        subreddit = reddit_client.subreddit(str(reddit_id))
        record = parse_subreddit(reddit_client, subreddit)
  
        all_records.append(record)

    df = pd.DataFrame.from_records(all_records, columns=["subreddit_id", "subreddit_name", "subreddit_display_name", "subreddit_subscribers", "subreddit_date", "subreddit_description", "subreddit_public_description", "subreddit_over18", "subreddit_spoilers_enabled", "subreddit_can_assign_user_flair", "subreddit_can_assign_link_flair", "subreddit_lang", "subreddit_active_user_count"])
    return df


def getSubmissions(reddit_client : praw.Reddit, sub_id : str, subreddit_filter : str, subreddit_items : int, time_filter : str) -> pd.DataFrame:
    """
    Retrieves submission from a subreddit ID.

    Args:
        reddit_client (praw.Reddit): current reddit client
        sub_id (str): a subreddit ID.
        subreddit_filter (str): the filter to apply to the subreddit (top, hot, new, controversial).
        subreddit_items (int): the number of items to retrieve. None to retrieve all items.
        time_filter (str): the time filter to apply to the subreddit (hour, day, week, month, year, all).

    Returns:
        pd.DataFrame: A DataFrame containing submissions metadata.
    """
    
    all_records = []
    # for sub_id in tqdm(lst_ids, total=len(lst_ids), desc="Récupération des soumissions"):
    remaining, reset_timestamp, used = check_limit(reddit_client)
    subreddit = reddit_client.subreddit(str(sub_id))
    remaining, reset_timestamp, used = check_limit(reddit_client)
    if not vars(subreddit).get('_fetched'):
        subreddit._fetch()
        remaining, reset_timestamp, used = check_limit(reddit_client)

    sub_record = parse_subreddit(reddit_client, subreddit)

    if subreddit_filter == "top":
        subreddit_selection = subreddit.top(limit=subreddit_items, time_filter= time_filter)
    elif subreddit_filter == "hot":
        subreddit_selection = subreddit.hot(limit=subreddit_items)
    elif subreddit_filter == "controversial":
        subreddit_selection = subreddit.controversial(limit=subreddit_items, time_filter= time_filter)
    elif subreddit_filter == "new":
        subreddit_selection = subreddit.new(limit=subreddit_items)
    elif subreddit_filter == "gilded":
        subreddit_selection = subreddit.gilded(limit=subreddit_items)
    elif subreddit_filter == "rising":
        subreddit_selection = subreddit.rising(limit=subreddit_items)
    else:
        return pd.DataFrame()
        
    
    remaining, reset_timestamp, used = check_limit(reddit_client)
    for i, submission in enumerate(subreddit_selection):
        try:
            remaining, reset_timestamp, used = check_limit(reddit_client)
            if not vars(submission).get('_fetched'):
                submission._fetch()
                remaining, reset_timestamp, used = check_limit(reddit_client)

            author = submission.author
            author_record  = parse_author(reddit_client, author)
            submission_record = parse_submission(reddit_client, submission)    

            record = sub_record + author_record + submission_record
            all_records.append(record)
           
        except Exception as e:
            pass
            print(e)

        df = pd.DataFrame.from_records(all_records, 
                                        columns = ["subreddit_id", "subreddit_name", "subreddit_display_name", "subreddit_subscribers", "subreddit_date", "subreddit_description", "subreddit_public_description", "subreddit_over18", 
                                                    "subreddit_spoilers_enabled", "subreddit_can_assign_user_flair", "subreddit_can_assign_link_flair", "subreddit_lang", "subreddit_active_user_count",
                                                    "author_id", "author_name", "author_link_karma", "author_comment_karma", "author_created_utc", "author_icon_img", "author_is_employee", "author_is_mod", "author_is_gold",
                                                    "submission_id", "submission_title", "submission_name", "submission_created_utc", "submission_distinguished", "submission_edited", "submission_is_self", "submission_link_flair_template_id", 
                                                    "submission_link_flair_text", "submission_locked", "submission_num_comments", "submission_over_18", "submission_permalink", "submission_selftext", "submission_spoiler", 
                                                    "submission_stickied", "submission_url", "submission_upvote_ratio", "submission_downs", "submission_ups", "submission_num_crossposts", "submission_num_reports", "submission_score", 
                                                    "submission_total_awards_received", "submission_view_count"]
        )

    return df



def getComments(reddit_client : praw.Reddit, submission_id : str) -> pd.DataFrame:
    """
    Retrieves all comments from a submission ID.

    Args:
        reddit_client (praw.Reddit): current reddit client
        submission_id (str): a submission ID.

    Returns:
        pd.DataFrame: A DataFrame containing comments metadata.
    
    """
    
    remaining, reset_timestamp, used = check_limit(reddit_client)
    submission = reddit_client.submission(str(submission_id))
    if not vars(submission).get('_fetched'):
        submission._fetch()

    submission.comments.replace_more(limit=None)
    remaining, reset_timestamp, used = check_limit(reddit_client)

    all_records = []
    for comment in tqdm(submission.comments.list(), total=len(submission.comments.list()), desc="Récupération des commentaires"):
        remaining, reset_timestamp, used = check_limit(reddit_client)
        record = (submission_id,) + parse_comments(reddit_client, comment)
        all_records.append(record)

    df = pd.DataFrame.from_records(all_records, columns=["submission_id", "comment_id", "comment_body", "comment_date", "comment_distinguished", "comment_is_submitter", "comment_link_id", "comment_parent_id", "comment_permalink", 
                                                         "comment_controversiality", "comment_depth", "comment_score", "comment_total_awards_received", "comment_ups",
                                                         "author_id", "author_name", "author_link_karma", "author_comment_karma", "author_created_utc", "author_icon_img", "author_is_employee", "author_is_mod", "author_is_gold"
                                                         ])

    return df

def get_top_level_comments(reddit_client : praw.Reddit, submission_id : str) -> pd.DataFrame:
    """
    Retrieves top level comments from a submission ID.

    Args:
        reddit_client (praw.Reddit): current reddit client
        submission_id (str): a submission ID.

    Returns:
        pd.DataFrame: A DataFrame containing comments metadata.
    
    """

    remaining, reset_timestamp, used = check_limit(reddit_client)
    submission = reddit_client.submission(str(submission_id))
    if not vars(submission).get('_fetched'):
        submission._fetch()

    submission.comments.replace_more(limit=None)
    remaining, reset_timestamp, used = check_limit(reddit_client)

    all_records = []
    for comment in tqdm(submission.comments, total=len(submission.comments), desc="Récupération des commentaires"):
        remaining, reset_timestamp, used = check_limit(reddit_client)
        record = (submission_id,) + parse_comments(reddit_client, comment)
        all_records.append(record)

    df = pd.DataFrame.from_records(all_records, columns=["submission_id", "comment_id", "comment_body", "comment_date", "comment_distinguished", "comment_is_submitter", "comment_link_id", "comment_parent_id", "comment_permalink", 
                                                         "comment_controversiality", "comment_depth", "comment_score", "comment_total_awards_received", "comment_ups",
                                                         "author_id", "author_name", "author_link_karma", "author_comment_karma", "author_created_utc", "author_icon_img", "author_is_employee", "author_is_mod", "author_is_gold"
                                                         ])

    return df

def parse_author(reddit_client : praw.Reddit, author : praw.models.Redditor) -> tuple:
    """
    Parses a Reddit author object and extracts relevant information.

    Args:
        reddit_client (praw.Reddit): current reddit client
        author (praw.models.Redditor): The Reddit author object.

    Returns:
        tuple: A tuple containing the following information about the author:
            - author_id: The ID of the author.
            - author_name: The name of the author.
            - author_link_karma: The link karma of the author.
            - author_comment_karma: The comment karma of the author.    
            - author_created_utc: The creation date of the author.
            - author_icon_img: The icon image of the author.
            - author_is_employee: Indicates if the author is an employee.
            - author_is_mod: Indicates if the author is a moderator.
            - author_is_gold: Indicates if the author has Reddit Gold.
    """

    if author:
        if not vars(author).get('_fetched'):
            remaining, reset_timestamp, used = check_limit(reddit_client)
            author._fetch()
        author_comment_karma= vars(author).get("comment_karma", None)

        author_created_utc= vars(author).get("created_utc", None)
        if author_created_utc:
            author_created_utc = datetime.datetime.fromtimestamp(int(author_created_utc)).replace(tzinfo=datetime.timezone.utc).strftime("%d/%m/%Y %H:%M:%S")
        else:
            author_created_utc = datetime.datetime(1970,1,1,0,0,0)
        
        author_icon_img= vars(author).get("icon_img", None)
        author_is_employee= vars(author).get("is_employee", None)
        author_is_mod= vars(author).get("is_mod", None)
        author_is_gold= vars(author).get("is_gold", None)
        author_link_karma= vars(author).get("link_karma", None)
        author_name= vars(author).get("name", None)
        author_id= vars(author).get("id", None)

        record = (author_id, author_name, author_link_karma, author_comment_karma, author_created_utc, author_icon_img, author_is_employee, author_is_mod, author_is_gold)
    else:
        record = (None, None, None, None, None, None, None, None, None)
    return record

def parse_submission(reddit_client : praw.Reddit, submission : praw.models.Submission) -> tuple:
    """
    Parses a Reddit submission object and extracts relevant information.

    Args:
        reddit_client (praw.Reddit): current reddit client
        submission (praw.models.Submission): The Reddit submission object.

    Returns:
        tuple: A tuple containing information about the submission.
    """

    if submission :
        if not vars(submission).get('_fetched'): 
            remaining, reset_timestamp, used = check_limit(reddit_client)
            submission._fetch()
        submission_id= vars(submission).get("id", None)
        submission_title= vars(submission).get("title", None)
        submission_name= vars(submission).get("name", None)
        submission_created_utc= vars(submission).get("created_utc", None)
        if submission_created_utc:
            submission_created_utc = datetime.datetime.fromtimestamp(int(submission_created_utc)).replace(tzinfo=datetime.timezone.utc).strftime("%d/%m/%Y %H:%M:%S")
        else:
            submission_created_utc = datetime.datetime(1970,1,1,0,0,0)
        submission_distinguished= vars(submission).get("distinguished", None)
        submission_edited= vars(submission).get("edited", None)
        submission_is_self= vars(submission).get("is_self", None)
        submission_link_flair_template_id= vars(submission).get("link_flair_template_id", None)
        submission_link_flair_text= vars(submission).get("link_flair_text", None)
        submission_locked= vars(submission).get("locked", None)
        submission_num_comments= vars(submission).get("num_comments", None)
        submission_over_18= vars(submission).get("over_18", None)
        submission_permalink= vars(submission).get("permalink", None)
        submission_selftext= vars(submission).get("selftext", None)
        submission_spoiler= vars(submission).get("spoiler", None)
        submission_stickied= vars(submission).get("stickied", None)
        submission_upvote_ratio= vars(submission).get("upvote_ratio", None)
        submission_url= vars(submission).get("url", None)
        submission_downs= vars(submission).get("downs", None)
        submission_num_crossposts= vars(submission).get("num_crossposts", None)
        submission_num_reports= vars(submission).get("num_reports", None)
        submission_score= vars(submission).get("score", None)
        submission_total_awards_received= vars(submission).get("total_awards_received", None)
        submission_view_count= vars(submission).get("view_count", None)
        submission_ups= vars(submission).get("ups", None)
        record = (submission_id, submission_title, submission_name, submission_created_utc, submission_distinguished, submission_edited, submission_is_self, submission_link_flair_template_id, 
                  submission_link_flair_text, submission_locked, submission_num_comments, submission_over_18, submission_permalink, submission_selftext, submission_spoiler, 
                  submission_stickied, submission_url, submission_upvote_ratio, submission_downs, submission_ups, submission_num_crossposts, submission_num_reports, submission_score, 
                  submission_total_awards_received, submission_view_count)
    else:
        record = (None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None)
    return record 


def parse_subreddit(reddit_client : praw.Reddit, subreddit : praw.models.Subreddit) -> tuple:
    """
    Parses a Reddit subreddit object and extracts relevant information.

    Args:
        reddit_client (praw.Reddit): current reddit client
        subreddit (praw.models.Subreddit): The Reddit subreddit object.

    Returns:
        tuple: A tuple containing information about the subreddit.
    """

    if subreddit:
        if not vars(subreddit).get('_fetched'):
            remaining, reset_timestamp, used = check_limit(reddit_client)
            subreddit._fetch()
        subreddit_id= vars(subreddit).get("id", None)
        name = vars(subreddit).get("name", None)
        display_name = vars(subreddit).get("display_name", None)
        subscribers = vars(subreddit).get("subscribers", None)
        subscribers = vars(subreddit).get("subscribers", None)
        date = vars(subreddit).get("created_utc", None)
        if date:
            date=datetime.datetime.fromtimestamp(int(date)).replace(tzinfo=datetime.timezone.utc).strftime("%d/%m/%Y %H:%M:%S")
        else:
            date = datetime.datetime(1970,1,1,0,0,0)
        description = vars(subreddit).get("description", None)
        public_description = vars(subreddit).get("public_description", None)
        over18 = vars(subreddit).get("over18", None)
        spoilers_enabled = vars(subreddit).get("spoilers_enabled", None)
        can_assign_user_flair = vars(subreddit).get("can_assign_user_flair", None)
        can_assign_link_flair = vars(subreddit).get("can_assign_link_flair", None)
        lang = vars(subreddit).get("lang", None)
        active_user_count = vars(subreddit).get("active_user_count", None)

        record = (subreddit_id, name, display_name, subscribers, date, description, public_description, over18, spoilers_enabled, can_assign_user_flair, can_assign_link_flair, lang, active_user_count)

    else:
        record = (None, None, None, None, None, None, None, None, None, None, None, None, None)
    return record

def parse_comments(reddit_client : praw.Reddit, comment : praw.models.Comment) -> tuple:
    """
    Parses a Reddit comment object and extracts relevant information.

    Args:
        reddit_client (praw.Reddit): current reddit client
        comment (praw.models.Comment): The Reddit comment object.

    Returns:
        tuple: A tuple containing information about the comment.
    """

    if comment:
        if not vars(comment).get('_fetched'):
            remaining, reset_timestamp, used = check_limit(reddit_client)
            comment._fetch()
        comment_id = vars(comment).get("id", None)
        comment_body = vars(comment).get("body", None)
        comment_date = vars(comment).get("created_utc", None)
        if comment_date:
            comment_date = datetime.datetime.fromtimestamp(int(comment_date)).replace(tzinfo=datetime.timezone.utc).strftime("%d/%m/%Y %H:%M:%S")
        else:
            comment_date = datetime.datetime(1970,1,1,0,0,0)
        comment_distinguished = vars(comment).get("distinguished", None)
        # comment_edited = vars(comment).get("edited", None)
        comment_is_submitter = vars(comment).get("is_submitter", None)
        comment_link_id = vars(comment).get("link_id", None)
        comment_parent_id = vars(comment).get("parent_id", None)
        comment_permalink = vars(comment).get("permalink", None)
        comment_controversiality = vars(comment).get("controversiality", None)
        comment_depth = vars(comment).get("depth", None)
        # comment_downs = vars(comment).get("downs", None)
        # comment_likes = vars(comment).get("likes", None)
        # comment_num_reports = vars(comment).get("num_reports", None)
        comment_score = vars(comment).get("score", None)
        comment_total_awards_received = vars(comment).get("total_awards_received", None)
        comment_ups = vars(comment).get("ups", None)
        author = comment.author
        author_record = parse_author(reddit_client, author)
        record = (comment_id, comment_body, comment_date, comment_distinguished, comment_is_submitter, comment_link_id, comment_parent_id, comment_permalink, comment_controversiality, comment_depth, comment_score, comment_total_awards_received, comment_ups) + author_record    
    else:
        record = (None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None)  
    return record
            