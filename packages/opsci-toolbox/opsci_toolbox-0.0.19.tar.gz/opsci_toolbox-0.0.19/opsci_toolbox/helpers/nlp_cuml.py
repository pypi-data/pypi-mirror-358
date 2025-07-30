from cuml import UMAP
import cudf
from sklearn.feature_selection import chi2
from cuml.feature_extraction.text import CountVectorizer
from cuml.cluster.hdbscan import HDBSCAN, all_points_membership_vectors, approximate_predict, membership_vector
import numpy as np 
from tqdm import tqdm
import os
from opsci_toolbox.helpers.common import load_pickle, create_dir, write_pickle
import cudf.pandas
cudf.pandas.install()
import pandas as pd 

def reduce_with_cuml_UMAP(embeddings: np.ndarray, 
                          n_neighbors: int = 5, 
                          n_components: int = 3, 
                          min_dist: float = 0.0, 
                          metric: str = "cosine", 
                          spread: float = 1.0,
                          learning_rate: float = 1.0, 
                          n_epochs:int = 300,
                          random_state:int = None
                           ) -> tuple:
    """
    Reduces the dimensionality of embeddings using UMAP with cuML library.

    Args:
        embeddings (np.ndarray): The input embeddings to be reduced.
        n_neighbors (int, optional): The number of nearest neighbors to consider. Defaults to 5.
        n_components (int, optional): The number of dimensions of the embedded space. Defaults to 3.
        min_dist (float, optional): The minimum distance between embedded points. Defaults to 0.0.
        metric (str, optional): The metric to use for distance computation. Defaults to "cosine".
        spread (float, optional): The effective scale of embedded points. Defaults to 1.0.

    Returns:
        reducer (UMAP): The UMAP reducer object.
        reduced_embeddings (np.ndarray): The reduced embeddings.
    """    
    reducer = UMAP(n_neighbors=n_neighbors, 
                   n_components=n_components, 
                   min_dist=min_dist, 
                   metric=metric,
                   spread = spread,
                   n_epochs=n_epochs, 
                   learning_rate=learning_rate,
                   random_state=random_state).fit(embeddings)
    
    reduced_embeddings = reducer.transform(embeddings)
    return reducer, reduced_embeddings


def supervised_reduce_with_cuml_UMAP(embeddings: np.ndarray, 
                          n_neighbors: int = 5, 
                          n_components: int = 3, 
                          min_dist: float = 0.0, 
                          metric: str = "cosine", 
                          spread: float = 1.0,
                          learning_rate: float = 1.0, 
                          n_epochs:int = 300,
                          y: np.ndarray = None,
                          convert_dtype: bool = False,
                          random_state:int=None
                           ) -> tuple:
    """
    Reduces the dimensionality of embeddings using UMAP with cuML library.

    Args:
        embeddings (np.ndarray): The input embeddings to be reduced.
        n_neighbors (int, optional): The number of nearest neighbors to consider. Defaults to 5.
        n_components (int, optional): The number of dimensions of the embedded space. Defaults to 3.
        min_dist (float, optional): The minimum distance between embedded points. Defaults to 0.0.
        metric (str, optional): The metric to use for distance computation. Defaults to "cosine".
        spread (float, optional): The effective scale of embedded points. Defaults to 1.0.

    Returns:
        reducer (UMAP): The UMAP reducer object.
        reduced_embeddings (np.ndarray): The reduced embeddings.
    """    
    reducer = UMAP(n_neighbors=n_neighbors, 
                   n_components=n_components, 
                   min_dist=min_dist, 
                   metric=metric,
                   spread = spread,
                   n_epochs=n_epochs, 
                   learning_rate=learning_rate,
                   random_state=random_state).fit(X = embeddings, y = y, convert_dtype = convert_dtype)
    
    reduced_embeddings = reducer.transform(embeddings)
    return reducer, reduced_embeddings

