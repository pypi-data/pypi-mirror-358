import re
import umap
import numpy as np
import hdbscan
import pandas as pd
import os
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder, OneHotEncoder
from sklearn.cluster import AgglomerativeClustering
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import spacy
from spacy.language import Language
from spacy_language_detection import LanguageDetector
from spacymoji import Emoji
# from langchain.embeddings import HuggingFaceEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from sklearn.feature_selection import chi2
from urlextract import URLExtract
import ast
import emoji
import requests
import json
from opsci_toolbox.helpers.common import write_json, write_pickle, load_pickle, create_dir, copy_file, write_jsonl
from textacy.preprocessing.replace import urls
from textacy.preprocessing.remove import brackets
from eldar import Query
import torch
from transformers import TextClassificationPipeline, AutoModelForSequenceClassification, AutoTokenizer, AutoConfig
from bs4 import BeautifulSoup
from nltk.tokenize import PunktSentenceTokenizer

####################################################################
# CLEANING
####################################################################

def remove_html_tags(text: str) -> str:
    """
    Remove HTML tags from the given text.

    Parameters:
    - text (str): The text containing HTML tags.

    Returns:
    - str: The text with HTML tags removed.
    """
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text()

def remove_rt(text: str) -> str:
    """
    Remove the retweet tag from a given text.

    Args:
    - text (str): The input text possibly containing a retweet tag in the format "RT @username: ".

    Returns:
    - str: The cleaned text with the retweet tag removed.

    Example:
    >>> remove_rt("RT @user123: Check out this tweet!")
    'Check out this tweet!'
    """
    # Regular expression pattern to match "RT @username: "
    pattern = r'RT @\w+: '

    # Substitute the pattern with an empty string
    cleaned_text = re.sub(pattern, '', text)

    return cleaned_text

def filter_by_query(df: pd.DataFrame, col_text: str, query: str, ignore_case: bool = True, ignore_accent: bool = True, match_word: bool = False) -> pd.DataFrame:
    """
    Filter DataFrame rows by a query on a specific text column.

    Args:
        df : pandas DataFrame
            The DataFrame to filter.
        col_text : str
            The name of the column containing text data to query.
        query : str
            The query string to filter the DataFrame.
        ignore_case : bool, optional
            Whether to ignore case sensitivity. Default is True.
        ignore_accent : bool, optional
            Whether to ignore accents. Default is True.
        match_word : bool, optional
            Whether to match the whole word. Default is False.

    Returns:
        df_filtered : pandas DataFrame
            The filtered DataFrame.
    """
    eldar_query=Query(query, ignore_case = ignore_case, ignore_accent=ignore_accent, match_word=match_word)
    df = df[df[col_text].apply(eldar_query)]
    df=df.reset_index(drop=True)
    return df

def remove_trailing_dots(text):
    if text.endswith('…'):
        return text[:-3].strip()
    return text

def TM_clean_text(df: pd.DataFrame, col: str, col_clean: str) -> pd.DataFrame:
    """
    Generic cleaning process for topic modeling.

    Args:
        df : pandas DataFrame
            The DataFrame containing text data.
        col : str
            The name of the column containing the original text data.
        col_clean : str
            The name of the column to store the cleaned text data.

    Returns:
        df : pandas DataFrame
            The DataFrame with cleaned text data.
    """
    df[col_clean] = df[col].apply(remove_rt)
    df[col_clean] = df[col_clean].apply(remove_emoji)
    df[col_clean] = df[col_clean].apply(remove_trailing_dots)
    df[col_clean] = df[col_clean].apply(remove_html_tags)
    df[col_clean] = df[col_clean].apply(lambda x : brackets(x))
    df[col_clean] = df[col_clean].apply(lambda x : urls(x, repl= ''))
    df[col_clean] = df.apply(lambda row: " ".join(filter(lambda x: x[0] != "@", row[col_clean].split())), 1)
    # df[col_clean] = df[col_clean].apply(remove_multiple_hashtags)
    df[col_clean] = df[col_clean].apply(remove_extra_spaces)
    # df = df.loc[(df[col_clean] != ""), :]
    return df



def extract_insta_shortcode(url: str) -> str:
    """
    Extracts the shortcode from an Instagram URL.

    Args:
        url : str
            The Instagram URL containing the shortcode.

    Returns:
        shortcode : str
            The extracted shortcode.
    """    
    pattern =r'(?:https?:\/\/)?(?:www\.)?instagram\.com\/(?:p|reel|tv|stories)\/([a-zA-Z0-9_-]+)\/?'

    shortcode = re.findall(pattern, url)
    return shortcode[0]

def remove_parentheses_content(text: str) -> str:
    """
    Remove content within parentheses from the given text.

    Parameters:
    - text (str): The text from which content within parentheses should be removed.

    Returns:
    - str: The text with content within parentheses removed.
    """
    # Using regular expression to find content between parentheses and removing it
    result = re.sub(r'\([^)]*\)', '', text)
    return result

def remove_hashtags(text: str) -> str:
    """
    Removes any hashtag from text.

    Args:
        text : str
            The input text string to clean.

    Returns:
        result : str
            The input text string with hashtags removed.
    """
    pattern = r'\B#\w+'
    result = re.sub(pattern, '', text).strip()
    return result

def remove_multiple_hashtags(text: str) -> str:
    """
    Removes series of hashtags separated by spaces.

    Args:
        text : str
            The input text string to clean.

    Returns:
        result : str
            The input text string with series of hashtags removed.
    """
    pattern = r'(?:\B#\w+\s*){2,}'
    result = re.sub(pattern, '', text).strip()
    return result


def remove_emojis(text: str) -> str:
    """
    Removes emojis and their textual representations from a text string.

    Args:
        text : str
            The input text string containing emojis.

    Returns:
        text_no_emojis : str
            The input text string with emojis and their textual representations removed.
    """
    # Convert emojis to their textual representations
    text_no_emojis = emoji.demojize(text)
    
    # Remove emojis and their textual representations
    text_no_emojis = re.sub(r':[a-zA-Z_]+:', '', text_no_emojis)
    
    return text_no_emojis

