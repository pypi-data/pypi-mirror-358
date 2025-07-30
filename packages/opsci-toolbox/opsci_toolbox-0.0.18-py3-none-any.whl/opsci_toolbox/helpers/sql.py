import mysql.connector
import pandas as pd
from mysql.connector import errorcode

def connect_to_mysql_database(host: str = 'localhost', user: str = 'root', password: str = 'password', database: str = 'subs'):
    """
    Connect to a MySQL database.

    Parameters:
    - host (str): The host of the database. Default is 'localhost'.
    - user (str): The username to use for connecting to the database. Default is 'root'.
    - password (str): The password to use for connecting to the database. Default is 'password'.
    - database (str): The name of the database to connect to. Default is 'subs'.

    Returns:
    - mysql.connector.connection.MySQLConnection: The connection object if connection is successful.
    - None: If the connection fails.
    """
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        return conn
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
        return None

def execute_query(conn: mysql.connector.connection.MySQLConnection, query: str) -> pd.DataFrame:
    """
    Execute a SQL query and return the results as a pandas DataFrame.

    Parameters:
    - conn (mysql.connector.connection.MySQLConnection): The connection object to the database.
    - query (str): The SQL query to be executed.

    Returns:
    - pd.DataFrame: A DataFrame containing the results of the query.
    """
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    column_names = [i[0] for i in cursor.description]
    df = pd.DataFrame(results, columns=column_names)
    cursor.close()
    return df