def transform_with_cuml_UMAP(reducer, 
                             new_embeddings: np.ndarray) -> np.ndarray:
    """
    Transform new data points using a UMAP object.

    Args:
        reducer (UMAP): The UMAP reducer object.
        new_embeddings (np.ndarray): The new data points to be transformed.

    Returns:
        reduced_embeddings (np.ndarray): The transformed embeddings.
    """
    reduced_embeddings = reducer.transform(new_embeddings)
    return reduced_embeddings


def hdbscan_cuml_clustering(embeddings: np.ndarray,
                            min_cluster_size: int = 5,
                            min_samples: int = None,
                            max_cluster_size: int = 0,
                            metric: str = 'euclidean',
                            alpha: float = 1.0,
                            p: int = 2,
                            cluster_selection_epsilon: float = 0.0,
                            cluster_selection_method: str = 'eom',
                            gen_min_span_tree: bool = False,
                            gen_single_linkage_tree_: bool = False,
                            prediction_data: bool = True) -> tuple:
    """
    Perform clustering using the HDBSCAN (Hierarchical Density-Based Spatial Clustering of Applications with Noise) algorithm.

    Args:
        embeddings : array-like or sparse matrix, shape (n_samples, n_features)
            The input data to be clustered.
        min_cluster_size : int, optional
            The minimum number of samples in a group for that group to be considered a cluster; groupings smaller than this size will be left as noise.
        min_samples : int or None, optional
            The number of samples in a neighborhood for a point to be considered as a core point. This includes the point itself. If ‘None’, it defaults to the min_cluster_size.
        max_cluster_size : int, optional (default=0)
            A limit to the size of clusters returned by the eom algorithm. Has no effect when using leaf clustering (where clusters are usually small regardless) and can also be overridden in rare cases by a high value for cluster_selection_epsilon. 
            Note that this should not be used if we want to predict the cluster labels for new points in future (e.g. using approximate_predict), as the approximate_predict function is not aware of this argument.
        metric : str or callable, optional
            The metric to use for distance computation. Default is 'euclidean'.
        alpha : float, optional
             Distance scaling parameter as used in robust single linkage.
        p : int, optional
            The Minkowski p-norm distance metric parameter. Default is None.
        cluster_selection_epsilon : float, optional
            A distance threshold. Clusters below this value will be merged. Note that this should not be used if we want to predict the cluster labels for new points in future (e.g. using approximate_predict), as the approximate_predict function is not aware of this argument.
        cluster_selection_method : {'eom', 'leaf'}, optional
            The method used to select clusters from the condensed tree. The standard approach for HDBSCAN* is to use an Excess of Mass algorithm to find the most persistent clusters. Alternatively you can instead select the clusters at the leaves of the tree – this provides the most fine grained and homogeneous clusters. Options are:
        approx_min_span_tree : bool, optional
            Whether to compute an approximation of the minimum spanning tree. Default is True.
        gen_min_span_tree : bool, optional
            Whether to populate the minimum_spanning_tree_ member for utilizing plotting tools. This requires the hdbscan CPU Python package to be installed.
        gen_condensed_tree : bool, optional
            Whether to populate the condensed_tree_ member for utilizing plotting tools. 
        gen_single_linkage_tree_ :  bool
            Whether to populate the single_linkage_tree_ member for utilizing plotting tools.
        prediction_data : bool, optional
            Whether the data is prediction data or not. Default is True.

    Returns:
        clusterer : hdbscan.HDBSCAN
            HDBSCAN clusterer object.
        labels : array, shape (n_samples,)
            Cluster labels for each point. Noisy samples are given the label -1.
        probabilities : array, shape (n_samples,)
            The probability of each sample being an outlier.
    """
    clusterer = HDBSCAN(min_cluster_size=min_cluster_size, 
                                min_samples=min_samples, 
                                max_cluster_size = max_cluster_size,  
                                metric=metric, 
                                alpha=alpha, 
                                p=p, 
                                cluster_selection_epsilon=cluster_selection_epsilon, 
                                cluster_selection_method=cluster_selection_method, 
                                gen_min_span_tree = gen_min_span_tree, 
                                prediction_data=prediction_data)

    clusterer.fit_predict(embeddings)
    
    return clusterer, clusterer.labels_, clusterer.probabilities_

