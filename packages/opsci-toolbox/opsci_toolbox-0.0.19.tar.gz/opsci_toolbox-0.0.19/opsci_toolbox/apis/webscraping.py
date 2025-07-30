from urllib.parse import urlparse
import requests
from trafilatura import extract
from bs4 import BeautifulSoup
from opsci_toolbox.helpers.common import write_json, read_json, list_files_in_dir, save_dataframe_csv
import justext
import os
import hashlib
import re
import concurrent.futures
import pandas as pd
from tqdm import tqdm

def get_tweet_html(username: str, tweet_id: str, **kwargs) -> str:
    """
    Retrieves the HTML code of a tweet given the username and tweet ID.

    Args:
        username (str): The username of the Twitter account.
        tweet_id (str): The ID of the tweet.
        kwargs : additional parameters to pass to the Twitter API.

    Returns:
        str: The HTML code of the tweet.


    """
    params = {'lang':"en",             # language of the features around the tweet
              "maxwidth" : 550,        # size of the tweet
              "hide_media":False,      # to hide photo / video
              "hide_thread":False,     # to hide original message on replies
              "omit_script": True,     # to include or not the JS script : <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
              "align": None,           # to align the tweet {left,right,center,none}
              "theme": "light",        # theme of the tweet {light,dark}
              "dnt": True              # When set to true, the Tweet and its embedded page on your site are not used for purposes that include personalized suggestions and personalized ads.
              }
    
    params.update(kwargs)

    url = f'https://publish.twitter.com/oembed?url=https://twitter.com/{username}/status/{tweet_id}'
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        html = data.get('html')
        return html, username, tweet_id
    else:
        print(response.url, "Failed to fetch data from Twitter.")
        return None, username, tweet_id


def parallel_twitter_oembed(usernames, tweet_ids, **kwargs):
    """
    Scrapes Twitter oEmbed data for multiple tweets in parallel.

    Args:
        usernames (list): A list of Twitter usernames.
        tweet_ids (list): A list of tweet IDs corresponding to the tweets of the given usernames.
        **kwargs: Additional keyword arguments to be passed to the `get_tweet_html` function.

    Returns:
        pandas.DataFrame: A DataFrame containing the scraped tweet HTML, username, and message ID.

    Raises:
        Exception: If there is an error while downloading the tweet HTML.

    """
    all_data = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit scraping tasks for each URL and add tqdm progress bar
        futures = [
            executor.submit(get_tweet_html, username, tweet_id, **kwargs)
            for username, tweet_id in zip(usernames, tweet_ids)
        ]
        for future in tqdm(
            concurrent.futures.as_completed(futures),
            total=len(usernames),
            desc="Scraping Progress",
        ):
            try:
                data, username, tweet_id = future.result()
                all_data.append((data, username, tweet_id))
            except Exception as e:
                print(f"Error downloading : {e}")

    df = pd.DataFrame(all_data, columns=["tweet_html", "user_name", "message_id"])
    return df


def url_get_domain(url: str) -> str:
    """
    Extracts and returns the domain name from a given URL.

    Args:
        url (str): The URL string from which the domain name is to be extracted.

    Returns:
        str: The domain name extracted from the URL.
    """
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.hostname if parsed_url.hostname else parsed_url.netloc
        return domain
    except Exception as e:
        pass
        print(url, e)
        return url


def url_get_extension(url: str) -> str:
    """
    Extracts and returns the extension (TLD) of the domain name from a given URL.

    Args:
        url (str): The URL string from which the domain extension is to be extracted.

    Returns:
        str: The extension (TLD) of the domain name extracted from the URL.
    """
    # Parse the URL using urlparse
    parsed_url = urlparse(url)

    # Extract the netloc (network location) from the parsed URL
    netloc = parsed_url.netloc

    # Split the netloc by '.' to get the domain and TLD
    domain_parts = netloc.split(".")

    # Get the last part, which represents the TLD
    extension = ".".join(domain_parts[-1:])

    return extension


def url_clean_parameters(url: str) -> str:
    """
    Removes query parameters and UTM tags from a given URL and returns the cleaned URL.

    Args:
        url (str): The URL string from which parameters and UTM tags are to be removed.

    Returns:
        str: The cleaned URL without any parameters or UTM tags.
    """
    parsed_url = urlparse(url)
    netloc = parsed_url.netloc if parsed_url.netloc else ""
    path = parsed_url.path if parsed_url.path else ""
    return netloc + path


