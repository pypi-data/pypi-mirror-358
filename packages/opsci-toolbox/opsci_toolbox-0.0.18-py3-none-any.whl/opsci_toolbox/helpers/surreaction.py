import pandas as pd
from tqdm import tqdm

def generate_index(df : pd.DataFrame, col_author_id : str ='author_id', col_date :  str = 'created_time') -> pd.DataFrame:
    """
    Generates an index based on author ID and creation date.
    
    Args:
        df (pd.DataFrame): The input DataFrame containing author IDs and creation dates.
        col_author_id (str): The column name for author IDs. Default is 'author_id'.
        col_date (str): The column name for creation dates. Default is 'created_time'.
    
    Returns:
        pd.DataFrame: The DataFrame with a new 'index' column containing the generated indices.
    """
    res=[]
    for i, row in tqdm(df.iterrows(), total=df.shape[0], desc="generation des index"): 
        new_index=".".join([ str(i) for i in [ row[col_author_id], row[col_date].year, row[col_date].month, row[col_date].day]])
        res.append(new_index)
    df["index"]=res
    
    return df
                     
def avg_performance(df : pd.DataFrame, 
                    col_date : str ='created_time', 
                    col_author_id : str ='author_id', 
                    col_engagement :  list =['shares', 'comments', 'reactions', 'likes','top_comments', 'love', 'wow', 'haha', 
                                    'sad', 'angry','total_engagement', 'replies', 'percentage_replies'], 
                    rolling_period :  str ='7D') -> pd.DataFrame:
    
    """
    Computes average performance on a rolling period for a list of engagement metrics.

    Args:
        df (pd.DataFrame): The input DataFrame containing engagement metrics.
        col_date (str): The column name for creation dates. Default is 'created_time'.
        col_author_id (str): The column name for author IDs. Default is 'author_id'.
        col_engagement (List[str]): A list of columns representing engagement metrics.
        rolling_period (str): The rolling period for calculating the average. Default is '7D'.

    Returns:
        pd.DataFrame: The DataFrame with additional columns containing the rolling average of engagement metrics.
    """
                     
    # Nettoyage au cas où
    df[col_date] = pd.to_datetime(df[col_date]) 
    df = df.sort_values([col_author_id, col_date]) 

    # Le point central c'est la colone created_time, on la met en index.
    # Ensuite on groupe par author_id en gardant les colonnes de valeurs.
    # On applique la moyenne mean sur un rolling tous les 2 jours. Automatiquement il va prendre l'index, ici created_time comme pivot. 
    # On met tout à plat
    average = df.set_index(col_date).groupby(col_author_id)[col_engagement].rolling(rolling_period).mean(numeric_only=True).reset_index()
                     
    # Sur les résultats précédent, on simplifie pour récupérer une liste avec juste la liste jour / author_id
    average = average.set_index(col_date).groupby([col_author_id]).resample('1D').last(numeric_only=True).reset_index()

    # On génère nos supers index
    df=generate_index(df, col_author_id =col_author_id, col_date=col_date)    
    
    average = generate_index(average, col_author_id = col_author_id, col_date=col_date)

    # On fusionne 
    df = pd.merge(df, average[['index']+col_engagement], how='left', on=['index'], suffixes=('', '_avg'))
    
    return df

def kpi_reaction(df : pd.DataFrame, cols : list) -> pd.DataFrame:
    """
    Computes the overreaction rate for each column in the DataFrame.

    Args:
        df (pd.DataFrame): The input DataFrame containing engagement metrics.
        cols (List[str]): A list of column names for which to calculate the overreaction rate.

    Returns:
        pd.DataFrame: The DataFrame with additional columns containing the overreaction rates.
    """
    for col in cols:
        df['tx_'+col]=(df[col]-df[col+'_avg'])/(df[col]+df[col+'_avg'])
    return df

def get_reactions_type(df : pd.DataFrame, cols : list, col_dest : str) -> pd.DataFrame:
    """
    Returns the reaction type based on a list of metrics for each row in the DataFrame.

    Args:
        df (pd.DataFrame): The input DataFrame containing engagement metrics.
        cols (List[str]): A list of column names for which to determine the reaction type.
        col_dest (str): The name of the column to store the reaction type in.

    Returns:
        pd.DataFrame: The DataFrame with additional column containing the reaction types.
    """
    all_val=[]
    
    for i,row in tqdm(df.iterrows(), total=df.shape[0], desc="qualification des posts"):
        
        str_val=''
        count=0
        for col in cols:
            if row[col]>0:
                str_val=str_val+' '+col.replace('tx_', 'sur-')
                count=count+1
        if count==0:
            str_val="sous reaction"
        if count==len(cols):
            str_val="sur reaction totale"
            
        all_val.append(str_val.strip())
            
    df[col_dest]=all_val       
    return df

def compute_surreaction(df : pd.DataFrame, col_date : str, col_author_id : str, cols_sureaction_metrics : list, cols_typologie_sureaction : list, rolling_period_sureaction : str = '7D') -> pd.DataFrame:
    """
    Computes surreaction rates and typology for a DataFrame containing engagement metrics.

    Args:
        df (pd.DataFrame): The input DataFrame containing engagement metrics.
        col_date (str): The column name for creation dates.
        col_author_id (str): The column name for author IDs.
        cols_sureaction_metrics (List[str]): A list of column names for which to calculate surreaction rates.
        cols_typologie_sureaction (List[str]): A list of column names for categorizing the forms of reaction.
        rolling_period_sureaction (str): The rolling period for calculating the average and surreaction rates. Default is '7D'.

    Returns:
        pd.DataFrame: The DataFrame with additional columns containing surreaction rates and typology.
    """
    # on désactive temporairement les messages d'alerte
    pd.options.mode.chained_assignment = None  # default='warn'
    # on calcule nos performances moyennes pour une liste de métriques
    df= avg_performance(
        df, 
        col_date=col_date, 
        col_author_id=col_author_id, 
        col_engagement= cols_sureaction_metrics, 
        rolling_period=rolling_period_sureaction
        ) 

    # on calcule les taux de sur-réaction pour notre liste de métriques
    df=kpi_reaction(df, cols_sureaction_metrics)
    cols_tx_engagement=['tx_'+c for c in cols_sureaction_metrics]
    df[cols_tx_engagement]=df[cols_tx_engagement].fillna(-1)

    # on supprime nos colonnes contenant la performance moyenne (on ne devrait plus en avoir besoin)
    cols_to_drop = [c for c in df.columns if c.lower()[-4:] == '_avg']
    df.drop(columns=cols_to_drop, inplace=True)

    # on catégorise les formes de réaction
    cols_typologie = ["tx_"+ col for col in cols_typologie_sureaction]
    df=get_reactions_type(df, cols_typologie, 'type_engagement')

    # on réactive les alertes
    pd.options.mode.chained_assignment = 'warn'  # default='warn'  
    return df