def transform_with_cuml_HDBSCAN(clusterer, new_embeddings: np.ndarray) -> tuple:
    """
    Transform new data points using an HDBSCAN object.

    Args:
        clusterer : hdbscan.HDBSCAN
            The HDBSCAN clusterer object trained on the original data.
        new_embeddings : array-like or sparse matrix, shape (n_samples, n_features)
            The new data points to be transformed.

    Returns:
        new_data_topic : array, shape (n_samples,)
            Predicted cluster labels for each new data point.
        new_data_proba : array, shape (n_samples,)
            The probability of each new data point being an outlier.
    """
    new_data_topic, new_data_proba = approximate_predict(clusterer, new_embeddings)
    return new_data_topic, new_data_proba


def cuml_soft_clustering(clusterer) -> tuple:
    """
    Perform soft clustering using HDBSCAN.

    Args:
        clusterer : hdbscan.HDBSCAN
            The HDBSCAN clusterer object trained on the original data.

    Returns:
        soft_clusters_val : list of str. Predicted cluster labels for each data point, represented as strings.
        soft_clusters_proba : list of float. The maximum probability of each data point belonging to any cluster.
    """
    soft_clusters = all_points_membership_vectors(clusterer)
    soft_clusters_val = [str(np.argmax(x)) for x in soft_clusters] 
    soft_clusters_proba = [np.max(x) for x in soft_clusters] 
    return soft_clusters_val, soft_clusters_proba


def soft_cuml_clustering_new_data(clusterer, embeddings: np.ndarray) -> tuple:
    """
    Predict cluster memberships for new data points using HDBSCAN soft clustering.

    Args:
        clusterer : hdbscan.hdbscan_.HDBSCAN
            The HDBSCAN clusterer object trained on the original data.
        embeddings : array-like or sparse matrix, shape (n_samples, n_features)
            The new data points to be clustered.

    Returns:
        soft_clusters_val : list of str
            Predicted cluster labels for each new data point, represented as strings.
        soft_clusters_proba : list of float
            The maximum probability of each new data point belonging to any cluster.
    """
    soft_clusters = membership_vector(clusterer, embeddings)
    soft_clusters_val = [str(np.argmax(x)) for x in soft_clusters] 
    soft_clusters_proba = [np.max(x) for x in soft_clusters] 
    return soft_clusters_val, soft_clusters_proba

def process_UMAP(embedded_chunks_paths: list, path_reduced_embeddings_id: str, reducer, reencode: bool = False) -> list:
    """
    Process embeddings using UMAP reduction.

    Args:
        embedded_chunks_paths : list of str
            List of file paths containing the embedded chunks.
        path_reduced_embeddings_id : str
            Path to store the reduced embeddings.
        reducer : UMAP object
            The UMAP reducer object used for dimensionality reduction.
        reencode : bool, optional
            Whether to reencode the embeddings even if the reduced file already exists. Default is False.

    Returns:
        new_file_paths : list of str
            List of file paths to the reduced embeddings.
    """
    new_file_paths=[]
    for file_path in tqdm(embedded_chunks_paths, total=len(embedded_chunks_paths), desc="UMAP transform from files"):
        
        filename = os.path.splitext(os.path.basename(file_path))[0]
        new_filename = filename+"_reduce_embeddings.parquet"
        new_file_path = os.path.join(path_reduced_embeddings_id, new_filename)
    
        if not os.path.exists(new_file_path) or reencode:
            df = cudf_read_parquet(file_path)
            create_dir(path_reduced_embeddings_id)
            # embeddings = df["embeddings"].to_list()
            # embeddings = np.vstack(df['embeddings'].values)
            embeddings = np.vstack(df['embeddings'].to_pandas().tolist())
            reduced_embeddings = transform_with_cuml_UMAP(reducer, embeddings)
            reduced_embeddings_transformed=[list(e) for e in reduced_embeddings]
            df['reduced_embeddings'] = reduced_embeddings_transformed
            df.drop(columns=["embeddings"], inplace=True)
            print(path_reduced_embeddings_id, filename+"_reduce_embeddings")
            cudf_write_parquet(df, path_reduced_embeddings_id, filename+"_reduce_embeddings")
            new_file_paths.append(new_file_path)
        else:
            print("REDUCED EMBEDDINGS ALREADY EXISTS", file_path)
            new_file_paths.append(new_file_path)
    return new_file_paths



