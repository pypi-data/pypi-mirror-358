import os
import pandas as pd
import pickle
import glob
import requests
import json
from tqdm import tqdm
import shutil
import zipfile
import random
from collections import Counter
import gspread
from google.auth import exceptions
import pyarrow.parquet as pq
from datetime import datetime
import hashlib
import ast
import subprocess
import chardet

####################################################################################################
# FILE LOADERS
####################################################################################################

def load_file(path: str, delimiter: str = ";", decimal: str = ".")  -> pd.DataFrame:
    """
    Load a file into a Pandas DataFrame based on the file extension.

    Args:
        path (str): The file path to load.
        delimiter (str, optional): The delimiter used in CSV/TSV files. Default is ";".
        decimal (str, optional): The character used for decimal points in CSV/TSV files. Default is ".".

    Returns:
        pandas.DataFrame: The loaded data as a Pandas DataFrame.

    Raises:
        ValueError: If the file extension is not supported.
    """
    extension = os.path.splitext(os.path.basename(path))[1]
    if extension == ".parquet":
        df = load_parquet(path)
    elif extension == ".pickle":
        df = load_pickle(path)
    elif extension == ".json":
        df = load_json(path)
    elif extension == ".jsonl":
        df = load_jsonl(path)
    elif extension == ".csv":
        df = load_csv(path, delimiter = delimiter, decimal =decimal)
    elif extension == ".tsv":
        df = load_csv(path, delimiter = "\t", decimal =decimal)
    else :
        print("Check your input file. Extension isn't supported : .parquet, .pickle, .json, .jsonl, .csv, .tsv")
    return df

def load_parquet(path: str) -> pd.DataFrame:
    """
    Load a parquet file into a DataFrame.
    
    Args:
        path (str): The file path to the parquet file.
    
    Returns:
        pandas.DataFrame: The loaded data as a Pandas DataFrame.
    
    Raises:
        Exception: If there is an error reading the parquet file.
    """
    try:
        table = pq.read_table(path)
        df = table.to_pandas()
    except Exception as e:
        pass
        print(e)
    return df

def load_excel(path : str, sheet_name : str = ""):
    """
    Loads an Excel sheet into a Pandas DataFrame.

    Args:
        file_path (str): Path to the Excel file.
        sheet_name (str, int, list, or None): Name of sheet or sheet number to load.
            0 (default) - Load first sheet.
            str - Load sheet with specified name.
            list - Load multiple sheets, returns a dictionary of DataFrames.
            None - Load all sheets, returns a dictionary of DataFrames.

    Returns:
        DataFrame or dict of DataFrames.
    """
    try:
        df = pd.read_excel(path, sheet_name=sheet_name)
        return df
    except Exception as e:
        print(f"Error loading Excel file: {e}")
        return None
    
def load_pickle(path: str) -> pd.DataFrame:
    """
    Load a pickle file into a DataFrame.
    
    Args:
        path (str): The file path to the pickle file.
    
    Returns:
        pandas.DataFrame: The loaded data as a Pandas DataFrame.
    """
    return pd.read_pickle(path)


def load_json(path: str) -> pd.DataFrame:
    """
    Load a JSON file into a DataFrame.
    
    Args:
        path (str): The file path to the JSON file.
    
    Returns:
        pd.DataFrame: The loaded data as a Pandas DataFrame.
    
    Raises:
        Exception: If there is an error reading the JSON file.
    """
    df = pd.DataFrame()
    try:
        with open(path, 'r') as json_file:
            data = json.load(json_file)
        df = pd.json_normalize(data)
    except Exception as e:
        print(f"Error reading the JSON file: {e}")
        raise
    return df

def load_jsonl(path: str) -> pd.DataFrame:
    """
    Load a JSON Lines (jsonl) file into a DataFrame.
    
    Args:
        path (str): The file path to the jsonl file.
    
    Returns:
        pd.DataFrame: The loaded data as a Pandas DataFrame.
    
    Raises:
        Exception: If there is an error reading the jsonl file.
    """
    df = pd.DataFrame()
    try:
        data = []
        with open(path, 'r') as json_file:
            for line in tqdm(json_file, desc="Loading JSON Lines"):
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError as line_error:
                    print(f"Error decoding line: {line_error}")
            
        df = pd.json_normalize(data)
    except Exception as e:
        print(f"Error reading the jsonl file: {e}")
        raise
    return df


def load_csv(path: str, delimiter: str = ";", decimal: str = ".") -> pd.DataFrame:
    """
    Load a CSV file into a DataFrame.
    
    Args:
        path (str): The file path to the CSV file.
        delimiter (str, optional): The delimiter used in the CSV file. Default is ";".
        decimal (str, optional): The character used for decimal points in the CSV file. Default is ".".
    
    Returns:
        pd.DataFrame: The loaded data as a Pandas DataFrame.
    
    Raises:
        Exception: If there is an error reading the CSV file.
    """
    df = pd.DataFrame()
    try:
        df = pd.read_csv(path, delimiter=delimiter, encoding="utf-8", decimal=decimal)
    except Exception as e:
        print(f"Error reading the CSV file: {e}")
        raise
    return df