def remove_emoji(string):
    emoji_pattern = re.compile(
        "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002500-\U00002BEF"  # chinese char
        u"\U00002702-\U000027B0"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642"
        u"\u2600-\u2B55"
        u"\u200d"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\ufe0f"  # dingbats
        u"\u3030"
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', string)


def extract_numbers(text: str) -> list:
    """
    Extracts all numeric values from a given text string and returns them as a list of floats.

    Args:
        text (str): The input string from which numbers are to be extracted.

    Returns:
        list: A list containing all the extracted numbers as floats.
    """
    # Define a regular expression pattern to match numbers
    pattern = r'\d+\.?\d*'

    # Use re.findall to find all matches of the pattern in the text
    numbers = re.findall(pattern, text)

    # Convert the extracted numbers from strings to floats
    numbers = [float(num) for num in numbers]

    return numbers

def contains_question_mark(text: str) -> int:
    """
    Checks if a given text string contains a question mark.

    Args:
        text (str): The input string to be checked.

    Returns:
        int: Returns 1 if the text contains a question mark, otherwise 0.
    """
    return 1 if '?' in text else 0

def contains_exclamation_mark(text: str) -> int:
    """
    Checks if a given text string contains an exclamation mark.

    Args:
        text (str): The input string to be checked.

    Returns:
        int: Returns 1 if the text contains an exclamation mark, otherwise 0.
    """
    return 1 if '!' in text else 0

def extract_urls_from_text(text: str) -> list:
    """
    Extracts URLs from a text string.

    Args:
        text : str
            The input text string containing URLs.

    Returns:
        urls : list of str
            A list of URLs extracted from the input text.
    """
    extractor = URLExtract()
    urls = extractor.find_urls(text)
    return urls

def extract_hashtags(text: str, lower: bool = True) -> list:
    ''' 
    Extracts hashtags from the text using a regular expression.

    Args:
        text : str
            The input text string containing hashtags.
        lower : bool, optional
            Whether to convert extracted hashtags to lowercase. Default is True.

    Returns:
        hashtags : list of str
            A list of hashtags extracted from the input text.
    '''
    hashtags = re.findall(r'\B#\w+', text)
    if lower : 
        hashtags= [h.lower() for h in hashtags]
    return hashtags

def extract_mentions(text: str, mention_char: str = '@', lower: bool = False) -> list:
    ''' 
    Extracts mentions from the text using a regular expression.

    Args:
        text : str
            The input text string containing mentions.
        mention_char : str, optional
            The character used to indicate mentions. Default is '@'.
        lower : bool, optional
            Whether to convert extracted mentions to lowercase. Default is False.

    Returns:
        mentions : list of str
            A list of mentions extracted from the input text.
    '''
    pattern = r"(?<=^|(?<=[^a-zA-Z0-9-_\.]))" + re.escape(mention_char) + r"([A-Za-z0-9_]{4,15})"

    mentions = re.findall(pattern, text)
    if lower: 
        mentions = [mention.lower() for mention in mentions]
    return mentions

def remove_extra_spaces(text: str) -> str:
    """
    Removes extra spaces from a text string.

    Args:
        text : str
            The input text string with extra spaces.

    Returns:
        cleaned_text : str
            The input text string with extra spaces removed.
    """
    cleaned_text = re.sub(r'\s+', ' ', text)
    return cleaned_text.strip()

def remove_characters(text: str, start_indices: list, end_indices: list) -> str:
    """
    Remove characters from a text string using lists of start and end indices.

    Args:
        text : str
            The input text string.
        start_indices : list of int
            A list of start indices indicating the positions from which characters should be removed.
        end_indices : list of int
            A list of end indices indicating the positions up to which characters should be removed.

    Returns:
        result : str
            The input text string with characters removed based on the specified indices.
    """
    if start_indices is None or len(start_indices) <1:
        return text
    if len(start_indices) != len(end_indices):
        print("ERROR - The number of start indices must be equal to the number of end indices.")
        return text

    result = ""
    current_start = 0

    for start, end in zip(start_indices, end_indices):
        if start < 0 or end > len(text) or start > end:
            print("ERROR - Invalid start or end indices")
            return text

        result += text[current_start:start]
        current_start = end + 1

    result += text[current_start:]

    return result


def load_stopwords_df(lang: str) -> pd.DataFrame:
    """
    Load a CSV file without header containing stopwords. If the file doesn't exist, it creates an empty file.

    Args:
        lang : str
            The language code used to identify the stopwords file.

    Returns:
        df : pandas DataFrame
            A DataFrame containing stopwords loaded from the file.
    """
    lexicon_dir = os.path.join(os.getcwd(), "lexicons")
    file_path = os.path.join(lexicon_dir, f"stop_words_{lang.lower()}.csv")

    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
    else:
        current_file_path = os.path.abspath(__file__)
        data_path = os.path.abspath(os.path.join(current_file_path, '..', '..', 'lexicons', f"stop_words_{lang.lower()}.csv"))
        if os.path.exists(data_path):
            create_dir(lexicon_dir)
            copy_file(data_path, lexicon_dir, f"stop_words_{lang.lower()}.csv")
            df = pd.read_csv(file_path)
        else:
            create_dir(lexicon_dir)
            df = pd.DataFrame(columns=['word'])
            df.to_csv(file_path, index=False)
            print("No stopwords list for this lang. New file created, use add_stopwords() to append words.")

    # df.rename(columns={0: 'word'}, inplace=True)
    df.sort_values(by="word", inplace=True)
    
    return df
    
def add_stopwords(lang: str, new_stopwords: list, lower: bool = True) -> pd.DataFrame:
    """
    Add a list of stopwords to an existing file. It removes duplicates.

    Args:
        lang : str
            The language code used to identify the stopwords file.
        new_stopwords : list of str
            The list of stopwords to add.
        lower : bool, optional
            Whether to convert the new stopwords to lowercase before adding. Default is True.

    Returns:
        new_df : pandas DataFrame
            A DataFrame containing the updated list of stopwords.
    """
    df = load_stopwords_df(lang)
    init_size = len(df.iloc[:, 0].unique())  # Selecting the first column

    if lower:
        new_stopwords_lowered = [x.lower() for x in new_stopwords]
        new_kw_list = list(set(list(df.iloc[:, 0].str.lower().unique()) + new_stopwords_lowered))  # Selecting the first column
    else:
        new_kw_list = list(set(list(df.iloc[:, 0].unique()) + new_stopwords))  # Selecting the first column

    new_df = pd.DataFrame({df.columns[0]: new_kw_list}).sort_values(by=df.columns[0])  # Selecting the first column

    added_kw = len(new_df.iloc[:, 0].unique()) - init_size  # Selecting the first column
    print(added_kw, "stop words added.")

    lexicon_dir = os.path.join(os.getcwd(), "lexicons")
    file_path = os.path.join(lexicon_dir, f"stop_words_{lang.lower()}.csv")
    new_df.to_csv(file_path, encoding="utf-8", index=False)
    return new_df

def remove_stopwords(lang: str, stopwords: list) -> pd.DataFrame:
    """
    Remove stopwords from an existing file.

    Args:
        lang : str
            The language code used to identify the stopwords file.
        stopwords : list of str
            The list of stopwords to remove.

    Returns:
        df : pandas DataFrame
            A DataFrame containing the updated list of stopwords after removal.
    """
    df = load_stopwords_df(lang)
    init_size = len(df.iloc[:, 0].unique())  # Selecting the first column
    df = df[~df.iloc[:, 0].isin(stopwords)].reset_index(drop=True)  # Selecting the first column
    removed_kw = init_size - len(df.iloc[:, 0].unique())  # Selecting the first column
    print(removed_kw, "stopwords removed")
    lexicon_dir = os.path.join(os.getcwd(), "lexicons")
    file_path = os.path.join(lexicon_dir, f"stop_words_{lang.lower()}.csv")
    df.to_csv(file_path,  encoding="utf-8", index=False)
    print("File saved -", file_path)
    return df

def keep_valid_filename_chars(text: str, replace: str = '') -> str:
    """
    Replace all characters not typically allowed in filenames with a specified replacement string.

    Args:
        text : str
            The input text string.
        replace : str, optional
            The string to replace invalid filename characters with. Default is an empty string.

    Returns:
        cleaned_text : str
            The input text string with invalid filename characters replaced.
    """
    return re.sub(r'[.<>:"/\\|?*\x00-\x1F]', replace, text)

    

def keep_alphanum_char(text: str, replace: str = '') -> str:
    """
    Replace all non-alphanumeric characters in a text string.

    Args:
        text : str
            The input text string.
        replace : str, optional
            The string to replace non-alphanumeric characters with. Default is an empty string.

    Returns:
        cleaned_text : str
            The input text string with non-alphanumeric characters replaced.
    """
    return re.sub("[^a-zA-Z0-9]", replace, text)


def substitute_punctuations_with_white_space(text : str) -> str:
    """
    Substitute punctuations with white spaces in the input string.

    Args:
        text (str): The input string.

    Returns:
        str: The modified string with punctuations replaced by white spaces.
    """
    text = re.sub(r"[%s]" % re.escape('!"#$%&\()*+,-./:;<=>?@[\\]^_`{|}~“…”’'), " ", text)
    return text

def translate_wt_libre(text: str, source: str, target: str, filename: str, dir_json: str, url: str = "http://127.0.0.1:5000/translate", format_payload="html") -> dict:
    """
    Translate text using LibreTranslate service.

    Args:
        text : str
            The text to be translated.
        source : str
            The source language code.
        target : str
            The target language code.
        filename : str
            The filename to save the translation result.
        dir_json : str
            The directory to save the translation result JSON file.
        url : str, optional
            The URL of the WT Libre translation service. Default is "http://127.0.0.1:5000/translate".
        format_payload : str, optional
            Possible values are html or text.

    Returns:
        json_data : dict
            The translation result in JSON format.
    """    
    headers = {"Content-Type": "application/json"}
    payload = {
        "q": text,
        "source": source,
        "target": target,
        "format": format_payload,
        "api_key": ""
    }

    file_path = os.path.join(dir_json , str(filename)+'.json')
    if not os.path.exists(file_path):
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        json_data = response.json()
        json_data['clean_text']=text
        write_json(json_data, dir_json , str(filename))
        return json_data
    
def translate_batch(batch_text: list, source: str, target: str, filename: str, dir_json: str, url: str = "http://127.0.0.1:5000/translate", format_payload="html") -> list:
    """
    Translate a batch of texts using LibreTranslate service.

    Args:
        batch_text : list of str
            The list of texts to be translated.
        source : str
            The source language code.
        target : str
            The target language code.
        filename : str
            The filename to save the translation results.
        dir_json : str
            The directory to save the translation result JSONL file.
        url : str, optional
            The URL of the WT Libre translation service. Default is "http://127.0.0.1:5000/translate".
        format_payload : str, optional
            Possible values are html or text.

    Returns:
        json_results : list of dict
            The translation results as a list of dictionaries containing 'translated_text' and 'clean_text'.
    """    
    headers = {"Content-Type": "application/json"}
    payload = {
        "q": batch_text,
        "source": source,
        "target": target,
        "format": format_payload,
        "api_key": ""
    }

    file_path = os.path.join(dir_json , str(filename)+'.json')
    if not os.path.exists(file_path):
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        json_data = response.json()
        json_results=[]
        for i, value in enumerate(json_data.get("translatedText", [])):
            v = {"translated_text" : value, "clean_text" : batch_text[i]}
            json_results.append(v)
       
        write_jsonl(json_results, dir_json , str(filename))
        return json_results

def translate(text: str, source: str, target: str, url: str = "http://127.0.0.1:5000/translate", format_payload="html") -> str:
    """
    Translate text using LibreTranslate service.

    Args:
        text : str
            The text to be translated.
        source : str
            The source language code.
        target : str
            The target language code.
        url : str, optional
            The URL of the translation service. Default is "http://127.0.0.1:5000/translate".
        format_payload : str, optional
            Possible values are html or text.

    Returns:
        translatedText : str
            The translated text.
    """
    headers = {"Content-Type": "application/json"}
    payload = {
        "q": text,
        "source": source,
        "target": target,
        "format": format_payload,
        "api_key": ""
    }

    response = requests.post(url, data=json.dumps(payload), headers=headers)
    json_data = response.json()
    translatedText = json_data.get("translatedText", "")
    return translatedText
    
def translate_row(df: pd.DataFrame, col: str, source: str = "auto", target: str = "en") -> pd.DataFrame:
    """
    Translate the text in a specific column of a DataFrame.

    Args:
        df : pandas DataFrame
            The DataFrame containing the text to be translated.
        col : str
            The name of the column containing the text to be translated.
        source : str, optional
            The source language code. Default is "auto".
        target : str, optional
            The target language code. Default is "en" (English).

    Returns:
        df : pandas DataFrame
            The DataFrame with an additional column containing the translated text.
    """
    translations =[]
    for i, row in df.iterrows():
        txt_to_translate = row[col].replace(' | ', ', ')
        txt_translated = translate(txt_to_translate, source="auto", target = "en")
        translations.append(txt_translated)
    df["translation_"+col]=translations
    return df

###################################################################
# METRICS
###################################################################

def cosine_similarity(a: np.array, b: np.array) -> float:
    """
    Calculate the cosine similarity between two vectors.

    Args:
        a : numpy array
            The first vector.
        b : numpy array
            The second vector.

    Returns:
        similarity : float
            The cosine similarity between the two vectors.
    """
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def approximate_tokens(text: str) -> int:
    """
    Approximate the number of tokens in a text.

    Args:
        text : str
            The input text.

    Returns:
        num_tokens : int
            The approximate number of tokens in the text.
    """
    return len(text.split(' '))

def approximate_unique_tokens(text: str) -> int:
    """
    Approximate the number of distinct tokens in a text.

    Args:
        text : str
            The input text.

    Returns:
        num_unique_tokens : int
            The approximate number of distinct tokens in the text.
    """
    return len(set(text.split(' ')))

def count_word_occurrences(text: str, word: str) -> int:
    """
    Count the occurrences of a word in a text.

    Args:
        text : str
            The input text.
        word : str
            The word to count occurrences of.

    Returns:
        occurrences : int
            The number of occurrences of the word in the text.
    """
    # Convert both text and word to lowercase for case-insensitive matching    
    word_lower = word.lower()

    # Use count() to find the number of occurrences
    occurrences = text.count(word_lower)
    
    return occurrences


def chi2_per_category(lst_text: list, lst_categorie: list, col_cat: str, n_words: int = 10, p_value_limit: float = 0.95, min_freq: int = 3) -> pd.DataFrame:
    """
    Calculate Chi-squared (Chi2) statistics per category based on the provided texts and corresponding categories.

    Args:
        lst_text : list
            List of texts for which Chi2 will be calculated.
        lst_categorie : list
            List of categories corresponding to each text.
        col_cat : str
            Name of the column for categories in the resulting DataFrame.
        n_words : int, optional
            Number of top words to display per category. Default is 10.
        p_value_limit : float, optional
            Threshold for p-values to filter significant words. Default is 0.95.
        min_freq : int, optional
            Minimum frequency threshold for word occurrences per class. Default is 3.

    Returns:
        DataFrame
            DataFrame containing the top words with their corresponding Chi2 scores, p-values, and word counts per class.

    Description:
        This function calculates Chi-squared (Chi2) statistics per category based on the provided texts and corresponding categories. 
        It identifies significant words that are most associated with each category, filtering out those with p-values greater than 
        the specified limit and those with word counts below the minimum frequency threshold.
    """
    count_vectorizer = CountVectorizer(token_pattern=r'[^\s]+')
    X_train_count = count_vectorizer.fit_transform(lst_text)
    X_names_count = count_vectorizer.get_feature_names_out()

    df_chi=pd.DataFrame()
    for cat in np.unique(lst_categorie):
        chi2_scores, p_values = chi2(X_train_count, lst_categorie == str(cat))
        word_count = X_train_count[lst_categorie == str(cat)].sum(axis=0) 
        df_chi_tmp = pd.DataFrame({col_cat: cat, "relevant_words_chi2": X_names_count, "chi2":chi2_scores, "p_values": 1 - p_values, "word_count_per_class":word_count.tolist()[0]}).sort_values(by="chi2", ascending=False).head(n_words)
        df_chi_tmp = df_chi_tmp[df_chi_tmp["p_values"]>p_value_limit]
        df_chi_tmp = df_chi_tmp[df_chi_tmp["word_count_per_class"]>min_freq]
        df_chi=pd.concat([df_chi, df_chi_tmp])

    df_chi.reset_index(drop=True)
    return df_chi

def word_frequency_per_categorie(df: pd.DataFrame, col_text: str, col_cat: str, ngram_range: tuple = (1, 1), stop_words: list = [], n_words: int = 20, min_freq: int = 3) -> pd.DataFrame:
    """
    Calculate word frequency per category.

    Args:
        df : pandas DataFrame
            DataFrame containing text data and corresponding categories.
        col_text : str
            Name of the column containing the text data.
        col_cat : str
            Name of the column containing the categories.
        ngram_range : tuple, optional
            The range for n-grams. Default is (1, 1) for unigrams.
        stop_words : list, optional
            List of stopwords to be ignored during frequency calculation. Default is an empty list.
        n_words : int, optional
            Number of top words to display per category. Default is 20.
        min_freq : int, optional
            Minimum frequency threshold for word occurrences per category. Default is 3.

    Returns:
        DataFrame
            DataFrame containing word frequencies per category.

    Description:
        This function calculates word frequencies per category based on the provided DataFrame, considering the text data and corresponding categories. 
        It filters out words with frequencies below the specified minimum frequency threshold and returns the top words for each category.
    """
    count_vectorizer = CountVectorizer(token_pattern=r'[^\s]+', ngram_range=ngram_range, stop_words=stop_words)
    X_train_count = count_vectorizer.fit_transform(df[col_text].to_list())
    X_names_count = count_vectorizer.get_feature_names_out()

    df_count = pd.DataFrame()
    for cat in np.unique(df[col_cat].tolist()):
        word_count = X_train_count[df[col_cat] == str(cat)].sum(axis=0)
        df_count_tmp = pd.DataFrame({col_cat: [cat]*len(X_names_count), "word": X_names_count, "freq": word_count.tolist()[0]}).sort_values(by="freq", ascending=False)
        if n_words:
            df_count_tmp=df_count_tmp.head(n_words)
        if min_freq:
            df_count_tmp=df_count_tmp[df_count_tmp["freq"]>min_freq]
        df_count = pd.concat([df_count, df_count_tmp])
    return df_count


def top_items_per_category(df: pd.DataFrame, col_lst: str = "hashtags", col_cat: str = "soft_topic", col_id: str = "tweet_id", n_items: int = 10) -> pd.DataFrame:
    """
    Count the occurrences of items (e.g., hashtags) per category and select the top items per category.

    Args:
        df : pandas DataFrame
            DataFrame containing data.
        col_lst : str, optional
            Name of the column containing lists of items (e.g., hashtags). Default is "hashtags".
        col_cat : str, optional
            Name of the column containing categories. Default is "soft_topic".
        col_id : str, optional
            Name of the column containing unique identifiers. Default is "tweet_id".
        n_items : int, optional
            Number of top items to select per category. Default is 10.

    Returns:
        DataFrame
            DataFrame containing the top items per category.

    Description:
        This function takes a DataFrame with a column containing lists of tokens (e.g., hashtags) and counts their occurrences grouped by a category.
        It then selects the most frequently occurring items per category based on the provided metric (e.g., volume of tweets).
    """
    df_count = (df[[col_cat, col_id, col_lst]].explode(col_lst)
            .groupby([col_cat, col_lst], group_keys=False)
            .agg({col_id:'nunique'})
            .reset_index()
            .groupby(col_cat, group_keys=False)
            .apply(lambda x: x.nlargest(n_items, col_id))
            .reset_index(drop=True)
            .groupby(col_cat, group_keys=False)
            .apply(lambda x: list(zip(x[col_lst], x[col_id])))
            .reset_index(name="top_"+col_lst)
            )
    return df_count

def topic_aggregate_chunks(df: pd.DataFrame, col_id: str, col_topic : str, col_chunk_id: str, col_engagement: str, col_user_id: str=None, metrics : dict =dict())-> pd.DataFrame:
    """
    Calculate the intermediate agregation of chunks per Post ID and topic

    Args:
        df : pandas DataFrame
            DataFrame containing processed data.
        col_id : str
            Name of the column containing unique posts identifiers.
        col_topic : str
            Name of the column containing topic labels.
        col_chunk_id : str
            Name of the column containing unique sentences identifiers.
        col_engagement : str
            Name of the column containing engagement metrics.
        col_user_id : str
            Name of the column containing user identifiers.
        metrics : dict
            Dictionary containing additional metrics to aggregate.

    Returns:
        DataFrame
            DataFrame containing the agregated posts per topic

    Description:
        This function aggregates various metrics for each post and topic, including verbatim counts, engagement sums, average word counts, occurrences of emojis, hashtags, and mentions, as well as unique counts for emojis, hashtags, and mentions. Additionally, it computes the average topic coordinates (x and y) if available. Finally, it calculates percentages for verbatims, engagements, users (if applicable), occurrences of emojis, hashtags, and mentions, and their respective combinations with verbatims.
    """
    metrics_dict = dict()
    # metrics_dict[col_id]=(col_id,'first')
    # if col_id != col_chunk_id:
    #     metrics_dict[col_chunk_id]=(col_chunk_id,"nunique")
    metrics_dict[col_chunk_id]=(col_chunk_id,"nunique")
    metrics_dict[col_engagement]=(col_engagement,'first')

    if col_user_id:
        metrics_dict[col_user_id]=(col_user_id,"first")
    if "sentiment" in df.columns:
        metrics_dict["sentiment"] = ("sentiment", "mean")
    if "sentiment_score" in df.columns:
        metrics_dict["sentiment_score"] = ("sentiment_score", "mean")

    metrics_dict["tokens_count"] = ("tokens_count", "sum")
    metrics_dict["lemmas_count"] = ("lemmas_count", "sum")
    metrics_dict["emojis_count"] = ("emojis_count", "sum")
    metrics_dict["unique_emojis"] = ("unique_emojis", lambda x: set(emoji for sublist in x for emoji in sublist))
    metrics_dict["unique_emojis_count"] = ("unique_emojis", len)
    metrics_dict["hashtags"] = ("hashtags", lambda x: list(hashtag for sublist in x for hashtag in sublist))
    metrics_dict["hashtags_count"] = ("hashtags_count", "sum")
    metrics_dict["mentions"] = ("mentions", lambda x: list(mention for sublist in x for mention in sublist))
    metrics_dict["mentions_count"] = ("mentions_count", "sum")
    metrics_dict["extracted_urls_from_text"] = ("extracted_urls_from_text", lambda x: list(url for sublist in x for url in sublist))
    metrics_dict["domain"] = ("domain", lambda x: list(domain for sublist in x for domain in sublist))
    metrics_dict["len_numbers"] = ("len_numbers", "sum")
    metrics_dict["interrogation"] = ("interrogation", "sum")
    metrics_dict["exclamation"] = ("exclamation", "sum")
    metrics_dict["x"] = ("x", "mean")
    metrics_dict["y"] = ("y", "mean")

    metrics_dict.update(metrics)

    df_gb = df.groupby([col_id, col_topic]).agg(**metrics_dict).reset_index()
    df_gb[col_topic]=df_gb[col_topic].astype(str)
    
    return df_gb

def sentiment_to_category(sentiment : float, boundaries : list = [-1.0, -0.5, 0.5, 1.0], labels :list = ['negative', 'neutral', 'positive']) -> str:
    """
    Assign a sentiment category to a sentiment score.

    Args:
        sentiment : float
            sentiment score
        boundaries : list
            list of boundaries for each category
        labels : list
            list of labels for each category

    Returns:
        str
            category label

    Description:
        This function assigns a sentiment category to a sentiment score based on a list of boundaries and labels. If the sentiment score is outside the boundaries, it is assigned to the last category.
    """
    for i in range(len(boundaries) - 1):
        if boundaries[i] <= sentiment < boundaries[i + 1]:
            return labels[i]
    return labels[-1] 


def topic_representation(df: pd.DataFrame, col_topic: str, col_id: str, col_engagement: str, col_user_id: str, metrics: dict) -> pd.DataFrame:
    """
    Calculate the representation of topics in a processed DataFrame.

    Args:
        df_processed_data : pandas DataFrame
            DataFrame containing processed data.
        col_topic : str
            Name of the column containing topic labels.
        col_id : str
            Name of the column containing unique identifiers.
        col_engagement : str
            Name of the column containing engagement metrics.
        col_user_id : str
            Name of the column containing user identifiers.
        metrics : dict
            Dictionary containing additional metrics to aggregate.

    Returns:
        DataFrame
            DataFrame containing the representation of topics.

    Description:
        This function aggregates various metrics for each topic, including verbatim counts, engagement sums, average word counts, occurrences of emojis, hashtags, and mentions, as well as unique counts for emojis, hashtags, and mentions. Additionally, it computes the average topic coordinates (x and y) if available. Finally, it calculates percentages for verbatims, engagements, users (if applicable), occurrences of emojis, hashtags, and mentions, and their respective combinations with verbatims.
    """
    #on s'assure que les colonnes de métriques soient bien complètes et en float
    # df_processed_data[metrics]=df_processed_data[metrics].fillna(0).astype(float) 

    #on crée un dictionnaire contenant les agrégations
    metrics_dict = dict()
    metrics_dict['verbatims']=(col_id,'nunique')
    metrics_dict['engagements']=(col_engagement,'sum')
    if col_user_id:
        metrics_dict["users"]=(col_user_id,"nunique")
        panel_cols = [col for col in df.columns if col[:6] == 'panel_']
        if len(panel_cols)>0:
            for panel_col in panel_cols:
                metrics_dict[panel_col+'_verbatims'] = (panel_col, "sum")
                metrics_dict[panel_col+'_users'] = (col_user_id, lambda x : x[df[panel_col]].nunique())
                metrics_dict[panel_col+'_engagements'] = (col_engagement, lambda x : x[df[panel_col]].sum())

    metrics_dict.update(metrics)

    metrics_dict['avg_word_count']=("tokens_count", lambda x: round(x.mean(),2))
    metrics_dict['verbatims_with_emoji']=("emojis_count", lambda x: (x > 0).sum() )
    metrics_dict['emojis_occurences']=("emojis_count", "sum")
    metrics_dict['unique_emojis']=("unique_emojis", lambda x: len(set(emoji for sublist in x for emoji in sublist)))
    metrics_dict['unique_hashtags']=("hashtags", lambda x: len(set(hashtag for sublist in x for hashtag in sublist)))
    metrics_dict['verbatims_with_hashtags']=("hashtags_count", lambda x: (x > 0).sum() )
    metrics_dict['hashtags_occurences']=("hashtags_count", "sum")
    metrics_dict['unique_mentions']=("mentions", lambda x: len(set(mention for sublist in x for mention in sublist)))
    metrics_dict['verbatims_with_mentions']=("mentions_count", lambda x: (x > 0).sum() )
    metrics_dict['mentions_occurences']=("mentions_count", "sum")
    metrics_dict['verbatims_with_numbers']= ("len_numbers", lambda x: (x > 0).sum())
    metrics_dict['verbatims_with_interrogation']=("interrogation", "sum")
    metrics_dict['verbatims_with_exclamation']=("exclamation", "sum")
    metrics_dict['topic_x']=("x", "mean")
    metrics_dict['topic_y']=("y", "mean")

    # on produit la représentation des topics finale
    df_distrib_all = (df.groupby(col_topic)
                      .agg(**metrics_dict)
                      .sort_values(by="verbatims", ascending=False)
                      .assign(engagement_per_verbatims = lambda x : x["engagements"] / x["verbatims"])
                      .assign(verbatims_per_user = lambda x : x["verbatims"] / x["users"] if col_user_id else 0)
                      .assign(engagement_per_user = lambda x : x["engagements"] / x["users"] if col_user_id else 0)
                      .assign(percentage_verbatims = lambda x : x["verbatims"] / x["verbatims"].sum())
                      .assign(percentage_engagement = lambda x : x["engagements"] / x["engagements"].sum())
                      .assign(percentage_users = lambda x : x["users"] / x["users"].sum() if col_user_id else 0)
                      .assign(percentage_verbatims_with_emoji = lambda x : x["verbatims_with_emoji"] / x["verbatims"])
                      .assign(percentage_verbatims_with_hashtags = lambda x : x["verbatims_with_hashtags"] / x["verbatims"])  
                      .assign(percentage_verbatims_with_mentions = lambda x : x["verbatims_with_mentions"] / x["verbatims"])
                      .assign(percentage_verbatims_with_numbers = lambda x : x["verbatims_with_numbers"] / x["verbatims"])
                      .assign(percentage_verbatims_with_numbers = lambda x : x["verbatims_with_interrogation"] / x["verbatims"])
                      .assign(percentage_verbatims_with_numbers = lambda x : x["verbatims_with_exclamation"] / x["verbatims"])
                      .reset_index())

    df_distrib_all[col_topic]=df_distrib_all[col_topic].astype(str)
    return df_distrib_all

def generic_representation(df_processed_data: pd.DataFrame, col_gb: str, col_id: str, col_engagement: str, col_user_id: str = None, metrics: dict = {}) -> pd.DataFrame:
    """
    Calculate a generic representation of data based on grouping by a specified column.

    Args:
        df_processed_data : pandas DataFrame
            DataFrame containing processed data.
        col_gb : str
            Name of the column to group by.
        col_id : str
            Name of the column containing unique identifiers.
        col_engagement : str
            Name of the column containing engagement metrics.
        col_user_id : str, optional
            Name of the column containing user identifiers. Default is None.
        metrics : dict, optional
            Dictionary containing additional metrics to aggregate. Default is an empty dictionary.

    Returns:
        DataFrame
            DataFrame containing the generic representation of data.

    Description:
        This function aggregates various metrics for each group, including verbatim counts, engagement sums, and any additional metrics provided in the `metrics` parameter. It also computes derived metrics such as verbatims per user and engagement per verbatim. Finally, it calculates percentages for verbatims, engagements, and users (if applicable) within each group.
    """
    #on crée un dictionnaire contenant les agrégations
    metrics_dict = dict()
    metrics_dict['verbatims']=(col_id,'nunique')
    metrics_dict['engagements']=(col_engagement,'sum')
    if col_user_id:
        metrics_dict["users"]=(col_user_id,"nunique")
        
    metrics_dict.update(metrics)

    # on produit la représentation 
    df_distrib_all = (df_processed_data.groupby(col_gb)
                      .agg(**metrics_dict)
                      .sort_values(by="verbatims", ascending=False)
                      .assign(verbatims_per_user = lambda x : x["verbatims"] / x["users"] if col_user_id else 0)
                      .assign(engagement_per_verbatims = lambda x : x["engagements"] / x["verbatims"])
                      .assign(engagement_per_user = lambda x : x["engagements"] / x["users"] if col_user_id else 0)
                      .assign(percentage_verbatims = lambda x : x["verbatims"] / x["verbatims"].sum())
                      .assign(percentage_engagement = lambda x : x["engagements"] / x["engagements"].sum())
                      .assign(percentage_users = lambda x : x["users"] / x["users"].sum() if col_user_id else 0)
                      .reset_index())

    return df_distrib_all

def create_frequency_table(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """
    Create a frequency table for a given column in a DataFrame.

    Args:
        df : pandas DataFrame
            DataFrame containing the data.
        col : str
            Name of the column for which the frequency table is to be created.

    Returns:
        pandas DataFrame
            DataFrame containing the frequency table.

    Description:
        This function generates a frequency table for the specified column in the DataFrame. It sorts the DataFrame by the specified column in descending order, calculates the rank of each entry, and assigns dense ranks both ascending and descending.
    """
    df_frequency=(df.sort_values(col, ascending=False)
                  .reset_index(drop=True)
                  .reset_index()
                  .assign(rank=lambda x: x['index'] + 1)
                  .drop(columns=['index'])
                  .assign(rank_dense=lambda x: x[col].rank(method='dense', ascending=False).astype(int))
                  .assign(rank_dense_asc=lambda x: x[col].rank(method='dense', ascending=True).astype(int))
                 )
    return df_frequency

###################################################################
# SAMPLING
###################################################################

def calculate_sample(len_df: int, n_rows: float) -> int:
    """
    Convert a percentage to the number of rows to sample.

    Args:
        len_df : int
            Length of the DataFrame.
        n_rows : float
            Number of rows to sample. If less than or equal to 1, it's treated as a percentage.

    Returns:
        int
            Number of rows to sample.

    """
    if 0 < n_rows <= 1 :
        top_rows = int(n_rows * len_df)
        return top_rows
    elif n_rows > 1 or n_rows == 0:
        top_rows = n_rows
        return top_rows
    else :
        print("ERREUR - paramètre du sampling incorrect")
    
def sampling_by_engagement(df: pd.DataFrame, col_engagement: str, top_rows: float = 0.3, sample_size: float = 0.5) -> pd.DataFrame:
    """
    Create a sample dataset by keeping a part of the top publications based on engagement metrics.
    This function generates a sample dataset by keeping a portion of the top publications based on engagement metrics. It sorts the dataset by the specified engagement metric, keeps the top `top_rows` rows, and then samples the remaining rows to achieve the desired `sample_size`. The final sample is shuffled for randomness

    Args:
        df : pandas.DataFrame
            The original DataFrame.
        col_engagement : str
            The column name containing the engagement metrics.
        top_rows : float, optional
            The number of "most engaging" rows to keep. Values could be either an integer or a float between 0 and 1 (= sample a percentage). Default is 0.3.
        sample_size : float, optional
            The final size of the sample. Ex: 1000 rows from an original dataset of 100000 rows. Values could be either an integer or a float between 0 and 1 (= sample a percentage). Default is 0.5.

    Returns:
        pandas.DataFrame
            The sampled DataFrame.

    """
    
    sample_rows = calculate_sample(len(df), sample_size)  
    top_rows = calculate_sample(sample_rows, top_rows)

    print(sample_rows, top_rows)
    print("TOP ROWS:", top_rows, "- SAMPLE SIZE:", sample_rows)

    if sample_rows < len(df):
        if sample_rows < top_rows:
            raise ValueError("sample_size must be higher than top_rows")    

        df = df.sort_values(by=col_engagement, ascending = False) #sort dataset by metric
        df_head = df.head(top_rows) # keep the most engaging rows
        df_tail = df[top_rows:].sample(sample_rows-top_rows, random_state = 42) #sample the tail
        df_sample = pd.concat([df_head, df_tail]).sample(frac=1, random_state=42).reset_index(drop=True) #create a new df and shuffle rows
        return df_sample
    else:
        return df
    
def sample_most_engaging_posts(df: pd.DataFrame, col_topic: str, col_engagement: str, sample_size: float = 0.1, min_size: int = 10) -> pd.DataFrame:
    """
    Perform a "stratified sample" of the most engaging content per topic, ensuring a minimum number of items per group.

    Args:
        df : pandas.DataFrame
            The DataFrame containing the data.
        col_topic : str
            The column name containing the topic information.
        col_engagement : str
            The column name containing the engagement metrics.
        sample_size : float, optional
            The size of the sample relative to the total data. Default is 0.1 (10%).
        min_size : int, optional
            The minimum number of items to retain per group. Default is 10.

    Returns:
        pandas.DataFrame
            The sampled DataFrame.

    """
    df = (df.groupby(col_topic, group_keys=False)
          .apply(lambda x: x.sort_values(by=col_engagement, ascending=False)
                 .head(max(min_size, int(len(x)*sample_size)))
                 )
        )
    return df

###################################################################
# SPACY
###################################################################

def get_lang_detector(nlp, name):
    return LanguageDetector(seed=42)  # We use the seed 42

def PRarmy_nlp_process(nlp, df: pd.DataFrame, col_text: str, col_lemma: str = "lemmatized_text", pos_to_keep: list = ["VERB","NOUN","ADJ", "ADV", "PROPN"], entities_to_keep: list = ['PERSON','ORG', 'LOC'], stopwords: list = [], batch_size: int = 100, n_process: int = 1) -> pd.DataFrame:
    """ 
    Perform natural language processing tasks using spaCy for PR Army project.
    Its main tasks are lemmatization and named entity recognition (NER).

    Args:
        nlp : spacy.Language
            The spaCy language model.
        df : pandas.DataFrame
            The DataFrame containing the text data.
        col_text : str
            The name of the column containing the text data.
        col_lemma : str
            The name of the column to store the lemmatized text data.
        pos_to_keep : list
            A list of part-of-speech tags to keep during lemmatization.
        entities_to_keep : list
            A list of NER tags to keep.
        stopwords : list
            A list of stopwords to remove during processing.
        batch_size : int, optional
            The batch size for spaCy processing. Default is 100.
        n_process : int, optional
            The number of processes for parallel processing. Default is 1.
    Returns:
        pandas.DataFrame
            The DataFrame with processed text data.

    """
    all_records = []
    text=list(df[col_text].astype('unicode').values)

    for doc in tqdm(nlp.pipe(text, batch_size=batch_size, n_process=n_process), total= len(text), desc = "NLP Process"):
        NER_type = []
        NER_text = []

        ### LEMMATIZATION

        if len(pos_to_keep)>0 and len(stopwords)>0:
            lemmas_list = [str(tok.lemma_).lower() for tok in doc if not (tok.is_punct or tok.is_space) and tok.text.lower() not in stopwords and tok.pos_ in pos_to_keep] 
        elif len(pos_to_keep)>0 and len(stopwords) < 1:
            lemmas_list = [str(tok.lemma_).lower() for tok in doc if not (tok.is_punct or tok.is_space) and tok.pos_ in pos_to_keep] 
        elif len(pos_to_keep) < 1 and len(stopwords) > 0:
            lemmas_list = [str(tok.lemma_).lower() for tok in doc if not (tok.is_punct or tok.is_space) and tok.text.lower() not in stopwords] 
        else :
            lemmas_list = [str(tok.lemma_).lower() for tok in doc if not (tok.is_punct or tok.is_space)] 

        ### NER 
        if len(entities_to_keep)>0:
            for ent in doc.ents:
                if ent.label_ in entities_to_keep:
                    NER_type.append(ent.label_)
                    NER_text.append(ent.text)

        else:
            for ent in doc.ents:
                NER_type.append(ent.label_)
                NER_text.append(ent.text)

        
        record = (NER_type, NER_text, ' '.join(map(str, lemmas_list)))
        all_records.append(record)



    df[['NER_type', 'NER_text', col_lemma]] = pd.DataFrame(all_records, index=df.index)

    return df

def TM_nlp_process(nlp, df: pd.DataFrame, col_text: str, col_lemma: str, pos_to_keep: list, stopwords: list, batch_size: int = 100, n_process: int = 1, stats: bool = True, join_list: bool = False) -> pd.DataFrame:
    """ 
    Perform natural language processing tasks using spaCy for topic modeling.

    Args:
        nlp : spacy.Language
            The spaCy language model.
        df : pandas.DataFrame
            The DataFrame containing the text data.
        col_text : str
            The name of the column containing the text data.
        col_lemma : str
            The name of the column to store the lemmatized text data.
        pos_to_keep : list
            A list of part-of-speech tags to keep during lemmatization.
        stopwords : list
            A list of stopwords to remove during processing.
        batch_size : int, optional
            The batch size for spaCy processing. Default is 100.
        n_process : int, optional
            The number of processes for parallel processing. Default is 1.
        stats : bool, optional
            Whether to compute and store additional statistics. Default is True.
        join_list : bool, optional
            Whether to join the lemmas into a single string. Default is False.

    Returns:
        pandas.DataFrame
            The DataFrame with processed text data.

    """
    all_lemmas=[]
    tokens_counts=[]
    tokens_kept=[]
    all_emojis=[]
    all_unique_emojis=[]
    emojis_counts=[]
    unique_emojis_count=[]

    text=list(df[col_text].astype('unicode').values)

    for doc in tqdm(nlp.pipe(text, batch_size=batch_size, n_process=n_process), total= len(text), desc = "NLP Process"):

        emojis=[str(token) for token in doc if token._.is_emoji]
        unique_emojis=list(set(emojis))
        all_emojis.append(emojis)
        all_unique_emojis.append(unique_emojis)

        if len(pos_to_keep)>0 and len(stopwords)>0:
            lemmas_list = [str(tok.lemma_).lower() for tok in doc if not (tok.is_punct or tok.is_space) and tok.text.lower() not in stopwords and tok.pos_ in pos_to_keep] 
        elif len(pos_to_keep)>0 and len(stopwords) < 1:
            lemmas_list = [str(tok.lemma_).lower() for tok in doc if not (tok.is_punct or tok.is_space) and tok.pos_ in pos_to_keep] 
        elif len(pos_to_keep) < 1 and len(stopwords) > 0:
            lemmas_list = [str(tok.lemma_).lower() for tok in doc if not (tok.is_punct or tok.is_space) and tok.text.lower() not in stopwords] 
        else :
            lemmas_list = [str(tok.lemma_).lower() for tok in doc if not (tok.is_punct or tok.is_space)] 
            
        all_lemmas.append(lemmas_list)

        if stats:
            tokens_counts.append(len(doc))
            emojis_counts.append(len(emojis))
            unique_emojis_count.append(len(unique_emojis))
            tokens_kept.append(len(lemmas_list))
            
    if join_list:
        df[col_lemma]=[' '.join(map(str, l)) for l in all_lemmas]    
    else:
        df[col_lemma]=all_lemmas
    if stats:
        df["tokens_count"]=tokens_counts
        df["emojis_count"]=emojis_counts
        df["unique_emojis_count"]=unique_emojis_count
        df["lemmas_count"]=tokens_kept

    df["emojis"]=all_emojis
    df["unique_emojis"]=all_unique_emojis
    
    return df


def load_spacy_model(model: str, disable_components: list = ["transformer", "morphologizer", "trainable_lemmatizer", "textcat_multilabel", "textcat", "entity_ruler", "entity_linker"], lang_detect: bool = False, emoji: bool = False) -> spacy.language.Language:
    """
    Load a spaCy model with optional configurations. This function loads a spaCy model with optional configurations such as disabling specific components, enabling emoji parsing, 
        and enabling language detection. It first loads the spaCy model specified by the 'model' parameter and then applies 
        additional configurations based on the provided flags.

        If 'disable_components' is provided, the specified spaCy components will be disabled. If 'lang_detect' is set to True, 
        language detection will be enabled using the 'get_lang_detector' function. If 'emoji' is set to True, the emoji component 
        will be included in the spaCy pipeline.

    Args:
        model : str
            Name of the spaCy model to load.
        disable_components : list, optional
            List of spaCy components to disable. Default is ["transformer", "morphologizer", "trainable_lemmatizer", "textcat_multilabel", "textcat", "entity_ruler", "entity_linker"].
        lang_detect : bool, optional
            Flag indicating whether language detection should be enabled. Default is False.
        emoji : bool, optional
            Flag indicating whether to include the emoji component in the spaCy pipeline. Default is False.

    Returns:
        nlp : spacy.language.Language
            Loaded spaCy language processing pipeline.
        
    """
    if torch.cuda.is_available():
        
        spacy.prefer_gpu()

    if len(disable_components)>0:
        nlp = spacy.load(model, disable=disable_components)
    else:
        nlp = spacy.load(model)

    if emoji:
        nlp.add_pipe("emoji", first=True)
    
    if lang_detect:
        Language.factory("language_detector", func=get_lang_detector)
        nlp.add_pipe('language_detector', last=True)

    return nlp

def get_labels(nlp: spacy.language.Language, pipe_step: str = "ner", explanations: bool = False) -> pd.DataFrame:
    """ 
    Return labels associated with a pipeline step and optionally provide explanations.This function retrieves the labels associated with a specific pipeline step of the spaCy language processing pipeline. It returns a DataFrame containing the labels. If 'explanations' is set to True, explanations for each label are also included.
    Args:
        nlp : spacy.language.Language. The spaCy language processing pipeline.
        pipe_step : str, optional. The pipeline step for which labels are retrieved. Default is "ner".
        explanations : bool, optional. Flag indicating whether to include explanations for the labels. Default is False.

    Returns:
        DataFrame : DataFrame containing the labels associated with the specified pipeline step.
        
    """
    pipe_details=nlp.get_pipe(pipe_step)
    labels=list(pipe_details.labels)
    df=pd.DataFrame({'label':labels})
    if explanations:
        descriptions=[spacy.explain(label) for label in labels]
        df['explanation']=descriptions

    return df


def spacy_langdetect(nlp, df: pd.DataFrame, col_text: str, batch_size: int = 100, n_process: int = 1) -> pd.DataFrame:
    """
    Detect language and return a score.This function uses spaCy's language detection capabilities to detect the language of text data in a DataFrame.It returns a DataFrame containing the detected languages and their scores, which indicate the confidence levelof the language detection for each text.

    Args:
        nlp : spacy.language.Language
            The spaCy language processing pipeline with language detection enabled.
        df : pd.DataFrame
            DataFrame containing the text data to analyze.
        col_text : str
            The name of the column containing the text data.
        batch_size : int, optional
            The batch size for processing texts. Default is 100.
        n_process : int, optional
            The number of processes to use for language detection. Default is 1.

    Returns:
        pd.DataFrame
            DataFrame containing the detected languages and their scores.
        
    """
    text=list(df[col_text].astype('unicode').values)

    languages=[]
    for doc in tqdm(nlp.pipe(text, batch_size=batch_size, n_process=n_process), total= len(text), desc = "Language detection"):
        lang=doc._.language.get("language")
        score =doc._.language.get("score")
        languages.append((lang, score))

    df[['detected_language','score']]=languages

    return df

def extract_noun_chunks(nlp, df: pd.DataFrame, col_text: str, batch_size: int = 100, n_process: int = 1, stats: bool = False) -> pd.DataFrame:
    """
    Spacy implementation to extract noun chunks.

    Parameters:
        nlp : spacy.language.Language
            The spaCy language processing pipeline.
        df : pd.DataFrame
            DataFrame containing the text data to analyze.
        col_text : str
            The name of the column containing the text data.
        batch_size : int, optional
            The batch size for processing texts. Default is 100.
        n_process : int, optional
            The number of processes to use for text processing. Default is 1.
        stats : bool, optional
            Flag indicating whether to compute statistics about the noun chunks. Default is False.

    Returns:
        pd.DataFrame
            DataFrame containing the extracted noun chunks and their statistics if enabled.

    Description:
        This function utilizes spaCy's noun chunk extraction capabilities to extract noun chunks from text data in a DataFrame.
        It returns a DataFrame containing the extracted noun chunks for each text. Optionally, it can compute statistics such
        as the count of noun chunks and unique noun chunks if the 'stats' parameter is set to True.
    """
    all_chunks = []
    all_unique_chunks =[]
    chunks_count=[]
    unique_chunks_count=[]
    text=list(df[col_text].astype('unicode').values)

    for doc in tqdm(nlp.pipe(text, batch_size=batch_size, n_process=n_process), total= len(text), desc = "Noun Chunks extraction"):
        chunks=[chunk.text for chunk in doc.noun_chunks]
        unique_chunks=list(set(chunks))
        all_chunks.append(chunks)
        all_unique_chunks.append(unique_chunks)
        
        if stats:
            chunks_count.append(len(chunks))
            unique_chunks_count.append(len(unique_chunks))

    df['noun_chunks']=all_chunks
    df['unique_noun_chunks']=all_chunks
    if stats:
        df['noun_chunks_count']=chunks_count
        df['unique_noun_chunks_count']=unique_chunks_count
    return df

def extract_emojis(nlp, df: pd.DataFrame, col_text: str, batch_size: int = 100, n_process: int = 1, stats: bool = True) -> pd.DataFrame:
    """ 
    Spacy implementation to extract emojis
    
    Parameters:
        nlp : spacy.language.Language
            The spaCy language processing pipeline.
        df : pd.DataFrame
            DataFrame containing the text data to analyze.
        col_text : str
            The name of the column containing the text data.
        batch_size : int, optional
            The batch size for processing texts. Default is 100.
        n_process : int, optional
            The number of processes to use for text processing. Default is 1.
        stats : bool, optional
            Flag indicating whether to compute statistics about the emojis. Default is True.

    Returns:
        pd.DataFrame
            DataFrame containing the extracted emojis and their statistics if enabled.

    Description:
        This function utilizes spaCy's emoji detection capabilities to extract emojis from text data in a DataFrame.
        It returns a DataFrame containing the extracted emojis for each text. Optionally, it can compute statistics such
        as the count of emojis and unique emojis if the 'stats' parameter is set to True.
    """
    all_emojis=[]
    all_unique_emojis=[]
    emojis_counts=[]
    unique_emojis_count=[]

    text=list(df[col_text].astype('unicode').values)

    for doc in tqdm(nlp.pipe(text, batch_size=batch_size, n_process=n_process), total= len(text), desc = "Emojis detection"):
        emojis=[str(token) for token in doc if token._.is_emoji]
        unique_emojis=list(set(emojis))
            
        all_emojis.append(emojis)
        all_unique_emojis.append(unique_emojis)

        if stats:
            emojis_counts.append(len(emojis))
            unique_emojis_count.append(len(unique_emojis))
        
    df["emojis"]=all_emojis
    df["unique_emojis"]=all_unique_emojis
    if stats:
        df["emojis_count"]=emojis_counts
        df["unique_emojis_count"]=unique_emojis_count
    
    return df

def split_n_sentences(nlp, df: pd.DataFrame, col_text: str, n_sentences: int = 1, batch_size: int = 100, n_process: int = 1, stats: bool = False, threshold: int = None) -> pd.DataFrame:
    """
    Split a text into chunks of n sentences, returning their start and end indexes in separate columns.

    Parameters:
        nlp : spacy.language.Language
            The spaCy language processing pipeline.
        df : pd.DataFrame
            DataFrame containing the text data to split.
        col_text : str
            The name of the column containing the text data.
        n_sentences : int, optional
            The number of sentences to group together. Default is 1.
        batch_size : int, optional
            The batch size for processing texts. Default is 100.
        n_process : int, optional
            The number of processes to use for text processing. Default is 1.
        stats : bool, optional
            Flag indicating whether to compute statistics about the splitting process. Default is False.
        threshold : int, optional
            Maximum number of sentence batches to return per text. If None, all batches are returned. Default is None.

    Returns:
        pd.DataFrame
            DataFrame containing the split sentences with their start and end indexes in separate columns.

    """
    text = list(df[col_text].astype('unicode').values)

    count_sentences = []
    count_batches = []
    results = []
    start_indexes = []
    end_indexes = []

    for doc in tqdm(nlp.pipe(text, batch_size=batch_size, n_process=n_process), total=len(text), desc="Sentence splitting"):
        sentences = []


        # Extract sentences and their positions
        for sent in doc.sents:
            sentences.append((sent.text, sent.start_char, sent.end_char))

        if stats:
            count_sentences.append(len(sentences))

        if n_sentences > 1:
            # # Split sentences into batches of size n_sentences
            batches = [sentences[i:i + n_sentences] for i in range(0, len(sentences), n_sentences)]

            # Concatenate batches of sentences and adjust spans accordingly
            concatenate_batches = [" ".join([sub[0] for sub in sublist]) for sublist in batches]
            concatenate_spans = [(sublist[0][1], sublist[-1][2]) for sublist in batches]

            if threshold is not None:
                concatenate_batches = concatenate_batches[:threshold]
                concatenate_spans = concatenate_spans[:threshold]

            results.append(concatenate_batches)
            start_indexes.append([span[0] for span in concatenate_spans])
            end_indexes.append([span[1] for span in concatenate_spans])

            if stats:
                count_batches.append(len(concatenate_batches))
        else:
            sentences = sentences[:threshold] if threshold is not None else sentences

            results.append([sub[0] for sub in sentences])
            start_indexes.append([sub[1] for sub in sentences])
            end_indexes.append([sub[2] for sub in sentences])

    df['sentences'] = results
    df['start_indexes'] = start_indexes
    df['end_indexes'] = end_indexes

    df = df.explode(['sentences','start_indexes', 'end_indexes']).reset_index(drop=True)

    return df


def split_n_sentences_nltk(df: pd.DataFrame, col_text: str, n_sentences: int = 1, threshold: int = None, stats: bool = False) -> pd.DataFrame:
    """
    Split a text into chunks of n sentences, returning their start and end indexes in separate columns using NLTK PunktSentenceTokenizer.

    Parameters:
        df : pd.DataFrame
            DataFrame containing the text data to split.
        col_text : str
            The name of the column containing the text data.
        n_sentences : int, optional
            The number of sentences to group together. Default is 1.
        threshold : int, optional
            Maximum number of sentence batches to return per text. If None, all batches are returned. Default is None.
        stats : bool, optional
            Flag indicating whether to compute statistics about the splitting process. Default is False.

    Returns:
        pd.DataFrame
            DataFrame containing the split sentences with their start and end indexes in separate columns.

    """
    tokenizer = PunktSentenceTokenizer()
    text = list(df[col_text].astype('unicode').values)

    count_sentences = []
    count_batches = []
    results = []
    start_indexes = []
    end_indexes = []

    for doc in tqdm(text, total=len(text), desc="Sentence splitting"):
        sentences = []
        start_pos = 0

        # Tokenize sentences and compute positions
        for sent in tokenizer.tokenize(doc):
            start_idx = doc.find(sent, start_pos)
            end_idx = start_idx + len(sent)
            sentences.append((sent, start_idx, end_idx))
            start_pos = end_idx

        if stats:
            count_sentences.append(len(sentences))

        if n_sentences > 1:
            # Split sentences into batches of size n_sentences
            batches = [sentences[i:i + n_sentences] for i in range(0, len(sentences), n_sentences)]

            # Concatenate batches of sentences and adjust spans accordingly
            concatenate_batches = [" ".join([sub[0] for sub in sublist]) for sublist in batches]
            concatenate_spans = [(sublist[0][1], sublist[-1][2]) for sublist in batches]

            if threshold is not None:
                concatenate_batches = concatenate_batches[:threshold]
                concatenate_spans = concatenate_spans[:threshold]

            results.append(concatenate_batches)
            start_indexes.append([span[0] for span in concatenate_spans])
            end_indexes.append([span[1] for span in concatenate_spans])

            if stats:
                count_batches.append(len(concatenate_batches))
        else:
            sentences = sentences[:threshold] if threshold is not None else sentences

            results.append([sub[0] for sub in sentences])
            start_indexes.append([sub[1] for sub in sentences])
            end_indexes.append([sub[2] for sub in sentences])

    df['sentences'] = results
    df['start_indexes'] = start_indexes
    df['end_indexes'] = end_indexes

    df = df.explode(['sentences', 'start_indexes', 'end_indexes']).reset_index(drop=True)

    return df


def spacy_NER(nlp, df: pd.DataFrame, col_text: str, entities_to_keep: list = ['PERSON','ORG'], explode: bool = True, batch_size : int = 100, n_process: int =1) -> pd.DataFrame:
    """
    Spacy implementation of NER. 
    To define entities type to keep, call get_labels(nlp, pipe_step="ner", explanations=False)
    explode = False means it returns 1 list of entities per document
    explode = True means it returns 1 entity per row
    
    Args:
        nlp : spacy.language.Language
            The spaCy language processing pipeline.
        df : pd.DataFrame
            DataFrame containing the text data.
        col_text : str
            The name of the column containing the text data.
        entities_to_keep : list, optional
            List of entity types to keep. Default is ['PERSON','ORG'].
        explode : bool, optional
            Flag indicating whether to explode the DataFrame to have one entity per row. Default is True.
        batch_size : int, optional
            Batch sizes
        n_process : int, optional
            Number of processes
    
    Returns:
        pd.DataFrame
            DataFrame containing the NER information.

    Description:
        This function performs Named Entity Recognition (NER) using spaCy on a DataFrame with text data. It extracts entities of the specified types 
        and stores the NER information in separate columns. If 'explode' is set to True, it returns one entity per row in the DataFrame.
    """
    l_text = df[col_text].tolist()
    all_records = []
    for doc in tqdm(nlp.pipe(l_text, batch_size=batch_size, n_process=n_process), total= len(l_text), desc = "NLP Process"):
        NER_type = []
        NER_text = []
        NER_start_char = []
        NER_end_char=[]
        # entities_data = []

        if len(entities_to_keep)>0:
            for ent in doc.ents:
                if ent.label_ in entities_to_keep:
                    NER_type.append(ent.label_)
                    NER_text.append(ent.text)
                    NER_start_char.append(ent.start_char)
                    NER_end_char.append(ent.end_char)
                    # entities_data.append([ent.label_, ent.text, ent.start_char, ent.end_char])
        else:
            for ent in doc.ents:
                NER_type.append(ent.label_)
                NER_text.append(ent.text)
                NER_start_char.append(ent.start_char)
                NER_end_char.append(ent.end_char)
                # entities_data.append([ent.label_, ent.text, ent.start_char, ent.end_char])
        record = (NER_type, NER_text, NER_start_char, NER_end_char)
        all_records.append(record)

    df[['NER_type', 'NER_text','NER_start_char','NER_end_char']] = pd.DataFrame(all_records, index=df.index)

    if explode:
        df= df.explode(['NER_type', 'NER_text','NER_start_char','NER_end_char'])

    return df

def tokenize(nlp, df: pd.DataFrame, col_text: str, col_tokens: str, pos_to_keep: list, stopwords: list, batch_size: int = 100, n_process: int = 1, stats: bool = True) -> pd.DataFrame:
    """ 
    Spacy implementation to tokenize text
    
    Parameters:
        nlp : spacy.language.Language
            The spaCy language processing pipeline.
        df : pd.DataFrame
            DataFrame containing the text data.
        col_text : str
            The name of the column containing the text data.
        col_tokens : str
            The name of the column to store the tokenized text.
        pos_to_keep : list
            List of POS tags to keep.
        stopwords : list
            List of stopwords to exclude from tokens.
        batch_size : int, optional
            Batch size for processing. Default is 100.
        n_process : int, optional
            Number of processes for parallel processing. Default is 1.
        stats : bool, optional
            Flag indicating whether to calculate and store statistics. Default is True.
    
    Returns:
        pd.DataFrame
            DataFrame containing the tokenized text.

    Description:
        This function tokenizes text using spaCy and stores the tokens in a new column in the DataFrame. 
        It allows filtering tokens based on POS tags and stopwords. If 'stats' is set to True, it calculates 
        and stores token counts.
    """
    all_tokens=[]
    tokens_counts=[]
    tokens_kept=[]

    text=list(df[col_text].astype('unicode').values)

    for doc in tqdm(nlp.pipe(text, batch_size=batch_size, n_process=n_process), total= len(text), desc = "Tokenization"):
        if len(pos_to_keep)>0 and len(stopwords)>0:
            token_list = [str(tok.text).lower() for tok in doc if not (tok.is_punct or tok.is_space) and tok.text.lower() not in stopwords and tok.pos_ in pos_to_keep] 
        elif len(pos_to_keep)>0 and len(stopwords) < 1:
            token_list = [str(tok.text).lower() for tok in doc if not (tok.is_punct or tok.is_space) and tok.pos_ in pos_to_keep] 
        elif len(pos_to_keep) < 1 and len(stopwords) > 0:
            token_list = [str(tok.text).lower() for tok in doc if not (tok.is_punct or tok.is_space) and tok.text.lower() not in stopwords] 
        else :
            token_list = [str(tok.text).lower() for tok in doc if not (tok.is_punct or tok.is_space)] 
            
        all_tokens.append(token_list)

        if stats:
            tokens_counts.append(len(doc))
            tokens_kept.append(len(token_list))
        
    df[col_tokens]=all_tokens
    if stats:
        df["tokens_count"]=tokens_counts
        df["kept_tokens_count"]=tokens_kept
    
    return df


def lemmatize(nlp, df: pd.DataFrame, col_text: str, col_lemma: str, pos_to_keep: list, stopwords: list, batch_size: int = 100, n_process: int = 1, stats: bool = True, join_list: bool = False) -> pd.DataFrame:
    """ 
    Spacy implementation to lemmatize text
    
    Parameters:
        nlp : spacy.language.Language
            The spaCy language processing pipeline.
        df : pd.DataFrame
            DataFrame containing the text data.
        col_text : str
            The name of the column containing the text data.
        col_lemma : str
            The name of the column to store the lemmatized text.
        pos_to_keep : list
            List of POS tags to keep.
        stopwords : list
            List of stopwords to exclude from lemmas.
        batch_size : int, optional
            Batch size for processing. Default is 100.
        n_process : int, optional
            Number of processes for parallel processing. Default is 1.
        stats : bool, optional
            Flag indicating whether to calculate and store statistics. Default is True.
        join_list : bool, optional
            Flag indicating whether to join the lemmas into a single string. Default is False.
    
    Returns:
        pd.DataFrame
            DataFrame containing the lemmatized text.

    Description:
        This function lemmatizes text using spaCy and stores the lemmatized text in a new column in the DataFrame. 
        It allows filtering lemmas based on POS tags and stopwords. If 'stats' is set to True, it calculates 
        and stores token counts.
    """
    all_lemmas=[]
    tokens_counts=[]
    tokens_kept=[]

    text=list(df[col_text].astype('unicode').values)

    for doc in tqdm(nlp.pipe(text, batch_size=batch_size, n_process=n_process), total= len(text), desc = "Lemmatization"):

        if len(pos_to_keep)>0 and len(stopwords)>0:
            lemmas_list = [str(tok.lemma_).lower() for tok in doc if not (tok.is_punct or tok.is_space) and tok.text.lower() not in stopwords and tok.pos_ in pos_to_keep] 
        elif len(pos_to_keep)>0 and len(stopwords) < 1:
            lemmas_list = [str(tok.lemma_).lower() for tok in doc if not (tok.is_punct or tok.is_space) and tok.pos_ in pos_to_keep] 
        elif len(pos_to_keep) < 1 and len(stopwords) > 0:
            lemmas_list = [str(tok.lemma_).lower() for tok in doc if not (tok.is_punct or tok.is_space) and tok.text.lower() not in stopwords] 
        else :
            lemmas_list = [str(tok.lemma_).lower() for tok in doc if not (tok.is_punct or tok.is_space)] 
            
        all_lemmas.append(lemmas_list)

        if stats:
            tokens_counts.append(len(doc))
            tokens_kept.append(len(lemmas_list))
        
    if join_list:
        df[col_lemma]=[' '.join(map(str, l)) for l in all_lemmas]    
    else:
        df[col_lemma]=all_lemmas
    if stats:
        df["tokens_count"]=tokens_counts
        df["lemmas_count"]=tokens_kept
    
    return df


####################################################################
# VECTORISATION
####################################################################

def count_vectorize(lst_text: list) -> tuple:
    """
    Parameters:
        lst_text : list
            List of texts to be vectorized.

    Returns:
        count_vectorizer : sklearn.feature_extraction.text.CountVectorizer
            CountVectorizer object used for vectorization.
        features : scipy.sparse.csr.csr_matrix
            Sparse matrix of token counts.
        features_names : list
            List of feature names.
        vocabulary : dict
            Vocabulary dictionary mapping terms to feature indices.

    Description:
        This function vectorizes a list of texts using the CountVectorizer from scikit-learn. It tokenizes the texts based on 
        the provided token pattern, which defaults to considering any non-whitespace sequence as a token. The function returns 
        the CountVectorizer object itself, the sparse matrix of token counts, the list of feature names, and the vocabulary 
        dictionary mapping terms to feature indices.   
    """
    count_vectorizer = CountVectorizer(token_pattern=r'[^\s]+')
    features = count_vectorizer.fit_transform(lst_text)
    features_names = count_vectorizer.get_feature_names_out()
    vocabulary=count_vectorizer.vocabulary_
    
    return count_vectorizer, features, features_names, vocabulary 

def tfidf_vectorize(lst_text: list, analyzer: str = 'word', max_df: float = 1.0, max_features: int = None, 
                    min_df: float = 1, use_idf: bool = True, ngram_range: tuple = (1, 1), stop_words: list = None) -> tuple:
    """
    Parameters:
        lst_text : list
            List of texts to be vectorized.
        analyzer : str, {'word', 'char', 'char_wb'}, optional
            Whether to use word or character n-grams. Default is 'word'.
        max_df : float, optional
            Ignore terms that have a document frequency higher than the given threshold. Default is 1.0.
        max_features : int or None, optional
            Maximum number of features to be extracted. Default is None.
        min_df : float, optional
            Ignore terms that have a document frequency lower than the given threshold. Default is 1.
        use_idf : bool, optional
            Enable inverse-document-frequency reweighting. Default is True.
        ngram_range : tuple, optional
            The lower and upper boundary of the range of n-values for different n-grams to be extracted. Default is (1, 1).
        stop_words : str or list, optional
            Specifies the stopwords to be removed. Default is None.

    Returns:
        tfidf_vectorizer : sklearn.feature_extraction.text.TfidfVectorizer
            TfidfVectorizer object used for vectorization.
        features : scipy.sparse.csr.csr_matrix
            Sparse matrix of TF-IDF features.
        features_names : list
            List of feature names.
        vocabulary : dict
            Vocabulary dictionary mapping terms to feature indices.

    Description:
        This function vectorizes a list of texts using the TF-IDF (Term Frequency-Inverse Document Frequency) vectorizer 
        from scikit-learn. It applies various parameters to customize the vectorization process, such as input format, 
        encoding, analyzer, document frequency thresholds, n-gram range, stopwords, and token pattern for tokenization. 
        The function returns the TfidfVectorizer object itself, the sparse matrix of TF-IDF features, the list of feature 
        names, and the vocabulary dictionary mapping terms to feature indices.
    """
    tfidf_vectorizer = TfidfVectorizer(input="content", 
                                       analyzer=analyzer, 
                                       max_df=max_df,
                                       max_features=max_features, 
                                       min_df=min_df, 
                                       use_idf=use_idf, 
                                       ngram_range=ngram_range, 
                                       stop_words=stop_words,
                                      token_pattern=r'[^\s]+')
    
    features = tfidf_vectorizer.fit_transform(lst_text)
    features_names = tfidf_vectorizer.get_feature_names_out()
    vocabulary=tfidf_vectorizer.vocabulary_
    
    return tfidf_vectorizer, features, features_names, vocabulary

def SF_vectorize(lst_text: list, model_name: str) -> np.array:
    """
    Vectorize text using Sentence Transformers.
    
    Parameters:
        lst_text : list
            List of texts to be vectorized.
        model_name : str
            Name of the Sentence Transformers model to be used.

    Returns:
        features : numpy.ndarray
            Encoded features of the input texts.
    
    Description:
        This function vectorizes a list of texts using Sentence Transformers. It encodes the texts into fixed-size 
        vectors of features using the specified model. The function returns the encoded features as a numpy array.
    """
    model = SentenceTransformer(model_name)
    features = model.encode(lst_text)
    return features

def load_HF_embeddings(model_name : str, encode_kwargs : dict ={'batch_size':32}, model_kwargs : dict ={'device': 'cuda:0'}):
    """
    create a HugginFace encoder
    """
    try:
        HF_encoder = HuggingFaceEmbeddings(model_name=model_name, encode_kwargs = encode_kwargs, model_kwargs=model_kwargs)
        return HF_encoder
    except Exception as e:
        pass
        print(e)


def HF_vectorize(HF_encoder, lst_txt):
    """
    Vectorize using a Huggingface encoder
    """
    embeddings = HF_encoder.embed_documents(lst_txt)

    return embeddings

def encode_chunked_files(chunk_files_paths: list, 
                         HF_encoder, 
                         cols: list, 
                         col_text: str, 
                         path_embedded_chunks: str, 
                         reencode: bool = False) -> list:
    """
    Encode text from files and save the results in another pickle file.
    
    Parameters:
        chunk_files_paths (list): List of file paths containing documents.
        HF_encoder (Encoder): Encoder object for text vectorization.
        cols (list): Columns to keep in the resulting DataFrame.
        col_text (str): Column containing text data in the DataFrame.
        path_embedded_chunks (str): Path to save the embedded chunks.
        reencode (bool, optional): Whether to re-encode files even if they already exist. Defaults to False.
    
    Returns:
        List[str]: List of paths for newly created files.
    """
    new_file_paths=[]
    for file in tqdm(chunk_files_paths, total=len(chunk_files_paths), desc="Encoding text from files"):
        new_filename = os.path.splitext(os.path.basename(file))[0]+"_embedded"
        new_file_path = os.path.join(path_embedded_chunks, new_filename+".pickle")
        # on vérifie si on a déjà effectué l'encodage, si reencode == True, on effectue quand même la procédure
        if not os.path.exists(new_file_path) or reencode:
            current_df = load_pickle(file)

            text_list = current_df[col_text].to_list()

            # text vectorization
            embeddings = HF_encoder.embed_documents(text_list)

            # on crée un dataframe avec les embeddings
            current_df = current_df[cols]
            current_df['embeddings'] = embeddings

            # on sauvegarde
            new_file_path = write_pickle(current_df, path_embedded_chunks, new_filename)
            new_file_paths.append(new_file_path)
        else :
            new_file_paths.append(new_file_path)

    return new_file_paths

####################################################################
# ENCODING FEATURES
####################################################################

def encode_labels(data_to_encode: np.ndarray) -> tuple:
    """
    Encodes a list of labels using a LabelEncoder.

    Args:
        data_to_encode (List[Union[str, int]]): The list of labels to encode. Labels can be of any hashable type, but strings or integers are typical.

    Returns:
        Tuple[LabelEncoder, np.ndarray]: A tuple containing the fitted LabelEncoder instance and a numpy array of encoded labels.
    """
    label_encoder = LabelEncoder()
    label_encoder.fit(data_to_encode)
    encoded_labels = label_encoder.transform(data_to_encode)
    return label_encoder, encoded_labels


def encode_new_labels(label_encoder : LabelEncoder, data_to_encode : np.ndarray) -> np.ndarray:
    """
    Encodes a list of new labels using an already fitted LabelEncoder.

    Args:
    - label_encoder (LabelEncoder): A pre-fitted LabelEncoder instance.
    - data_to_encode (List[Union[str, int]]): The list of new labels to encode using the pre-fitted encoder.

    Returns:
    - np.ndarray: A numpy array of encoded labels.
    """
    encoded_labels = label_encoder.transform(data_to_encode)
    return encoded_labels

def one_hot_encode(data_to_encode:np.ndarray) -> tuple:
    """
    One-hot encodes a list of categorical values using OneHotEncoder.

    Args:
    - data_to_encode (List[Union[str, int]]): The list of categorical values to encode. The values can be of any hashable type, typically strings or integers.

    Returns:
    - Tuple[OneHotEncoder, np.ndarray]: A tuple containing the fitted OneHotEncoder instance and a numpy array of one-hot encoded values.
    """
    one_hot_encoder = OneHotEncoder(sparse=False)
    data_to_encode_reshaped = np.array(data_to_encode).reshape(-1, 1)  # Reshape for OneHotEncoder
    one_hot_encoder.fit(data_to_encode_reshaped)
    encoded_array = one_hot_encoder.transform(data_to_encode_reshaped)
    return one_hot_encoder, encoded_array


def one_hot_encode_new_data(one_hot_encoder: OneHotEncoder, data_to_encode: np.ndarray) -> np.ndarray:
    """
    One-hot encodes a list of new categorical values using an already fitted OneHotEncoder.

    Args:
    - one_hot_encoder (OneHotEncoder): A pre-fitted OneHotEncoder instance.
    - data_to_encode (List[Union[str, int]]): The list of new categorical values to encode using the pre-fitted encoder.

    Returns:
    - np.ndarray: A numpy array of one-hot encoded values.
    """
    data_to_encode_reshaped = np.array(data_to_encode).reshape(-1, 1)  # Reshape for OneHotEncoder
    encoded_array = one_hot_encoder.transform(data_to_encode_reshaped)
    return encoded_array

####################################################################
# SCALING FEATURES
####################################################################

def scaling_features(features: list, method: str = "standard") -> list:
    """
    Scale features using either standardization or min-max scaling.

    Parameters:
        features (Union[List[List[float]], List[float]]): List of features to scale.
        method (str, optional): Method of scaling, either "standard" for standardization or "min-max" for min-max scaling. Defaults to "standard".

    Returns:
        Union[List[List[float]], List[float]]: Scaled features.
    """
    try:
        if method=="standard":
            scaled_feat = StandardScaler(with_mean=False).fit_transform(features)

        else:
            scaled_feat = MinMaxScaler().fit_transform(features)
            
    except Exception as e:
        pass
        scaled_feat=features
        print(e, "features NOT SCALED")
            
    return scaled_feat
            
    

####################################################################
# REDUCTION DIMENSION
####################################################################

def lsa_reduction(features, n_components=50):
    """
    Reduce dimensions using TruncatedSVD
    """
    lsa = TruncatedSVD(n_components=n_components, random_state=0)
    embeddings = lsa.fit_transform(features)
    return embeddings

def reduce_with_UMAP(embeddings, n_neighbors = 5, n_components = 3, min_dist = 0.0, metric = "cosine"):
    """
    Reduce dimensions using UMAP
    - n_neighbors : number of neighbors
    - n_components : number of components
    - min_dist : minimum grouping distance 
    - metric : distance metric, usually "cosine" "hellinger" is another potential choice
    """
    #on réduit le nombe de dimensions
    reducer = umap.UMAP(n_neighbors=n_neighbors, 
                    n_components=n_components, 
                    min_dist=min_dist,
                    metric=metric).fit(embeddings)

    #on récupère les vecteurs réduits
    sample_reduced_embeddings = reducer.transform(embeddings)

    return reducer, sample_reduced_embeddings
    

def transform_with_UMAP(reducer, new_embeddings):
    """
    Transform new data points using a UMAP object
    """
    reduced_embeddings = reducer.transform(new_embeddings)
    return reduced_embeddings


def TSNE_reduction(features, n_components=2, perplexity=5, angle=0.5, n_iter=2000, distance_metric= 'cosine'):
    """
    Reduce dimensions using TSNE
    """
    embeddings = TSNE(n_components=n_components, 
                      perplexity=perplexity, 
                      angle=angle, 
                      n_iter=n_iter, 
                      metric=distance_metric, 
                      square_distances=True, 
                      init='random', 
                      learning_rate='auto',
                      random_state=42).fit_transform(features)
    return embeddings


def process_UMAP(embedded_chunks_paths, path_reduced_embeddings_id, reducer, reencode =  False):

    new_file_paths=[]
    for file_path in tqdm(embedded_chunks_paths, total=len(embedded_chunks_paths), desc="UMAP transform from files"):
        
        filename = os.path.splitext(os.path.basename(file_path))[0][:-9]
        new_filename = filename+"_reduce_embeddings.pickle"
        new_file_path = os.path.join(path_reduced_embeddings_id, new_filename)
    
        if not os.path.exists(new_file_path) or reencode:
            df = load_pickle(file_path)
            create_dir(path_reduced_embeddings_id)
            embeddings = df["embeddings"].to_list()
            reduced_embeddings = transform_with_UMAP(reducer, embeddings)
            reduced_embeddings_transformed=[list(e) for e in reduced_embeddings]
            df['reduced_embeddings'] = reduced_embeddings_transformed
            df.drop(columns=["embeddings"], inplace=True)
            print(path_reduced_embeddings_id, filename+"_reduce_embeddings")
            write_pickle(df, path_reduced_embeddings_id, filename+"_reduce_embeddings")
            new_file_paths.append(new_file_path)
        else:
            print("REDUCED EMBEDDINGS ALREADY EXISTS", file_path)
            new_file_paths.append(new_file_path)
    return new_file_paths

    
def process_HDBSCAN(clusterer, reduced_embeddings_paths, path_predictions_dataset_id, run_soft_clustering= False, reencode = False):
    new_file_paths=[]
    for file_path in tqdm(reduced_embeddings_paths, total=len(reduced_embeddings_paths), desc="HDBSCAN transform from files"):
        
        filename = os.path.splitext(os.path.basename(file_path))[0][:-18]
        new_filename = filename+ "_predictions.pickle"
        new_file_path = os.path.join(path_predictions_dataset_id, new_filename)
        if not os.path.exists(new_file_path) or reencode:
            df = load_pickle(file_path)
            reduced_embeddings = df["reduced_embeddings"].to_list()
            topics, probas = transform_with_HDBSCAN(clusterer, reduced_embeddings)
            df["topic"]=topics.astype(int).astype(str)
            df["proba"]=probas
            if run_soft_clustering:
                soft_clusters, soft_proba = soft_clustering_new_data(clusterer, np.array(reduced_embeddings))
                df["soft_topic"]=soft_clusters
                df["soft_proba"]=soft_proba

            write_pickle(df, path_predictions_dataset_id, filename+ "_predictions")
            new_file_paths.append(new_file_path)
        else:
            print("CLUSTERING ALREADY EXISTS", file_path)
            new_file_paths.append(new_file_path)
    return new_file_paths

    
    
####################################################################
# CLUSTERING
####################################################################

def agglomerative_clustering(embeddings, n_clusters=15, metric="euclidean", linkage="average", distance_threshold=None):
    """
    # on précise soit le nombre de clusters que l'on souhaite obtenir, soit le seuil de distance entre cluster.
    # un seul paramètre peut être défini, laisser l'autre à None
    n_clusters=15
    distance_threshold=None

    # métrique de distance : "euclidean", "l1", "l2", "manhattan", "cosine", or "precomputed"
    metric="euclidean"

    #méthode de calcul pour les branches
    # ward : minimizes the variance of the clusters being merged.
    # average : uses the average of the distances of each observation of the two sets.
    # complete or maximum : uses the maximum distances between all observations of the two sets.
    # single : uses the minimum of the distances between all observations of the two sets.
    linkage="average"

    """
    
    clusterer = AgglomerativeClustering(n_clusters=n_clusters, 
                                     metric=metric, 
                                     linkage=linkage, 
                                     distance_threshold=distance_threshold,
                                     compute_distances=True).fit(embeddings)
    return clusterer, clusterer.labels_
    
    
    
def hdbscan_clustering(embeddings, algorithm='best', alpha=1.0, cluster_selection_epsilon=0.0, approx_min_span_tree=True, gen_min_span_tree=True, leaf_size=40, metric='euclidean', min_cluster_size=5, min_samples=None, p=None, cluster_selection_method='eom', prediction_data = True):
    """
    This function performs clustering using the HDBSCAN (Hierarchical Density-Based Spatial Clustering of Applications with Noise) algorithm. It clusters the input data based on the specified parameters and returns the clusterer object, cluster labels for each point, and the probability of each sample being an outlier.
    
    Args
        embeddings : array-like or sparse matrix, shape (n_samples, n_features). The input data to be clustered.
        algorithm : {'best', 'generic', 'prims_kdtree', 'boruvka_kdtree', 'boruvka_balltree', 'prims_balltree'}, optional. The algorithm to use for computation. Default is best.
        alpha : float, optional. Scaling factor determining the individual weight of the (unnormalized) density estimate. Default is 1.0.
        cluster_selection_epsilon : float, optional. The epsilon value to specify a minimum cluster size. Default is 0.0.
        approx_min_span_tree : bool, optional. Whether to compute an approximation of the minimum spanning tree. Default is True.
        gen_min_span_tree : bool, optional. Whether to compute the minimum spanning tree. Default is True.
        leaf_size : int, optional. Leaf size for the underlying KD-tree or Ball Tree. Default is 40.
        metric : str or callable, optional. The metric to use for distance computation. Default is 'euclidean'.
        min_cluster_size : int, optional. The minimum size of clusters; single linkage splits that produce smaller clusters than this will be considered points "falling out" of a cluster rather than a cluster splitting into two new clusters. Default is 5.
        min_samples : int or None, optional. The number of samples in a neighborhood for a point to be considered a core point. If None, the value is set to min_cluster_size. Default is None.
        p : int, optional. The Minkowski p-norm distance metric parameter. Default is None.
        cluster_selection_method : {'eom', 'leaf', 'leaf_similar', 'eom_similar', 'tree', 'beagle'}, optional. The method used to select clusters from the condensed tree. Default is 'eom'.
        prediction_data : bool, optional. Whether the data is prediction data or not. Default is True.

    Returns:
        clusterer : hdbscan.hdbscan_.HDBSCAN. HDBSCAN clusterer object.
        labels : array, shape (n_samples,). Cluster labels for each point. Noisy samples are given the label -1.
        probabilities : array, shape (n_samples,). The probability of each sample being an outlier.
    """
    clusterer = hdbscan.HDBSCAN(algorithm=algorithm, 
                                alpha=alpha, 
                                cluster_selection_epsilon=cluster_selection_epsilon, 
                                approx_min_span_tree=approx_min_span_tree,
                                gen_min_span_tree=gen_min_span_tree,
                                leaf_size=leaf_size,
                                metric=metric,
                                min_cluster_size=min_cluster_size, 
                                min_samples=min_samples,
                                p=p,
                                cluster_selection_method=cluster_selection_method,
                                prediction_data = prediction_data)

    clusterer.fit(embeddings)
    
    return clusterer, clusterer.labels_, clusterer.probabilities_

def transform_with_HDBSCAN(clusterer, new_embeddings):
    """
    Transform new data points using a HDBSCAN object
    """
    new_data_topic, new_data_proba = hdbscan.approximate_predict(clusterer, new_embeddings)
    return new_data_topic, new_data_proba


def soft_clustering(clusterer):
    """
    HDBSCAN SOFT CLUSTERING
    """
    soft_clusters = hdbscan.all_points_membership_vectors(clusterer)
    soft_clusters_val = [str(np.argmax(x)) for x in soft_clusters] 
    soft_clusters_proba = [np.max(x) for x in soft_clusters] 
    return soft_clusters_val, soft_clusters_proba


def soft_clustering_new_data(clusterer, embeddings):
    """
    PREDICT NEW DATA POINTS HDBSCAN SOFT CLUSTERING
    """
    soft_clusters = hdbscan.prediction.membership_vector(clusterer, embeddings)
    soft_clusters_val = [str(np.argmax(x)) for x in soft_clusters] 
    soft_clusters_proba = [np.max(x) for x in soft_clusters] 
    return soft_clusters_val, soft_clusters_proba

def get_most_relevant_documents(cluster_id, condensed_tree):
          
    assert cluster_id > -1, "The topic's label should be greater than -1!"
        
    raw_tree = condensed_tree._raw_tree
    
    # Just the cluster elements of the tree, excluding singleton points
    cluster_tree = raw_tree[raw_tree['child_size'] > 1]
    
    # Get the leaf cluster nodes under the cluster we are considering
    leaves = hdbscan.plots._recurse_leaf_dfs(cluster_tree, cluster_id)
    
    # Now collect up the last remaining points of each leaf cluster (the heart of the leaf)
    result = np.array([])
    
    for leaf in leaves:
        max_lambda = raw_tree['lambda_val'][raw_tree['parent'] == leaf].max()
        points = raw_tree['child'][(raw_tree['parent'] == leaf) & (raw_tree['lambda_val'] == max_lambda)]
        result = np.hstack((result, points))
        
    return result.astype(int)

def get_exemplars(clusterer, df, col_topic, cols_to_keep, top_messages):
    """
    List the most relevant documents for each cluster
    """
    tree = clusterer.condensed_tree_
    clusters = tree._select_clusters()
    df_exemplars=pd.DataFrame()
    for idx in df[col_topic].unique():
        if int(idx) > -1:
            c_exemplars = get_most_relevant_documents(clusters[int(idx)], tree)
            df_exemplars_tmp = df.iloc[c_exemplars[:top_messages]]
            df_exemplars = pd.concat([df_exemplars, df_exemplars_tmp])
            df_exemplars = df_exemplars[cols_to_keep].reset_index(drop=True)
    return df_exemplars

def df_transform_column_as_list(column):
    """Transform a column with unknown data format to a list of values"""
    if isinstance(column.iloc[0], str):
        # Check if it's a list formatted as string, and convert to list
        try:
            values = ast.literal_eval(column.iloc[0])
        except ValueError:
            # If it's a single URL as string, make it a list
            values = [column.iloc[0]]
    elif isinstance(column.iloc[0], int):
        # Check if it's a list formatted as int, and convert to list
        values = [column.iloc[0]]
    elif isinstance(column.iloc[0], float):
        # Check if it's a list formatted as float, and convert to list
        values = [column.iloc[0]]
    elif isinstance(column.iloc[0], bool):
        # Check if it's a list formatted as bool, and convert to list
        values = [column.iloc[0]]
    elif isinstance(column.iloc[0], list):
        # If it's already a list, use it as is
        values = column.iloc[0]
    else:
        raise ValueError("Unsupported format")

    return values

def check_gpu():
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    return device
  
def HF_load_model(model_checkpoint):
    tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)
    model = AutoModelForSequenceClassification.from_pretrained(model_checkpoint)
    config = AutoConfig.from_pretrained(model_checkpoint)
    if torch.cuda.is_available():
        model.cuda()
    return model, tokenizer, config

def HF_sentiment_classifier(tokenizer, model, text, col_text, filename, dir_json):
    """ Calculate sentiment of a text. `return_type` can be 'label', 'score' or 'proba' """
    file_path= os.path.join(dir_json , str(filename)+'.json')
    results = {}
    if not os.path.exists(file_path):
        with torch.no_grad():
            inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True).to(model.device)
            proba = torch.sigmoid(model(**inputs).logits).cpu().numpy()[0]
            label = model.config.id2label[proba.argmax()]
            results = {"label":label, "score" : float(proba.max()), col_text : text}
            write_json(results, dir_json , str(filename))
            
    return results