def process_HDBSCAN(clusterer,
                    reduced_embeddings_paths: list,
                    path_predictions_dataset_id: str,
                    run_soft_clustering: bool = False,
                    reencode: bool = False) -> list:
    """
    Process reduced embeddings using HDBSCAN clustering.

    Args:
        clusterer : hdbscan.hdbscan_.HDBSCAN
            The HDBSCAN clusterer object.
        reduced_embeddings_paths : list of str
            List of file paths containing the reduced embeddings.
        path_predictions_dataset_id : str
            Path to store the clustering predictions.
        run_soft_clustering : bool, optional
            Whether to perform soft clustering in addition to regular clustering. Default is False.
        reencode : bool, optional
            Whether to reencode the embeddings even if the clustering file already exists. Default is False.

    Returns:
        new_file_paths : list of str
            List of file paths to the clustering predictions.
    """    
    new_file_paths=[]
    for file_path in tqdm(reduced_embeddings_paths, total=len(reduced_embeddings_paths), desc="HDBSCAN transform from files"):
        
        filename = os.path.splitext(os.path.basename(file_path))[0]
        new_filename = filename+ "_predictions.parquet"
        new_file_path = os.path.join(path_predictions_dataset_id, new_filename)
        if not os.path.exists(new_file_path) or reencode:
            df = cudf_read_parquet(file_path)
            # reduced_embeddings = df["reduced_embeddings"].to_list()
            # reduced_embeddings = np.vstack(df['reduced_embeddings'].values)
            reduced_embeddings = np.vstack(df['reduced_embeddings'].to_pandas().tolist())
            topics, probas = transform_with_cuml_HDBSCAN(clusterer, reduced_embeddings)
            df["topic"]=topics.astype(int).astype(str)
            df["proba"]=probas
            if run_soft_clustering:
                soft_clusters, soft_proba = soft_cuml_clustering_new_data(clusterer, np.array(reduced_embeddings))
                df["soft_topic"]=soft_clusters
                df["soft_proba"]=soft_proba

            cudf_write_parquet(df, path_predictions_dataset_id, filename+ "_predictions")
            new_file_paths.append(new_file_path)
        else:
            print("CLUSTERING ALREADY EXISTS", file_path)
            new_file_paths.append(new_file_path)
    return new_file_paths

# def cuml_word_frequency_per_categorie(df: pd.DataFrame, col_text: str, col_cat: str, ngram_range: tuple = (1, 1), stop_words: list = [], n_words: int = 20, min_freq: int = 3) -> pd.DataFrame:
#     """
#     Calculate word frequency per category using cuML for GPU acceleration.

#     Parameters:
#         df : pandas DataFrame
#             DataFrame containing text data and corresponding categories.
#         col_text : str
#             Name of the column containing the text data.
#         col_cat : str
#             Name of the column containing the categories.
#         ngram_range : tuple, optional
#             The range for n-grams. Default is (1, 1) for unigrams.
#         stop_words : list, optional
#             List of stopwords to be ignored during frequency calculation. Default is an empty list.
#         n_words : int, optional
#             Number of top words to display per category. Default is 20.
#         min_freq : int, optional
#             Minimum frequency threshold for word occurrences per category. Default is 3.