def read_txt_to_list(file_path: str) -> list[str]:
    """
    Read a text file line by line and append to a Python list.
    
    Args:
        file_path (str): The file path to the text file.
    
    Returns:
        list[str]: A list of lines read from the text file.
    
    Raises:
        FileNotFoundError: If the file does not exist.
        Exception: If any other error occurs during file reading.
    """
    
    # Initialize an empty list to store the lines
    lines = []

    try:
        # Open the file in read mode
        with open(file_path, 'r') as file:
            # Read each line and append it to the list
            lines = [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")
        raise
    return lines

def read_json(path: str) -> dict:
    """
    Read a JSON file and return a dictionary.
    
    Args:
        path (str): The file path to the JSON file.
    
    Returns:
        dict: The data read from the JSON file as a dictionary.
    
    Raises:
        FileNotFoundError: If the file does not exist.
        Exception: If there is an error reading the JSON file.
    """
    with open(path, 'r') as json_file:
        data = json.load(json_file)
    return data

def read_txt_file(file_path: str) -> str:
    """
    Read the content of a text file and return it as a string.
    
    Args:
        file_path (str): The file path to the text file.
    
    Returns:
        str: The content of the text file as a string.
    
    Raises:
        FileNotFoundError: If the file does not exist.
        Exception: If there is an error reading the text file.
    """
    try:
        with open(file_path, 'r') as file:
            content = file.read()
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        raise
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        raise
    return content

def read_jsonl(path: str) -> list[dict]:
    """
    Load a JSON Lines (jsonl) file into a list of dictionaries.
    
    Args:
        path (str): The file path to the jsonl file.
    
    Returns:
        list[dict]: A list of dictionaries containing the data read from the JSON Lines file.
    
    Raises:
        FileNotFoundError: If the file does not exist.
        Exception: If there is an error reading the jsonl file.
    """
    json_data = []
    try:
        with open(path, 'r') as json_file:
            for line in tqdm(json_file, desc="Reading JSON Lines"):
                try:
                    json_data.append(json.loads(line))
                except Exception as e:
                    print(f"Error decoding line: {e}")
                    raise
    except FileNotFoundError:
        print(f"File not found: {path}")
        raise
    return json_data


#########################################################################################
# FILE WRITERS
#########################################################################################


def write_pickle(data: pd.DataFrame, path: str, filename: str) -> str:
    """
    Write a DataFrame into a pickle file.
    
    Args:
        data (pd.DataFrame): The DataFrame to be written to the pickle file.
        path (str): The directory where the pickle file will be saved.
        filename (str): The name of the pickle file (without the extension).
    
    Returns:
        str: The full path to the saved pickle file.
    """
    file_path = os.path.join(path, filename + '.pickle')
    with open(file_path, 'wb') as f:
        pickle.dump(data, f)
    return file_path

def save_df_to_pickle(df: pd.DataFrame, path: str, filename: str) -> str:
    """
    Write a DataFrame into a pickle file.
    
    Args:
        data (pd.DataFrame): The DataFrame to be written to the pickle file.
        path (str): The directory where the pickle file will be saved.
        filename (str): The name of the pickle file (without the extension).
    
    Returns:
        str: The full path to the saved pickle file.
    """
    file_path = os.path.join(path, filename + '.pickle')
    df.to_pickle(file_path)
    return file_path


def write_list_to_txt(input_list: list, path: str, name: str) -> str:
    """
    Write a list to a text file, with each item on a new line.

    Args:
        input_list (list): The list to be written to the text file.
        path (str): The directory path where the text file will be saved.
        name (str): The name of the text file (without the extension).

    Returns:
        str: The full path to the saved text file.
    """
    file_path = os.path.join(path, name + '.txt')
    with open(file_path, 'w') as file:
        for item in input_list:
            file.write(str(item) + '\n')
    return file_path

def write_jsonl(data: list[dict], path: str, name: str) -> str:
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
            json.dump(entry, file)
            file.write('\n')
    return file_path


def write_json(json_dict: dict, path: str, name: str) -> str:
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
        json.dump(json_dict, outfile)
    return file_path




def write_dataframe_to_json(df: pd.DataFrame, path: str, name: str, orient: str = 'records') -> str:
    """
    Write a DataFrame to a JSON file.

    Args:
        df (pd.DataFrame): The DataFrame to be written to the JSON file.
        path (str): The directory path where the JSON file will be saved.
        name (str): The name of the JSON file (without the extension).
        orient (str, optional): The format of the JSON file. Default is 'records'.

    Returns:
        str: The full path to the saved JSON file.
    """
    file_path = os.path.join(path, name + ".json")
    df.to_json(file_path, orient=orient, lines=True)
    return file_path
    
    
def save_dataframe_excel(df: pd.DataFrame, path: str, name: str, sheet_name: str) -> str:
    """
    Write a DataFrame to an Excel file.

    Args:
        df (pd.DataFrame): The DataFrame to be written to the Excel file.
        path (str): The directory path where the Excel file will be saved.
        name (str): The name of the Excel file (without the extension).
        sheet_name (str): The name of the Excel sheet.

    Returns:
        str: The full path to the saved Excel file.
    """
    file_path = os.path.join(path, f"{name}.xlsx")
    df.to_excel(file_path, sheet_name=sheet_name, index=False)
    print(file_path, "- File created")
    return file_path

def add_dataframe_to_excel(df: pd.DataFrame, existing_file_path: str, new_sheet_name: str) -> None:
    """
    Adds a DataFrame to an existing Excel file as a new sheet.

    Args:
        df (pd.DataFrame): The DataFrame to be added.
        existing_file_path (str): Path to the existing Excel file.
        new_sheet_name (str): Name of the new sheet in the Excel file.

    Returns:
        None
    """
    # Read existing Excel file into a dictionary of DataFrames
    excel_file = pd.read_excel(existing_file_path, sheet_name=None)

    # Add the new DataFrame to the dictionary with the specified sheet name
    excel_file[new_sheet_name] = df

    # Write the updated dictionary of DataFrames back to the Excel file
    with pd.ExcelWriter(existing_file_path, engine='xlsxwriter') as writer:
        for sheet_name, df in excel_file.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)