def url_clean_protocol(url: str) -> str:
    """
    Removes the 'http://' or 'https://' prefix from a given URL.

    Args:
        url (str): The URL string from which the protocol is to be removed.

    Returns:
        str: The URL without the 'http://' or 'https://' prefix.
    """
    prefixes_to_remove = ["https://", "http://"]

    for prefix in prefixes_to_remove:
        if url.startswith(prefix):
            url = url[len(prefix) :]
            break

    return url


def url_remove_www(url: str) -> str:
    """
    Removes the 'www.' prefix from a given URL, along with any protocol prefix.

    Args:
        url (str): The URL string from which the 'www.' prefix is to be removed.

    Returns:
        str: The URL without the 'www.' prefix.
    """
    prefixes_to_remove = ["https://www.", "http://www.", "https://", "http://", "www."]

    for prefix in prefixes_to_remove:
        if url.startswith(prefix):
            url = url[len(prefix) :]
            break

    return url


def url_add_protocol(url: str) -> str:
    """
    Ensures the given URL has a protocol ('https://') and 'www.' prefix if necessary.

    Args:
        url (str): The URL string to be formatted with protocol and 'www.' prefix if required.

    Returns:
        str: The formatted URL with protocol and 'www.' prefix if it was missing.
    """
    parsed_url = urlparse(url)

    if len(parsed_url.scheme) < 1 and parsed_url.path.startswith("www"):
        url = "https://" + url
    elif len(parsed_url.scheme) < 1 and len(parsed_url.path.split(".")) < 3:
        url = "https://www." + url
    elif len(parsed_url.scheme) < 1 and len(parsed_url.path.split(".")) > 2:
        url = "https://" + url
    else:
        return url

    return url


def url_is_valid(url: str) -> bool:
    """
    Checks if a given URL is valid.

    Args:
        url (str): The URL string to be validated.

    Returns:
        bool: True if the URL is valid, False otherwise.
    """
    try:
        parsed_url = urlparse(url)
        return parsed_url.scheme in ["http", "https"] and parsed_url.netloc != ""
    except Exception as e:
        # If there is any error during URL parsing, consider it invalid
        return False