def add_tag_libretranslate_not_translate(text):
    """
    This function add fake html tag around words such as mentions, hashtags, urls and emojis to avoid translation of those tokens.

    Args:
    text (str): The text to process

    Returns:
    str: The text with the fake html tags
    """
    # This regex finds words starting with # and followed by alphanumeric characters or underscores
    mention_pattern = r"(?:RT\s|QT\s)?(?<=^|(?<=[^a-zA-Z0-9-_\.]))(@[A-Za-z0-9_]{4,15})"
    hashtag_pattern = r"(\B#\w+)"
    url_pattern = r"(https?://[^ ]+)"
    emoji_pattern = r':[a-zA-Z_]+:'

    pattern = re.compile(emoji_pattern+ "|" + mention_pattern + "|" + hashtag_pattern + "|" + url_pattern)
    
    # This function replaces the hashtag with an HTML link tag
    def replace_with_link(match):
        matcher_group = match.group(0)
        return f'<a href="{matcher_group}"></a>'
    
    # Use re.sub to substitute the hashtags with the HTML link tags
    text_no_emojis = emoji.demojize(text)
    result = re.sub(pattern, replace_with_link, text_no_emojis)
    
    return result

def clean_libre_translate_tags(text):
    """
    This function remove fake tags added by add_tag_libretranslate_not_translate() function.
    
    Args:
    text (str): The text to process

    Returns:
    str: The text with the fake html tags
    """
    cleaned_string = text.replace('<a href="', '').replace('"></a>', '')
    return cleaned_string