def save_dataframe_csv(df: pd.DataFrame, path: str, name: str) -> str:
    """
    Save a DataFrame to a CSV file within a specified directory.

    Args:
        df (pd.DataFrame): The DataFrame to be saved.
        path (str): The directory where the CSV file will be saved.
        name (str): The desired name for the CSV file (without extension).

    Returns:
        str: The full path to the saved CSV file.
    """
    file_path = os.path.join(path, f"{name}.csv")
    df.to_csv(
        file_path,
        sep=";",
        encoding="utf-8",
        index=False,
        decimal=",",
    )
    print("File saved:", file_path)
    return file_path

def write_txt_file(data: str, path: str, name: str) -> str:
    """
    Write a string to a text file.

    Args:
        data (str): The string to be written to the text file.
        path (str): The directory path where the text file will be saved.
        name (str): The name of the text file (without the extension).

    Returns:
        str: The full path to the saved text file.
    """
    file_path = os.path.join(path, name + '.txt')
    with open(file_path, "w") as file:
        file.write(data)
    return file_path

def split_df_into_chunks(df: pd.DataFrame, path: str, name: str, chunk_size: int = 10000) -> list:
    """
    Split a DataFrame into multiple pickle files with a specified chunk size.

    Args:
        df (pd.DataFrame): The DataFrame to be split.
        path (str): The directory path where the pickle files will be saved.
        name (str): The base name for the pickle files.
        chunk_size (int, optional): The size of each chunk. Default is 10000.

    Returns:
        list[str]: A list of file paths to the saved pickle files.
    """
    num_chunks = -(-len(df) // chunk_size)  # Calculate the number of chunks using ceil division

    file_paths = []

    # create smaller datasets of chunk_size each
    for i in range(num_chunks):
        start = i * chunk_size
        end = (i + 1) * chunk_size
        chunk = df.iloc[start:end]
        filename = f"{name}_{i}"  # Adjust the filename format as needed
        file_path = write_pickle(chunk, path, filename)
        file_paths.append(file_path)

    return file_paths

###################################################################################################
# FOLDERS / FILES HELPERS
###################################################################################################

def create_dir(path: str) -> str:
    """
    Create a local directory if it doesn't exist.

    Args:
        path (str): The directory path to be created.

    Returns:
        str: The path of the created directory.
    """
    if not os.path.exists(path):
        os.makedirs(path)
        print(path, "- directory created")
    return path


def list_files_in_dir(path: str, filetype: str = '*.json') -> list:
    """
    List files of a specific format in a directory.

    Args:
        path (str): The directory path to search for files.
        filetype (str, optional): The file type pattern to search for. 

    Returns:
        list: A list of file paths matching the specified file type pattern.
    """
    pattern = os.path.join(path, filetype)
    files = glob.glob(pattern)
    return files


def list_subdirectories(root_directory: str) -> list:
    """
    List subdirectories in a root directory.

    Args:
        root_directory (str): The root directory path.

    Returns:
        list[str]: A list of subdirectory names.
    """
    subdirectories = []
    for entry in os.scandir(root_directory):
        if entry.is_dir():
            subdirectories.append(entry.name)
    return subdirectories


def list_recursive_subdirectories(root_directory: str) -> list:
    """
    List recursively all subdirectories from a root directory.

    Args:
        root_directory (str): The root directory path.

    Returns:
        list[str]: A list of subdirectory paths.
    """
    subdirectories = []
    for root, dirs, files in os.walk(root_directory):
        subdirectories.extend([os.path.join(root, d) for d in dirs])
    return subdirectories


def list_files_in_subdirectories(path: str, filetype: str = '*.json') -> list:
    """
    Walk through subdirectories of a root directory to list files of a specific format.

    Args:
        path (str): The root directory path.
        filetype (str, optional): The file type pattern to search for.

    Returns:
        list[str]: A list of file paths matching the specified file type pattern in subdirectories.
    """
    files = []

    # Check if the directory exists
    if not os.path.exists(path):
        print(f"The directory '{path}' does not exist.")
        return files

    # Use glob to get all files in the directory and its subdirectories
    pattern = os.path.join(path, '**', filetype)
    files = glob.glob(pattern, recursive=True)

    return files

def copy_file(source_path: str, destination_path: str, new_filename: str = None) -> str:
    """
    Copy a file from a source path to a destination path.

    Args:
        source_path (str): The path of the source file.
        destination_path (str): The path of the destination directory.
        new_filename (str, optional): The new filename. If not provided, the original filename is used.

    Returns:
        str: The path of the copied file.
    """
    if new_filename:
        file_path = os.path.join(destination_path, new_filename)
    else:
        filename = os.path.basename(source_path)
        file_path = os.path.join(destination_path, filename)
    
    shutil.copy(source_path, file_path)
    return file_path

def remove_file(file_path: str) -> None:
    """
    Remove a single file.

    Args:
        file_path (str): The path of the file to be removed.

    Returns:
        None
    """
    try:
        os.remove(file_path)
        print(f"File {file_path} removed successfully.")
    except OSError as e:
        print(f"Error removing file {file_path}: {e}")
        
def remove_folder(folder_path: str) -> None:
    """
    Remove a folder and all its contents.

    Args:
        folder_path (str): The path of the folder to be removed.

    Returns:
        None
    """
    try:
        shutil.rmtree(folder_path)
        print(f"Folder {folder_path} and its contents removed successfully.")
    except OSError as e:
        print(f"Error removing folder {folder_path}: {e}")
           
        
def get_file_size(file_path: str) -> tuple[int, str]:
    """
    Get the size of a single file in a readable format (KB, MB, GB).

    Args:
        file_path (str): The path of the file.

    Returns:
        tuple[int, str]: A tuple containing the size of the file in bytes and its formatted size. If the file is not found, returns None.
    """
    try:
        size = os.path.getsize(file_path)

        # Define the units and their respective sizes
        units = ['B', 'KB', 'MB', 'GB']
        size_in_units = size
        unit_index = 0

        # Convert size to appropriate unit
        while size_in_units > 1024 and unit_index < len(units) - 1:
            size_in_units /= 1024
            unit_index += 1

        # Format the result
        formatted_size = "{:.2f} {}".format(size_in_units, units[unit_index])
        print(formatted_size)
        return size, formatted_size
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None

def get_folder_size(folder_path: str) -> tuple[int, str]:
    """
    Get the size of all files contained in a folder in a readable format (KB, MB, GB).

    Args:
        folder_path (str): The path of the folder.

    Returns:
        tuple[int, str]: A tuple containing the total size of all files in bytes and its formatted size.
        If the folder is not found, returns None.
    """
    total_size = 0

    try:
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                total_size += os.path.getsize(filepath)

        # Define the units and their respective sizes
        units = ['B', 'KB', 'MB', 'GB']
        size_in_units = total_size
        unit_index = 0

        # Convert size to appropriate unit
        while size_in_units > 1024 and unit_index < len(units) - 1:
            size_in_units /= 1024
            unit_index += 1

        # Format the result
        formatted_size = "{:.2f} {}".format(size_in_units, units[unit_index])

        return total_size, formatted_size
    except FileNotFoundError:
        print(f"Folder not found: {folder_path}")
        return None

def file_creation_date(file_path: str) -> datetime:
    """
    Return the last update timestamp of a file.

    Args:
        file_path (str): The path of the file.

    Returns:
        datetime: The last update timestamp as a datetime object.
        If the file does not exist, returns None.
    """
    # Check if the file exists
    if os.path.exists(file_path):
        # Get the last modified timestamp
        last_update_timestamp = os.path.getmtime(file_path)
        # Convert the timestamp to a datetime object
        last_update_date = datetime.fromtimestamp(last_update_timestamp)
        return last_update_date
    else:
        return None
    
############################################################################
# LISTS HELPERS
############################################################################
    
    
def transform_to_n_items_list(lst: list, n: int) -> list[list]:
    """
    Transform a list into a list of n-items sublists.

    Args:
        lst (list): The input list to be transformed.
        n (int): The number of items in each sublist.

    Returns:
        list[list]: A list of n-items sublists.
    """
    return [lst[i:i + n] for i in range(0, len(lst), n)]


def unduplicate_list(lst: list) -> list:
    """ 
    Remove duplicate elements from a list.

    Args:
        lst (list): The input list with possible duplicate elements.

    Returns:
        list: A list with duplicate elements removed.
    """
    return list(set(lst))


def sort_list(lst: list, reverse: bool = False) -> list:
    """
    Sort the list in ascending or descending order.

    Args:
        lst (list): The input list.
        reverse (bool): If True, sort the list in descending order. 
                     If False (default), sort the list in ascending order.

    Returns:
        list: A new list sorted based on the specified order.
    """
    return sorted(lst, reverse=reverse)


def map_list(lst: list, function: callable) -> list:
    """
    Apply a function to each element of the list.

    Args:
        lst (list): The input list.
        function (callable): The function to apply to each element.

    Returns:
        list: A new list with the function applied to each element.
    """
    return [function(element) for element in lst]


def flatten_list(lst: list) -> list:
    """
    Flatten a nested list into a single list.

    Args:
        lst (list): The input nested list.

    Returns:
        list: A new list with all nested elements flattened.
    """
    flattened_list = []

    def flatten_recursive(sublist):
        for element in sublist:
            if isinstance(element, list):
                flatten_recursive(element)
            else:
                flattened_list.append(element)

    flatten_recursive(lst)
    return flattened_list


def find_occurrences(lst: list, element) -> int:
    """
    Find the occurrences of a specific element in the list.

    Args:
        lst (list): The input list.
        element: The element to find occurrences of.

    Returns:
        int: The number of occurrences of the specified element in the list.
    """
    return lst.count(element)


def is_subset(subset: list, superset: list) -> bool:
    """
    Check if one list is a subset of another.

    Args:
        subset (list): The potential subset list.
        superset (list): The superset list.

    Returns:
        bool: True if the subset is a subset of the superset, False otherwise.
    """
    return all(element in superset for element in subset)

def common_elements(list1: list, list2: list) -> list:
    """
    Find the common elements between two lists.

    Args:
        list1 (list): The first list.
        list2 (list): The second list.

    Returns:
        list: A new list containing the common elements between list1 and list2.
    """
    return list(set(list1) & set(list2))


def shuffle_list(lst: list) -> list:
    """
    Shuffle the elements of the list randomly.

    Args:
        lst (list): The input list.

    Returns:
        list: A new list with the elements shuffled randomly.
    """
    shuffled_list = lst.copy()
    random.shuffle(shuffled_list)
    return shuffled_list


def sample_list(lst: list, sample_size) -> list:
    """
    Sample a list based on an integer or a float representing the sample size.

    Args:
        lst (list): The input list.
        sample_size (int or float): If an integer, the number of elements to keep.
                                 If a float, the percentage of elements to keep.

    Returns:
        list: A new list containing the sampled elements.

    Raises:
        ValueError: If the sample size is invalid (negative integer or float outside [0, 1]).
        TypeError: If the sample size is neither an integer nor a float.
    """
    if isinstance(sample_size, int):
        if sample_size < 0:
            raise ValueError("Sample size must be a non-negative integer.")
        return random.sample(lst, min(sample_size, len(lst)))
    elif isinstance(sample_size, float):
        if not 0 <= sample_size <= 1:
            raise ValueError("Sample size must be a float between 0 and 1.")
        sample_size = int(sample_size * len(lst))
        return random.sample(lst, sample_size)
    else:
        raise TypeError("Sample size must be an integer or a float.")

def count_elements(lst: list) -> dict:
    """
    Count the occurrences of each element in the list.

    Args:
        lst (list): The input list.

    Returns:
        dict: A dictionary where keys are unique elements from the list, and values are their counts.
    """
    return dict(Counter(lst))

def scale_list(lst: list, min_val: float = 1, max_val: float = 5) -> list:
    """
    Scale the values of a list to a specified range.

    Args:
        lst (list): The input list of values to be scaled.
        min_val (float): The minimum value of the output range (default is 1).
        max_val (float): The maximum value of the output range (default is 5).

    Returns:
        list: A new list with values scaled to the specified range.
    """
    min_w = min(lst)
    max_w = max(lst)
    scaled_w = []
    for x in lst:
        try:
            scaled_value = (x - min_w) / (max_w - min_w) * (max_val - min_val) + min_val
        except ZeroDivisionError:
            scaled_value = min_val
        scaled_w.append(scaled_value)
    return scaled_w


def df_scale_column(df: pd.DataFrame, col_to_scale: str, col_out: str, min_val: float, max_val: float) -> pd.DataFrame:
    """
    Scale values in a DataFrame column to a specified range.

    Args:
        df (pd.DataFrame): The input DataFrame.
        col_to_scale (str): The name of the column to be scaled.
        col_out (str): The name of the new column to store scaled values.
        min_val (float): The minimum value of the output range.
        max_val (float): The maximum value of the output range.

    Returns:
        pd.DataFrame: The DataFrame with a new column containing scaled values.
    """
    min_freq = df[col_to_scale].min()
    max_freq = df[col_to_scale].max()
    df[col_out] = df[col_to_scale].apply(lambda x: ((x - min_freq) / (max_freq - min_freq)) * (max_val - min_val) + min_val)
    return df

############################################################################
# ZIP HELPERS
############################################################################      
    
def zip_file(source_file_path: str, zip_file_path: str, name: str) -> str:
    """
    Zip a single file.

    Args:
        source_file_path (str): Path to the file to be zipped.
        zip_file_path (str): Path for the resulting zip file.
        name (str): Name for the resulting zip file (without extension).

    Returns:
        str: Path to the resulting zip file.
    """
    file_path = os.path.join(zip_file_path, f"{name}.zip")
 
    with zipfile.ZipFile(file_path, 'w') as zip_file:
        # The second argument to `arcname` is used to set the name of the file inside the zip
        zip_file.write(source_file_path, arcname=os.path.basename(source_file_path))

    return file_path
    
def zip_folder(source_folder_path: str, zip_file_path: str, name: str) -> str:
    """
    Zip an entire folder.

    Args:
        source_folder_path (str): Path to the folder to be zipped.
        zip_file_path (str): Path for the resulting zip file.
        name (str): Name for the resulting zip file (without extension).

    Returns:
        str: Path to the resulting zip file.
    """
    file_path = os.path.join(zip_file_path, f"{name}.zip")
    
    with zipfile.ZipFile(file_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for foldername, subfolders, filenames in os.walk(source_folder_path):
            for filename in filenames:
                fpath = os.path.join(foldername, filename)
                arcname = os.path.relpath(fpath, source_folder_path)
                zip_file.write(fpath, arcname=arcname)
                
    return file_path

def unzip_file(zip_file_path: str, destination_path: str) -> None:
    """
    Unzip a zip file.

    Args:
        zip_file_path (str): Path to the zip file to be unzipped.
        destination_path (str): Path where the contents of the zip file will be extracted.

    Returns:
        None
    """
    with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
        zip_ref.extractall(destination_path)
    

############################################################################
# Google Spreadsheets HELPERS
############################################################################   


def create_google_spreadsheet_client(credentials: str):
    """
    Create a Gspread client to interact with Google Sheets.

    Args:
        credentials (str): Path to the JSON file containing Google Service Account credentials.

    Returns:
        gspread.Client: A client object for interacting with Google Sheets.
    """
    return gspread.service_account(filename=credentials)

def read_google_spreadsheet(client: gspread.Client, sheet_id: str, worksheet_name: str) -> pd.DataFrame:
    """
    Read data from a Google spreadsheet and return it as a DataFrame.

    Args:
        client (gspread.Client): A Gspread client object authenticated with Google Sheets API.
        sheet_id (str): The ID of the Google spreadsheet.
        worksheet_name (str): The name of the worksheet within the spreadsheet.

    Returns:
        pd.DataFrame: A DataFrame containing the data from the specified worksheet.
    """
    try:
        # Open the Google Spreadsheet by ID
        sheet = client.open_by_key(sheet_id)
        
        # Select a specific worksheet by name
        worksheet = sheet.worksheet(worksheet_name)
        
        # Get all values from the worksheet
        df = pd.DataFrame(worksheet.get_all_records())
        
        return df
    except exceptions.GoogleAuthError as e:
        print(f"Authentication error: {e}")
    except gspread.exceptions.APIError as e:
        print(f"API error: {e}")
    except gspread.exceptions.WorksheetNotFound as e:
        print(f"Worksheet not found: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


def list_google_worksheets(client: gspread.Client, sheet_id: str) -> list:
    """
    Return a list of worksheet names for a spreadsheet ID.

    Args:
        client (gspread.Client): A Gspread client object authenticated with Google Sheets API.
        sheet_id (str): The ID of the Google spreadsheet.

    Returns:
        list: A list of worksheet names.
    """
    sheet = client.open_by_key(sheet_id)
    worksheet_obj = sheet.worksheets()
    worksheet_list = [sheet.title for sheet in worksheet_obj]
    return worksheet_list
    
def get_spreadsheet_permissions(client: gspread.Client, sheet_id: str) -> pd.DataFrame:
    """
    Return a DataFrame with the list of user email and type that can access the document.

    Args:
        client (gspread.Client): A Gspread client object authenticated with Google Sheets API.
        sheet_id (str): The ID of the Google spreadsheet.

    Returns:
        pd.DataFrame: A DataFrame containing the list of user email addresses and their access types.
    """
    sheet = client.open_by_key(sheet_id)
    permissions = sheet.list_permissions()
    user_list = [(user.get("emailAddress"), user.get("type")) for user in permissions if user.get("emailAddress") is not None]
    df = pd.DataFrame(user_list, columns=['email', 'type'])
    return df


def create_google_spreadsheet(client: gspread.Client, df: pd.DataFrame, filename: str, worksheet_name: str = "Sheet1") -> gspread.Spreadsheet:
    """
    Create a new Google spreadsheet and load a DataFrame into it.

    Args:
        client (gspread.Client): A Gspread client object authenticated with Google Sheets API.
        df (pd.DataFrame): The DataFrame to be loaded into the spreadsheet.
        filename (str): The desired filename for the new spreadsheet.
        worksheet_name (str, optional): The name of the worksheet within the spreadsheet. Defaults to "Sheet1".

    Returns:
        gspread.Spreadsheet: The created spreadsheet object.
    """
    spreadsheet = client.create(filename)
    worksheet = spreadsheet.sheet1
    if worksheet_name != "Sheet1":
        worksheet.update_title(worksheet_name)
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())

    return spreadsheet

def share_google_spreadsheet(spreadsheet: gspread.Spreadsheet, email: str, user_type: str = "user", user_role: str = "writer", notify: bool = False, email_message: str = None, with_link: bool = False) -> gspread.Spreadsheet:
    """
    Share a spreadsheet with a user.

    Args:
        spreadsheet (gspread.Spreadsheet): The Google spreadsheet object to be shared.
        email (str): The email address of the user with whom the spreadsheet will be shared.
        user_type (str, optional): The permission type for the user. Defaults to "user".
        user_role (str, optional): The role assigned to the user. Defaults to "writer".
        notify (bool, optional): Whether to notify the user about the sharing. Defaults to False.
        email_message (str, optional): The message to include in the notification email.
        with_link (bool, optional): Whether to include a link to the shared document in the notification email. Defaults to False.

    Returns:
        gspread.Spreadsheet: The updated spreadsheet object.
    """
    spreadsheet.share(email, perm_type=user_type, role=user_role, notify=notify, email_message=email_message, with_link=with_link)
    return spreadsheet

def generate_short_id(variables: dict) -> tuple[str, str]:
    """
    Generate an 8-character ID using a dictionary as input.

    Args:
        variables (dict): A dictionary containing the variables to be serialized.

    Returns:
        tuple: A tuple containing the generated short ID and the serialized variables.
    """
    # Serialize variables into JSON string
    serialized_variables = json.dumps(variables, sort_keys=True)
    # Generate a hash of the serialized variables
    hash_value = hashlib.sha256(serialized_variables.encode()).hexdigest()
    # Take the first 8 characters of the hash as the short ID
    short_id = hash_value[:8]
    return short_id, serialized_variables

def df_transform_column_as_list(column: pd.Series) -> pd.Series:
    """
    Transform a pandas Series where each cell is a string representation of a list,
    a single value, or already a list into a pandas Series with each cell as a list.

    Args:
        column (pd.Series): The input pandas Series to transform.

    Returns:
        pd.Series: A pandas Series with each cell as a list.
    """
    def transform(cell):
        if isinstance(cell, str):
            # Check if it's a list formatted as string, and convert to list
            if cell == "nan":
                values = []
            else:
                try:
                    values = ast.literal_eval(cell)
                except Exception as e:
                    # If it's a single URL as string, make it a list
                    values = [cell]
        elif isinstance(cell, (int, float, bool)):
            # Convert single value to list
            values = [cell]
        elif isinstance(cell, list):
            # If it's already a list, use it as is
            values = cell
        elif cell is None:
            values=[]
        else:
            values=[cell]
        return values

    return column.apply(transform)


def top_rows_per_category(df: pd.DataFrame, 
                          col_to_sort: str, 
                          col_to_gb: str, 
                          cols_to_keep: list[str], 
                          top_rows: int) -> pd.DataFrame:
    """
    Select the top rows for each category in a dataframe.

    Args:
        df (pd.DataFrame): The input dataframe.
        col_to_sort (str): The column name by which to sort the rows.
        col_to_gb (str): The column name to group by.
        cols_to_keep (List[str]): The list of columns to keep in the final output.
        top_rows (int): The number of top rows to select for each group.

    Returns:
        pd.DataFrame: A dataframe containing the top rows for each category.
    """
    df_gb = (df.sort_values(by=col_to_sort, ascending=False)
                 .groupby(col_to_gb)
                 .apply(lambda group: group.head(top_rows))
                 .reset_index(drop=True)
                )[cols_to_keep]
    return df_gb



def unrar_file(rar_file_path : str, output_dir : str) -> None:
    """
    Extracts a .rar file to the specified output directory using the unrar command.
    
    Args:
        rar_file_path (str): The path to the .rar file.
        output_dir (str): The directory where the contents should be extracted.
    
    Returns:
        None
    """
    try:
        # Ensure the output directory exists
        subprocess.run(['mkdir', '-p', output_dir], check=True)
        
        # Run the unrar command
        result = subprocess.run(['unrar', 'x', '-y', rar_file_path, output_dir], 
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Check if the extraction was successful
        if result.returncode != 0:
            print(f"Extraction failed. Error: {result.stderr}")
            
    except Exception as e:
        print(f"An error occurred: {e}")


def fill_nan(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fill missing values in a DataFrame with appropriate defaults based on the column data type.

    For string columns, missing values are replaced with an empty string.
    For numeric columns, missing values are replaced with zero.
    For datetime columns, missing values are replaced with the default date '1970-01-01'.
    For other types, missing values are filled with NaN.

    Args:
        df (DataFrame): The DataFrame in which missing values will be filled.

    Returns:
        DataFrame: The DataFrame with missing values filled.
    """
    mixed_columns = df.columns[df.isna().any()]

    for col in mixed_columns:
        if df[col].dtype == 'object':
            # For string columns, replace NaN with an empty string
            df[col] = df[col].fillna('')
        elif pd.api.types.is_numeric_dtype(df[col]):
            # For numeric columns, replace NaN with the column mean
            df[col] = df[col].fillna(0)
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            # For datetime columns, replace NaN with a default date
            default_date = pd.Timestamp('1970-01-01')
            df[col] = df[col].fillna(default_date)
        else:
            # For other types, we can use a general approach, such as fill with None or NaN
            df[col] = df[col].fillna(None)

    return df

def detect_encoding(file_path : str) -> str:
    """
    Detect the encoding of a file.

    Args:
        file_path (str): The path to the file whose encoding needs to be detected.

    Returns:
        str: The detected encoding of the file.
    """
    with open(file_path, 'rb') as file:
        raw_data = file.read()
    result = chardet.detect(raw_data)
    return result['encoding']

def remove_empty_folders(path: str):
    """
    Recursively remove empty folders from the specified directory.

    Parameters:
    - path (str): Path to the directory to scan for empty folders.
    """
    # Iterate over the directory tree
    for root, dirs, files in os.walk(path, topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            # If the directory is empty, remove it
            if not os.listdir(dir_path):
                os.rmdir(dir_path)
                print(f"Removed empty folder: {dir_path}")


def categorize_percentiles(percentile: float) -> str:
    """
    Categorizes a percentile value into a string representing its range.

    Args:
        percentile (float): The percentile value (between 0 and 1).

    Returns:
        str: The category of the percentile value.

    Raises:
        ValueError: If the percentile value is outside the range [0, 1].
    """
    if not (0 <= percentile <= 1):
        raise ValueError("Percentile must be between 0 and 1 inclusive.")
    
    if percentile <= 0.1:
        return '0-10%'
    elif percentile <= 0.2:
        return '10-20%'
    elif percentile <= 0.3:
        return '20-30%'
    elif percentile <= 0.4:
        return '30-40%'
    elif percentile <= 0.5:
        return '40-50%'
    elif percentile <= 0.6:
        return '50-60%'
    elif percentile <= 0.7:
        return '60-70%'
    elif percentile <= 0.8:
        return '70-80%'
    elif percentile <= 0.9:
        return '80-90%'
    else:
        return '90-100%'
    

def prepare_data_combinations(df: pd.DataFrame, columns_to_combine : list, col_date : str, date_format : str,  rolling_period : str, col_id : str, col_engagement : str) -> pd.DataFrame:
    """
    Prepare data for combinations of columns. Useful for data preparation before dataviz of time series. It adds missing rows for each combination of columns and date. 
    Args:
        df (pd.DataFrame): The input DataFrame.
        columns_to_combine (list): List of column names to combine.
        col_date (str): Name of the column containing dates.
        date_format (str): Format of the dates in col_date.
        rolling_period (str): Rolling period for grouping.
        col_id (str): Name of the column containing unique IDs.
        col_engagement (str): Name of the column containing engagement values.
    Returns:
        pd.DataFrame: The prepared DataFrame with combinations of columns.
    """

    df_wt_combinations = df.copy()
    df_wt_combinations["date"] = pd.to_datetime(df_wt_combinations[col_date], format=date_format).to_numpy()

    # Create all possible combinations of columns indexes
    # all_combinations = create_combination_index(df_wt_combinations, columns_to_combine, "date", rolling_period)

    # If no columns to combine, just use the date for grouping
    if not columns_to_combine:
        df_wt_combinations = (df_wt_combinations
                              .set_index("date")
                              .resample(rolling_period)
                              .agg({col_id: "nunique", col_engagement: "sum"})
                              .fillna(0)
                              .reset_index())
    else:
        # # Create all possible combinations of columns indexes
        # all_combinations = create_combination_index(df_wt_combinations, columns_to_combine, "date", rolling_period)
        
        df_wt_combinations = (df_wt_combinations
                              .set_index(["date"])
                              .groupby(columns_to_combine)
                              .resample(rolling_period)
                              .agg({col_id: "nunique", col_engagement: "sum"})
                              .fillna(0)
                              .reset_index())
    
    return df_wt_combinations

# def create_combination_index(df : pd.DataFrame, columns : list, date_column : str, rolling_period : str) -> pd.MultiIndex:
#     """
#     Create all possible combinations of unique values from specified columns and date range.
    
#     Args:
#         df (pd.DataFrame): The input DataFrame
#         columns (list): List of column names to create combinations from
#         date_column (str): Name of the date column
#         rolling_period (str): Frequency for date range (e.g., '1D', '1W', '1M')
    
#     Returns:
#         pd.MultiIndex: MultiIndex with all combinations
#     """
#     # Create a list to store unique values for each column
#     unique_values = []
    
#     # Get unique values for each specified column
#     for col in columns:
#         unique_values.append(df[col].unique())
    
#     # Create date range
#     date_range = pd.date_range(start=df[date_column].min(),
#                                end=df[date_column].max(),
#                                freq=rolling_period)
    
#     # Add date range to the list of unique values
#     unique_values.append(date_range)
    
#     # Create MultiIndex from product of all unique values
#     all_combinations = pd.MultiIndex.from_product(unique_values,
#                                                   names=columns + [date_column])
    
#     return all_combinations

# def prepare_data_combinations(df: pd.DataFrame, columns_to_combine : list, col_date : str, date_format : str,  rolling_period : str, col_id : str, col_engagement : str) -> pd.DataFrame:
#     """
#     Prepare data for combinations of columns. Useful for data preparation before dataviz of time series. It adds missing rows for each combination of columns and date. 
#     Args:
#         df (pd.DataFrame): The input DataFrame.
#         columns_to_combine (list): List of column names to combine.
#         col_date (str): Name of the column containing dates.
#         date_format (str): Format of the dates in col_date.
#         rolling_period (str): Rolling period for grouping.
#         col_id (str): Name of the column containing unique IDs.
#         col_engagement (str): Name of the column containing engagement values.
#     Returns:
#         pd.DataFrame: The prepared DataFrame with combinations of columns.
#     """

#     df_wt_combinations = df.copy()
#     df_wt_combinations["date"] = pd.to_datetime(df_wt_combinations[col_date], format=date_format).to_numpy()

#     # Create all possible combinations of columns indexes
#     all_combinations = create_combination_index(df_wt_combinations, columns_to_combine, "date", rolling_period)

#     # If no columns to combine, just use the date for grouping
#     if not columns_to_combine:
#         df_wt_combinations = (df_wt_combinations
#                               .set_index("date")
#                               .groupby(pd.Grouper(freq=rolling_period))
#                               .agg({col_id: "nunique", col_engagement: "sum"})
#                               .fillna(0)
#                               .reset_index())
#     else:
#         # # Create all possible combinations of columns indexes
#         # all_combinations = create_combination_index(df_wt_combinations, columns_to_combine, "date", rolling_period)
        
#         df_wt_combinations = (df_wt_combinations
#                               .set_index(["date"])
#                               .groupby([*columns_to_combine, pd.Grouper(freq=rolling_period)])
#                               .agg({col_id: "nunique", col_engagement: "sum"})
#                               .reindex(all_combinations, fill_value=0)
#                               .reset_index())
    
#     return df_wt_combinations

def custom_ordering(df : pd.DataFrame, col_to_order : str, custom_order : list) -> pd.DataFrame:
    """
    Orders the values in a DataFrame column based on a custom order.
    Args:
        df (DataFrame): The DataFrame containing the column to be ordered.
        col_to_order (str): The name of the column to be ordered.
        custom_order (list): The custom order of values.
    Returns:
        DataFrame: The DataFrame with the column values ordered according to the custom order.
    """
    df[col_to_order] = pd.Categorical(df[col_to_order], categories=custom_order, ordered=True).to_numpy()
    return df

# def calcul_total_et_pourcentage(df : pd.DataFrame, col_gb : list, metrics : dict) -> pd.DataFrame:
#     """
#     Calculates the total and percentage values for the given metrics based on a grouping column.
#     Args:
#         df (DataFrame): The input DataFrame.
#         col_gb (list):  Names of the columns to group by.
#         metrics (dict): A dictionary of metrics to calculate.
#     Returns:
#         DataFrame: The modified DataFrame with total and percentage values added.

#     """
#     percentage_agregations = {f'per_{key}': lambda x: x[key] / x[f"total_{key}"] for key in list(metrics.keys())}

#     df = (df.join(df.groupby(col_gb)
#                   .agg(metrics)
#                   .add_prefix("total_"), on=col_gb
#                   )
#                 .assign(**percentage_agregations).fillna(0)
#         )
    
#     return df

def calcul_total_et_pourcentage(df : pd.DataFrame, col_gb : list, metrics : dict) -> pd.DataFrame:
    """
    Calculates the total and percentage values for the given metrics based on a grouping column.
    Args:
        df (DataFrame): The input DataFrame.
        col_gb (list):  Names of the columns to group by.
        metrics (dict): A dictionary of metrics to calculate.
    Returns:
        DataFrame: The modified DataFrame with total and percentage values added.

    """
    # percentage_agregations = {f'per_{key}': lambda x: x[key] / x[f"total_{key}"] for key in list(metrics.keys())}

    df = (df.join(df.groupby(col_gb)
                  .agg(metrics)
                  .add_prefix("total_"), on=col_gb
                  )
        )
    for key in list(metrics.keys()):
        df['per_' + key] = df[key] / df['total_' + key]
        df['per_' + key] = df['per_' + key].fillna(0)

    return df