def url_is_reachable(url: str) -> bool:
    """
    Checks if a given URL is reachable (i.e., does not return a 404 error or other HTTP errors).

    Args:
        url (str): The URL string to be checked for reachability.

    Returns:
        bool: True if the URL is reachable, False otherwise.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return True  # No HTTP error, URL is reachable
    except requests.RequestException as e:
        print(f"Error: {e}")
        return False  # HTTP error occurred, URL is not reachable


def scrape(url: str) -> requests.Response:
    """
    Sends a GET request to the given URL and returns the full response.

    Args:
        url (str): The URL to be requested.

    Returns:
        requests.Response: The full response from the GET request.
    """
    try:
        response = requests.get(url)
    except Exception as e:
        pass
        print(e, "-", url)
    return response


def justext_parse_content(response: requests.Response, languages: list = ["English", "French"]) -> str:
    """
    Extracts and returns the main content from an HTML response using jusText.

    Args:
        response (requests.Response): The HTTP response object containing the HTML content.
        languages (list): A list of languages to use for stopword lists in jusText. Default is ["English", "French"].

    Returns:
        str: The extracted main content from the HTML response.
    """
    stoplist = frozenset()

    for lang in languages:
        current_stoplist = justext.get_stoplist(lang)
        stoplist = stoplist.union(current_stoplist)

    try:
        paragraphs = justext.justext(response.content, stoplist)
        filtered_paragraphs = [
            paragraph.text for paragraph in paragraphs if not paragraph.is_boilerplate
        ]
        concatenated_text = ". ".join(filtered_paragraphs)
        concatenated_text = re.sub(r"\.\. ", ". ", concatenated_text)

    except Exception as e:
        pass
        print(e)
    return concatenated_text


def trafilatura_parse_content(response: requests.Response) -> str:
    """
    Extracts and returns the main content from an HTML response using Trafilatura.

    Args:
        response (requests.Response): The HTTP response object containing the HTML content.

    Returns:
        str: The extracted main content from the HTML response.
    """
    try:
        text = extract(response.content)
    except Exception as e:
        pass
        print(e)
    return text


def process_scraping(
    url: str,
    path: str,
    method: str = "justext",
    languages: list = ["English", "French"],
    title: bool = True,
    meta: bool = True,
    lst_properties: list = [
        "og:site_name",
        "og:url",
        "og:title",
        "og:description",
        "og:type",
        "og:article:section",
        "og:article:author",
        "og:article:published_time",
        "article:modified_time",
        "og:image",
        "og:image:width",
        "og:image:height",
        "og:video",
        "og:video:url",
        "og:video:width",
        "og:video:height",
        "fb:page_id",
        "twitter:url",
        "twitter:title",
        "twitter:description",
        "twitter:image",
        "al:ios:app_store_id",
        "al:ios:app_name",
        "al:android:package",
        "al:android:app_name",
    ],
) -> dict:
    """
    Process scraping of a URL, extract main content, title, and meta properties,
    and store the results in a JSON file.

    Args:
        url (str): The URL to scrape.
        path (str): The directory path where the scraped data JSON file will be saved.
        method (str, optional): The method to use for content extraction ('justext' or 'trafilatura'). Defaults to 'justext'.
        languages (list, optional): A list of languages for stopword lists in jusText. Defaults to ["English", "French"].
        title (bool, optional): Whether to extract the title from the HTML. Defaults to True.
        meta (bool, optional): Whether to extract meta properties from the HTML. Defaults to True.
        lst_properties (list, optional): List of specific meta properties to extract. Defaults to a comprehensive list.

    Returns:
        dict or None: A dictionary containing the extracted data and file path if successful, or None if an error occurs.
    """
    try:

        # We name the files
        data = dict()
        url_hash = hashlib.md5(url.encode()).hexdigest()
        filename = f"scraped_data_{url_hash}.json"
        filepath = os.path.join(path, filename)

        # we scrape the HTML page
        response = scrape(url)

        # we parse the response to get main content and eventually title and meta tags
        if method == "justext":
            text = justext_parse_content(response, languages)
        else:
            text = trafilatura_parse_content(response)

        # we create a dict with results
        data = {"path": filepath, "url": url}

        if text:
            data["text"] = text
        else:
            data["text"] = None

        if title:
            title_txt = parse_title(response)
            data["title"] = title_txt
        else:
            data["title"] = None

        if meta:
            meta_dict = get_meta_properties(response)
            for key in meta_dict.keys():
                data[key] = meta_dict[key]
        else:
            for key in lst_properties:
                data[key] = None

        # we store the json file
        if not os.path.exists(filepath):
            write_json(data, path, filename)
        else:
            data = read_json(filepath)

        return data

    except Exception as e:
        print(url, "-", e)
        return None


def parse_title(response: requests.Response) -> str:
    """
    Extracts and returns the webpage title from an HTML response.

    Parameters:
    response (requests.Response): The HTTP response object containing the HTML content.

    Returns:
    str or None: The extracted title text if found, None if no title tag is found or an error occurs.
    """
    try:
        soup = BeautifulSoup(response.content, "html.parser")

        # Find the title tag and extract its text
        title_tag = soup.find("title")
        if title_tag:
            return title_tag.text.strip()
        else:
            print("No title found")
            return None
    except Exception as e:
        pass
        print(e)
        return None


def get_meta_properties(response: requests.Response, lst_properties: list = [
        "og:site_name",
        "og:url",
        "og:title",
        "og:description",
        "og:type",
        "og:article:section",
        "og:article:author",
        "og:article:published_time",
        "article:modified_time",
        "og:image",
        "og:image:width",
        "og:image:height",
        "og:video",
        "og:video:url",
        "og:video:width",
        "og:video:height",
        "fb:page_id",
        "twitter:url",
        "twitter:title",
        "twitter:description",
        "twitter:image",
        "al:ios:app_store_id",
        "al:ios:app_name",
        "al:android:package",
        "al:android:app_name",
    ]) -> dict:
    """
    Extracts specified meta properties from a webpage and returns them as a dictionary.

    Args:
        response (requests.Response): The HTTP response object containing the HTML content.
        lst_properties (list, optional): A list of meta property names to extract. Defaults to a comprehensive list.

    Returns:
        dict or None: A dictionary mapping meta property names to their content values if found, or None if an error occurs.
    """
    try:

        # Parse HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, "html.parser")

        # Find all 'meta' tags
        meta_tags = soup.find_all("meta")

        # Extract meta properties and content
        meta_properties = {}
        for meta_tag in meta_tags:
            property_attr = meta_tag.get("property")
            content_attr = meta_tag.get("content")

            if property_attr and content_attr:
                if property_attr in lst_properties:
                    meta_properties[property_attr] = content_attr
                else:
                    meta_properties[property_attr] = None

        return meta_properties

    except requests.RequestException as e:
        print(f"Error: {e}")
        return None


def parallel_scraping(
    urls: list,
    path: str,
    max_workers: int = 8,
    method: str = "justext",
    languages: list = ["English", "French"],
    title: bool = True,
    meta: bool = True,
    lst_properties: list = [
        "og:site_name",
        "og:url",
        "og:title",
        "og:description",
        "og:type",
        "og:article:section",
        "og:article:author",
        "og:article:published_time",
        "article:modified_time",
        "og:image",
        "og:image:width",
        "og:image:height",
        "og:video",
        "og:video:url",
        "og:video:width",
        "og:video:height",
        "fb:page_id",
        "twitter:url",
        "twitter:title",
        "twitter:description",
        "twitter:image",
        "al:ios:app_store_id",
        "al:ios:app_name",
        "al:android:package",
        "al:android:app_name",
    ],
):
    """
    Execute concurrent threads to scrape multiple webpages.

    Args:
        urls (list): List of URLs to scrape.
        path (str): The directory path where scraped data will be saved.
        max_workers (int, optional): Maximum number of concurrent threads. Defaults to 8.
        method (str, optional): Method to use for content extraction ('justext' or 'trafilatura'). Defaults to 'justext'.
        languages (list, optional): Languages for stopword lists in jusText. Defaults to ['English', 'French'].
        title (bool, optional): Whether to extract title from HTML. Defaults to True.
        meta (bool, optional): Whether to extract meta properties from HTML. Defaults to True.
        lst_properties (list, optional): List of specific meta properties to extract. Defaults to a comprehensive list.

    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit scraping tasks for each URL and add tqdm progress bar
        futures = [
            executor.submit(
                process_scraping,
                url,
                path,
                method,
                languages,
                title,
                meta,
                lst_properties,
            )
            for url in urls
        ]
        for future in tqdm(
            concurrent.futures.as_completed(futures),
            total=len(urls),
            desc="Scraping Progress",
        ):
            try:
                data = future.result()
            except Exception as e:
                print(f"Error scraping : {e}")