#     Returns:
#         DataFrame
#             DataFrame containing word frequencies per category.

#     Description:
#         This function calculates word frequencies per category based on the provided DataFrame, considering the text data and corresponding categories. 
#         It filters out words with frequencies below the specified minimum frequency threshold and returns the top words for each category.
#     """
#     # Convert pandas DataFrame to cuDF DataFrame
#     gdf = cudf.DataFrame.from_pandas(df)

#     # Initialize cuML's CountVectorizer
#     count_vectorizer = CountVectorizer(analyzer='word', ngram_range=ngram_range, stop_words=stop_words)
    
#     # Fit and transform the text data
#     X_train_count = count_vectorizer.fit_transform(gdf[col_text])
#     X_names_count = count_vectorizer.get_feature_names()

#     # Initialize the resulting DataFrame
#     df_count = cudf.DataFrame()

#     # Calculate word frequencies per category
#     for cat in gdf[col_cat].unique().to_pandas().tolist():
#         word_count = X_train_count[gdf[col_cat] == cat].sum(axis=0)
#         df_count_tmp = cudf.DataFrame({col_cat: [cat]*len(X_names_count), "word": X_names_count, "freq": word_count.tolist()[0]}).sort_values(by="freq", ascending=False)
        
#         # Apply frequency and n_words filters
#         if n_words:
#             df_count_tmp = df_count_tmp.head(n_words)
#         if min_freq:
#             df_count_tmp = df_count_tmp[df_count_tmp["freq"] > min_freq]
        
#         # Concatenate the result to the main DataFrame
#         df_count = cudf.concat([df_count, df_count_tmp])
    
#     # Convert the result back to pandas DataFrame
#     return df_count.to_pandas()

