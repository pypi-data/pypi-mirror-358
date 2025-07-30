from datetime import datetime, timezone
import pandas as pd

def get_now() -> datetime:
    """
    Gets the current datetime in Coordinated Universal Time (UTC).

    Returns:
        now (datetime): The current datetime in UTC.
    """
    return datetime.now(timezone.utc)

def str_to_datetime(date_string: str, format: str = "%a %b %d %H:%M:%S %z %Y") -> str:
    """
    Converts a string representation of a datetime to a datetime object.

    Args:
        date_string (str): The string representation of the datetime.
        format (str, optional): The format of the datetime string. Defaults to "%a %b %d %H:%M:%S %z %Y".
        -- Facebook Format : "2024-02-13T15:20:23+0000" = "%Y-%m-%dT%H:%M:%S%z"
        -- Youtube : '1970-01-01T00:00:00Z' = "%Y-%m-%dT%H:%M:%SZ" 
        -- Twitter RapidAPI : '%a %b %d %H:%M:%S %z %Y'

    Returns:
        formated_date (Union[datetime, str]): The datetime object if conversion is successful, otherwise the original string.
    """

    try:
        formated_date = datetime.strptime(date_string, format)
        return formated_date
    except Exception as e:
        pass
        print(e)
        return date_string

def datetime_to_str(date: datetime, date_format: str = '%Y-%m-%dT%H:%M:%SZ') -> str:
    """
    Converts a datetime object to a string representation.

    Args:
        date (datetime): The datetime object to convert.
        date_format (str, optional): The format of the output datetime string. Defaults to '%Y-%m-%dT%H:%M:%SZ'.

    Returns:
        str_date (str): The string representation of the datetime object.
    """    
    return date.strftime(date_format)

def number_of_days(start_date: datetime, end_date: datetime) -> int:
    """
    Calculates the number of days between two datetime objects.

    Args:
        start_date (datetime): The start date.
        end_date (datetime): The end date.

    Returns:
        days_difference (int): The number of days between the start and end dates.
    """
    # Calculate the difference
    time_difference = end_date -  start_date
    # Extract the number of days from the timedelta object
    days_difference = time_difference.days
    return days_difference

def df_col_to_datetime(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """
    Converts a column in a pandas DataFrame to datetime format.

    Args:
        df (pd.DataFrame): The pandas DataFrame.
        col (str): The name of the column to convert to datetime.

    Returns:
        df (pd.DataFrame): The DataFrame with the specified column converted to datetime format.
    """
    df[col] = pd.to_datetime(df[col])
    return df


# from dateutil import parser
# from datetime import datetime

# def detect_date_format(date_string):
#     formats = [
#         # Date formats
#         "%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%m-%d-%Y", 
#         "%Y/%m/%d", "%d/%m/%Y", "%Y.%m.%d", "%d.%m.%Y",
#         "%d %b %Y", "%d %B %Y", "%b %d, %Y", "%B %d, %Y",
#         "%d-%b-%Y", "%d-%B-%Y", "%b-%d-%Y", "%B-%d-%Y",
#         # Date and time formats
#         "%Y-%m-%d %H:%M:%S", "%d-%m-%Y %H:%M:%S", "%m/%d/%Y %H:%M:%S", "%m-%d-%Y %H:%M:%S",
#         "%Y/%m/%d %H:%M:%S", "%d/%m/%Y %H:%M:%S", "%Y.%m.%d %H:%M:%S", "%d.%m.%Y %H:%M:%S",
#         "%d %b %Y %H:%M:%S", "%d %B %Y %H:%M:%S", "%b %d, %Y %H:%M:%S", "%B %d, %Y %H:%M:%S",
#         "%d-%b-%Y %H:%M:%S", "%d-%B-%Y %H:%M:%S", "%b-%d-%Y %H:%M:%S", "%B-%d-%Y %H:%M:%S",
#         # Time formats with milliseconds
#         "%Y-%m-%d %H:%M:%S.%f", "%d-%m-%Y %H:%M:%S.%f", "%m/%d/%Y %H:%M:%S.%f", "%m-%d-%Y %H:%M:%S.%f",
#         "%Y/%m/%d %H:%M:%S.%f", "%d/%m/%Y %H:%M:%S.%f", "%Y.%m.%d %H:%M:%S.%f", "%d.%m.%Y %H:%M:%S.%f",
#         "%d %b %Y %H:%M:%S.%f", "%d %B %Y %H:%M:%S.%f", "%b %d, %Y %H:%M:%S.%f", "%B %d, %Y %H:%M:%S.%f",
#         "%d-%b-%Y %H:%M:%S.%f", "%d-%B-%Y %H:%M:%S.%f", "%b-%d-%Y %H:%M:%S.%f", "%B-%d-%Y %H:%M:%S.%f",
#         # ISO format
#         "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f",
#         "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S.%f",
#         "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d %H:%M:%S%z",
#         # Additional formats
#         "%y/%m/%d %H:%M:%S", "%d/%m/%y %H:%M:%S", "%y-%m-%d %H:%M:%S", "%d-%m-%y %H:%M:%S",
#     ]

#     for date_format in formats:
#         try:
#             # Try to parse the date string with each format
#             parsed_date = datetime.strptime(date_string, date_format)
#             return date_format
#         except ValueError:
#             continue

#     return None

# def detect_date_format(date_string):
#     try:
#         # Use dateutil parser to parse the date string
#         parsed_date = parser.parse(date_string, fuzzy=False)
#         return parsed_date
#     except ValueError:
#         return None