def parse_scraped_webpages(path_json_files: str, output_path: str, name: str) -> pd.DataFrame:
    """
    Parse JSON files containing scraped data and save the extracted data into a CSV file.

    Args:
        path_json_files (str): Directory path containing JSON files.
        output_path (str): Directory path where the CSV file will be saved.
        name (str): Name of the CSV file.

    Returns:
        pd.DataFrame: DataFrame containing the parsed data from JSON files.
    """
    extracted_data = []

    files_to_parse = list_files_in_dir(path_json_files, "*.json")

    for file in tqdm(
        files_to_parse, total=len(files_to_parse), desc="Parsing files progress"
    ):
        data = read_json(file)
        extracted_data.append(data)

    df = pd.DataFrame(extracted_data)
    save_dataframe_csv(df, output_path, name)
    return df

def download_file(url: str, path: str) -> None:
    """
    Download a file from a URL and save it locally.

    ARgs:
        url (str): The URL of the file to download.
        path (str): The local path where the file will be saved.

    Raises:
        requests.exceptions.RequestException: If an HTTP error occurs during the request.

    Returns:
        None
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses

        with open(path, 'wb') as file:
            file.write(response.content)

    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {url, e}")

def parallel_dl(urls: list, paths: list, max_workers: int = 8) -> None:
    """
    Execute concurrent threads to download multiple files from URLs and save them locally.

    Args:
        urls (list): List of URLs to download files from.
        paths (list): List of local paths where downloaded files will be saved.
        max_workers (int, optional): Maximum number of concurrent threads. Defaults to 8.

    Returns:
        None
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit scraping tasks for each URL and add tqdm progress bar
        futures = [
            executor.submit(
                download_file,
                url,
                path,
            )
            for url, path in zip(urls, paths)
        ]
        for future in tqdm(
            concurrent.futures.as_completed(futures),
            total=len(urls),
            desc="Scraping Progress",
        ):
            try:
                data = future.result()
            except Exception as e:
                print(f"Error downloading : {e}")