def cuml_word_frequency_per_categorie(gdf: pd.DataFrame, col_text: str, col_cat: str, ngram_range: tuple = (1, 1), stop_words: list = [], n_words: int = 20, min_freq: int = 3) -> pd.DataFrame:
    """
    Calculate word frequency per category using cuML for GPU acceleration.

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
    # Convert pandas DataFrame to cuDF DataFrame
    # gdf = cudf.DataFrame.from_pandas(df))
    # print(type(gdf))
    # gdf = convert_df_to_cudf(gdf)
    
    # Initialize cuML's CountVectorizer
    count_vectorizer = CountVectorizer(analyzer='word', ngram_range=ngram_range, stop_words=stop_words)
    
    # Fit and transform the text data
    X_train_count = count_vectorizer.fit_transform(cudf.Series(gdf[col_text]))
    X_names_count = count_vectorizer.get_feature_names()

    # Initialize the resulting DataFrame
    df_count = cudf.DataFrame()

    # Calculate word frequencies per category
    for cat in gdf[col_cat].unique().tolist():
        word_count = X_train_count[gdf[col_cat] == cat].sum(axis=0)
        df_count_tmp = cudf.DataFrame({col_cat: [cat]*len(X_names_count), "word": X_names_count, "freq": word_count.tolist()[0]}).sort_values(by="freq", ascending=False)
        
        # Apply frequency and n_words filters
        if n_words:
            df_count_tmp = df_count_tmp.head(n_words)
        if min_freq:
            df_count_tmp = df_count_tmp[df_count_tmp["freq"] > min_freq]

        df_count_tmp['word'] = df_count_tmp['word'].astype(str)
        # Concatenate the result to the main DataFrame
        df_count = cudf.concat([df_count, df_count_tmp])
    
    # Convert the result back to pandas DataFrame
    return df_count.to_pandas()




# def cuml_chi2_per_category(lst_text: list, lst_categorie: list, col_cat: str, n_words: int = 10, p_value_limit: float = 0.95, min_freq: int = 3) -> pd.DataFrame:

#     # Convert input lists to cuDF Series
#     gdf_text = cudf.Series(lst_text)
#     gdf_categorie = cudf.Series(lst_categorie)
    
#     # Initialize cuML's CountVectorizer
#     count_vectorizer = CountVectorizer(analyzer='word')
    
#     # Fit and transform the text data
#     X_train_count = count_vectorizer.fit_transform(gdf_text)
#     X_names_count = count_vectorizer.get_feature_names()
    
#     # Initialize the resulting DataFrame
#     df_chi = cudf.DataFrame()
    
#     # Calculate Chi-squared statistics per category
#     unique_categories = gdf_categorie.unique().to_pandas().tolist()    
#     for cat in unique_categories:
#         cat_series = (gdf_categorie == cat).astype(int).to_pandas()
#         chi2_scores, p_values = chi2(X_train_count.get(), cat_series)
#         word_count = X_train_count[cat_series.astype(bool)].sum(axis=0).get()[0]
    
#         df_chi_tmp = cudf.DataFrame({
#             col_cat: cat,
#             "relevant_words_chi2": X_names_count,
#             "chi2": chi2_scores,
#             "p_values": 1 - p_values,
#             "word_count_per_class": word_count
#         }).sort_values(by="chi2", ascending=False).head(n_words)
        
#         # Filter based on p_values and word_count
#         df_chi_tmp = df_chi_tmp[df_chi_tmp["p_values"] > p_value_limit]
#         df_chi_tmp = df_chi_tmp[df_chi_tmp["word_count_per_class"] > min_freq]
        
#         df_chi = cudf.concat([df_chi, df_chi_tmp])
    
#     # Reset index
#     df_chi.reset_index(drop=True, inplace=True)
#     return df_chi.to_pandas()

def cuml_chi2_per_category(lst_text: list, lst_categorie: list, col_cat: str, n_words: int = 10, p_value_limit: float = 0.95, min_freq: int = 3) -> pd.DataFrame:
    """
    Calculate Chi-squared statistics for each category and return a DataFrame 
    of relevant words per category.

    Args:
        lst_text (List[str]): List of text documents.
        lst_categorie (List[str]): List of categories corresponding to each document.
        col_cat (str): Name of the category column in the resulting DataFrame.
        n_words (int, optional): Number of top words to return per category. Default is 10.
        p_value_limit (float, optional): The minimum p-value to filter relevant words. Default is 0.95.
        min_freq (int, optional): The minimum frequency of words to be considered relevant. Default is 3.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the relevant words for each category.
    """
    # Convert input lists to cuDF Series
    gdf_text = cudf.Series(lst_text)
    gdf_categorie = lst_categorie
    
    # Initialize cuML's CountVectorizer
    count_vectorizer = CountVectorizer(analyzer='word')
    
    # Fit and transform the text data
    X_train_count = count_vectorizer.fit_transform(gdf_text)
    X_names_count = count_vectorizer.get_feature_names()
    
    # Initialize the resulting DataFrame
    df_chi = cudf.DataFrame()
    
    # Calculate Chi-squared statistics per category
    unique_categories = gdf_categorie.unique().tolist()    
    for cat in unique_categories:
        cat_series = (gdf_categorie == cat).astype(int)
        chi2_scores, p_values = chi2(X_train_count.get(), cat_series)
        word_count = X_train_count[cat_series.astype(bool)].sum(axis=0).get()[0]
    
        df_chi_tmp = cudf.DataFrame({
            col_cat: cat,
            "relevant_words_chi2": X_names_count,
            "chi2": chi2_scores,
            "p_values": 1 - p_values,
            "word_count_per_class": word_count
        }).sort_values(by="chi2", ascending=False).head(n_words)
        
        # Filter based on p_values and word_count
        df_chi_tmp = df_chi_tmp[df_chi_tmp["p_values"] > p_value_limit]
        df_chi_tmp = df_chi_tmp[df_chi_tmp["word_count_per_class"] > min_freq]
        
        df_chi = cudf.concat([df_chi, df_chi_tmp])
    
    # Reset index
    df_chi.reset_index(drop=True, inplace=True)
    return df_chi.to_pandas()

def cudf_write_parquet(df: cudf.DataFrame, path: str, filename: str) -> str:
    """
    Write a cuDF DataFrame to a Parquet file.

    Args:
        df (cudf.DataFrame): The cuDF DataFrame to be written.
        path (str): The directory path where the file should be saved.
        filename (str): The name of the file without extension.

    Returns:
        str: The file path of the saved Parquet file.
    """
    file_path = os.path.join(path, str(filename)+".parquet")
    df.to_parquet(file_path)
    return file_path

def cudf_read_parquet(path: str, cols : list = None) -> cudf.DataFrame:
    """
    Read a Parquet file into a cuDF DataFrame.

    Args:
        path (str): The file path to the Parquet file.

    Returns:
        cudf.DataFrame: The read cuDF DataFrame.
    """
    if cols : 
        df = cudf.read_parquet(path, columns=cols)
    else :
        df = cudf.read_parquet(path)
    return df 

def convert_df_to_cudf(df: pd.DataFrame) -> cudf.DataFrame:
    """
    Convert a pandas DataFrame to a cuDF DataFrame.

    Args:
        df (pd.DataFrame): The pandas DataFrame to convert.

    Returns:
        cudf.DataFrame: The resulting cuDF DataFrame.
    """
    return cudf.DataFrame.from_pandas(df)

def convert_cudf_to_df(cdf: cudf.DataFrame) -> pd.DataFrame:
    """
    Convert a cuDF DataFrame to a pandas DataFrame.

    Args:
        cdf (cudf.DataFrame): The cuDF DataFrame to convert.

    Returns:
        pd.DataFrame: The resulting pandas DataFrame.
    """
    return cdf.to_pandas()


def cudf_encode_chunked_files(chunk_files_paths: list, 
                         HF_encoder, 
                         cols: list, 
                         col_text: str, 
                         path_embedded_chunks: str, 
                         reencode: bool = False) -> list:
    """
    Encode text from files and save the results in another pickle file.
    
    Args:
        chunk_files_paths (List[str]): List of file paths containing documents.
        HF_encoder (Encoder): Encoder object for text vectorization.
        cols (List[str]): Columns to keep in the resulting DataFrame.
        col_text (str): Column containing text data in the DataFrame.
        path_embedded_chunks (str): Path to save the embedded chunks.
        reencode (bool, optional): Whether to re-encode files even if they already exist. Defaults to False.
    
    Returns:
        List[str]: List of paths for newly created files.
    """
    new_file_paths=[]
    for file in tqdm(chunk_files_paths, total=len(chunk_files_paths), desc="Encoding text from files"):
        new_filename = os.path.splitext(os.path.basename(file))[0]+"_embedded"
        new_file_path = os.path.join(path_embedded_chunks, new_filename+".parquet")
        # on vérifie si on a déjà effectué l'encodage, si reencode == True, on effectue quand même la procédure
        if not os.path.exists(new_file_path) or reencode:
            current_df = cudf_read_parquet(file)

            text_list = current_df[col_text].to_arrow().to_pylist()
            
            # text vectorization
            embeddings = HF_encoder.embed_documents(text_list)

            # on crée un dataframe avec les embeddings
            current_df = current_df[cols]
            current_df['embeddings'] = embeddings

            # on sauvegarde
            new_file_path = cudf_write_parquet(current_df, path_embedded_chunks, new_filename)
            new_file_paths.append(new_file_path)
        else :
            new_file_paths.append(new_file_path)

    return new_file_paths

def split_df_into_chunks(df: pd.DataFrame, path: str, name: str, chunk_size: int = 10000) -> list[str]:
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
        file_path = cudf_write_parquet(chunk, path, filename)
        file_paths.append(file_path)

    return file_paths