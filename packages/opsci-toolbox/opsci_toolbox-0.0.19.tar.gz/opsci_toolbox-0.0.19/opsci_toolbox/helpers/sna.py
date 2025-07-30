from nltk.collocations import BigramCollocationFinder
import networkx as nx
from sklearn.feature_extraction.text import CountVectorizer
from community import community_louvain
from collections import defaultdict
from opsci_toolbox.helpers.dataviz import generate_color_palette_with_colormap, generate_random_hexadecimal_color
from opsci_toolbox.helpers.common import scale_list
import pandas as pd
import math
from collections import Counter
from opsci_toolbox.helpers.dataviz import boxplot
from fa2_modified import ForceAtlas2

def create_subgraph_min_metric(G: nx.Graph, metric: str = "degree", min_value: float = 2) -> nx.Graph:
    """
    Creates a subgraph containing only the nodes that have at least the specified minimum value for a given metric.

    Args:
        G (nx.Graph): The input graph.
        metric (str, optional): The node metric to filter nodes by (e.g., "degree", "in_degree", "out_degree", "degree_centrality"). Default is "degree".
        min_value (float, optional): The minimum value required for nodes to be included in the subgraph. Default is 2.

    Returns:
        subgraph (nx.Graph): A subgraph containing only the nodes with at least the specified minimum metric value.
    """
    
    if metric == "degree":
        nodes_with_min_metric = [node for node, value in G.degree() if value >= min_value]
    elif metric == "in_degree" and G.is_directed():
        nodes_with_min_metric = [node for node, value in G.in_degree() if value >= min_value]
    elif metric == "out_degree" and G.is_directed():
        nodes_with_min_metric = [node for node, value in G.out_degree() if value >= min_value]
    elif metric == "degree_centrality":
        centrality = nx.degree_centrality(G)
        nodes_with_min_metric = [node for node, value in centrality.items() if value >= min_value]
    elif metric == "betweenness_centrality":
        centrality = nx.betweenness_centrality(G)
        nodes_with_min_metric = [node for node, value in centrality.items() if value >= min_value]
    elif metric == "closeness_centrality":
        centrality = nx.closeness_centrality(G)
        nodes_with_min_metric = [node for node, value in centrality.items() if value >= min_value]
    else:
        raise ValueError(f"Unsupported metric: {metric}")
    
    subgraph = G.subgraph(nodes_with_min_metric).copy()
    return subgraph
    
def group_nodes_by_values(dictionnary : dict) -> dict:
    """
    Group nodes by their values from a dictionary.

    Args:
        dictionnary (Dict[Any, Any]): A dictionary where keys are nodes and values are attributes 
                                      or categories.

    Returns:
        Dict[Any, List[Any]]: A dictionary where each key is a unique value from the input dictionary,
                              and the corresponding value is a list of nodes that have that value.

    """
    new_dict = {}
    for node, comm in dictionnary.items():
        if comm not in new_dict:
            new_dict[comm] = []
        new_dict[comm].append(node)
    return new_dict

def graph_key_metrics(G : nx.Graph) -> dict:
    """
    Calculate key metrics for a NetworkX graph.

    Args:
        G (nx.Graph): The NetworkX graph for which to calculate metrics.

    Returns:
        Dict[str, float]: A dictionary containing the following metrics:
            - "nodes": Number of nodes in the graph.
            - "edges": Number of edges in the graph.
            - "density": Density of the graph.
            - "average_degree": Average degree of nodes in the graph.
            - "assortativity": Degree assortativity coefficient of the graph.
            - "transitivity": Transitivity (global clustering coefficient) of the graph.
    """
    num_nodes = G.number_of_nodes()
    num_edges = G.number_of_edges()
    density = nx.density(G)
    total_degree = sum(degree for _, degree in G.degree())
    avg_degree = total_degree / num_nodes if num_nodes > 0 else 0
    assortativity = nx.degree_assortativity_coefficient(G)
    transitivity = nx.transitivity(G)
    key_metrics = {
        "nodes": num_nodes,
        "edges" : num_edges,
        "density" : density,
        "average_degree" : avg_degree,
        "assortativity" : assortativity,
        "transitivity" : transitivity
    }
    return key_metrics

def communities_metrics(G : nx.Graph, nodes_by_community : dict) -> dict:
    """
    Calculate various metrics for communities within a subgraph.

    Args:
        G (nx.Graph): The NetworkX graph containing the communities.
        nodes_by_community (Dict[Any, List[Any]]): A dictionary where keys are community identifiers and
                                                   values are lists of nodes in each community.

    Returns:
        Dict[Any, Dict[str, float]]: A dictionary where each key is a community identifier, and the value 
                                     is another dictionary containing various metrics for that community.
    """
    communities_metrics = {}
    for comm, nodes in nodes_by_community.items():
        subgraph = G.subgraph(nodes)
        num_nodes = subgraph.number_of_nodes()
        num_edges = subgraph.number_of_edges()
        density = nx.density(subgraph)
        total_degree = sum(degree for _, degree in subgraph.degree())
        avg_degree = total_degree / num_nodes if num_nodes > 0 else 0
        assortativity = nx.degree_assortativity_coefficient(subgraph)
        transitivity = nx.transitivity(subgraph)
        communities_metrics[comm] = {
            "nodes": num_nodes,
            "edges": num_edges,
            "density": density,
            "average_degree": avg_degree,
            "assortativity": assortativity,
            "transitivity": transitivity,
        }
    return communities_metrics

def remove_attributes(G : nx.Graph, attributes : list = ['degree_centrality', 'in_degree_centrality', 'out_degree_centrality', 'eigenvector_centrality', 'degree', 'in_degree', 'out_degree', 'composante', 'betweenness_centrality', 'viz']) -> nx.Graph:
    """
    Remove specified attributes from all nodes in a NetworkX graph.

    Args:
        G (nx.Graph): The NetworkX graph from which to remove node attributes.
        attributes (List[str], optional): List of attribute names to remove from each node. 
                                          Defaults to common graph attributes.

    Returns:
        nx.Graph: The graph with the specified attributes removed from each node.
    """
    for node, attrs in G.nodes(data=True):
        for attr in attributes:
            attrs.pop(attr, None)
    return G

def compute_modularity(G : nx.Graph, resolution : float =1, col_name : str = "modularity") -> dict:
   """
    Compute modularity of a graph using the Louvain method and assign community labels as node attributes.

    Args:
        G (nx.Graph): The input graph for which to compute modularity.
        resolution (float, optional): The resolution parameter for the Louvain method. Default is 1.
        col_name (str, optional): The name of the node attribute to store community labels. Default is "modularity".

    Returns:
        Dict[int, int]: A dictionary mapping each node to its community.
   """
   try : 
      communities = nx.community.louvain_communities(G, resolution=resolution)
      community_dict=transform_dict_of_nodes(communities)
   except Exception as e:
      pass
      print(e)
      community_dict = {node: 0 for node in G.nodes()}
   nx.set_node_attributes(G, community_dict, col_name)
   return community_dict

def compute_degrees(G : nx.Graph, col_name : str = "degree") -> dict:
   """ 
   Compute the degrees of nodes in a graph and assign them as node attributes.

    Args:
        G (nx.Graph): The input graph for which to compute node degrees.
        col_name (str, optional): The name of the node attribute to store degrees. Default is "degree".

    Returns:
        Dict[int, int]: A dictionary mapping each node to its degree.
   """
   try:
      degree_dict = {node[0] : node[1] for node in list(G.degree())}      
   except Exception as e:
      pass
      print(e)
      degree_dict = {node: 0 for node in G.nodes()}
   nx.set_node_attributes(G, degree_dict, col_name)
   return degree_dict

def compute_in_degrees(G: nx.Graph, col_name : str = "in_degree") -> dict:
   """ 
   Compute the in degrees of nodes in a graph and assign them as node attributes.

    Args:
        G (nx.Graph): The input graph for which to compute node in degrees.
        col_name (str, optional): The name of the node attribute to store in degrees. Default is "in_degree".

    Returns:
        Dict[int, int]: A dictionary mapping each node to its degree.
   """
   try:
      in_degree_dict = {node[0] : node[1] for node in list(G.in_degree())}
   except Exception as e :
      pass
      print(e)
      in_degree_dict = {node: 0 for node in G.nodes()}
   nx.set_node_attributes(G, in_degree_dict, col_name)
   return in_degree_dict

def compute_out_degrees(G : nx.Graph, col_name : str = "out_degree") -> dict: 
   """ 
   Compute the out degrees of nodes in a graph and assign them as node attributes.

    Args:
        G (nx.Graph): The input graph for which to compute node out degrees.
        col_name (str, optional): The name of the node attribute to store in degrees. Default is "out_degree".

    Returns:
        Dict[int, int]: A dictionary mapping each node to its degree.
   """     
   try:
      out_degree_dict = {node[0] : node[1] for node in list(G.out_degree())}
   except Exception as e:
      pass
      print(e)
      out_degree_dict = {node: 0 for node in G.nodes()}
   nx.set_node_attributes(G, out_degree_dict, col_name)
   return out_degree_dict

def compute_degree_centrality(G : nx.Graph, col_name : str = "degree_centrality") -> dict :
   """
   Computes and sets Degree centrality metric for the nodes in the network graph.
   
   Args:
      network (nx.Graph): The network graph on which to compute centrality.
   
   Returns:
      None
   """
   try:
      degree_cent = nx.degree_centrality(G)
      nx.set_node_attributes(G, degree_cent, col_name)
      # print("Calcul de la centralité de degrés effectué")
   except Exception as e:
      pass
      # print(e, "Calcul de la centralité de degrés impossible")
      # Set a default value for degree centrality
      degree_cent = {node: 0 for node in G.nodes()}
      nx.set_node_attributes(G, degree_cent, col_name)
   return degree_cent

def compute_in_degree_centrality(G : nx.Graph, col_name : str = "in_degree_centrality") -> dict :
   """
   Computes and sets In Degree centrality metric for the nodes in the network graph.
   
   Args:
      network (nx.Graph): The network graph on which to compute centrality.
   
   Returns:
      None
   """
   try:
      in_degree_cent = nx.in_degree_centrality(G)
      nx.set_node_attributes(G, in_degree_cent, col_name)
   except Exception as e:
      pass
      # Set a default value for degree centrality
      in_degree_cent = {node: 0 for node in G.nodes()}
      nx.set_node_attributes(G, in_degree_cent, col_name)
   return in_degree_cent

def compute_out_degree_centrality(G : nx.Graph, col_name : str = "out_degree_centrality") -> dict :
   """
   Computes and sets Out Degree centrality metric for the nodes in the network graph.
   
   Args:
      network (nx.Graph): The network graph on which to compute centrality.
   
   Returns:
      None
   """
   try:
      out_degree_cent = nx.out_degree_centrality(G)
      nx.set_node_attributes(G, out_degree_cent, col_name)
   except Exception as e:
      pass
      # Set a default value for degree centrality
      out_degree_cent = {node: 0 for node in G.nodes()}
      nx.set_node_attributes(G, out_degree_cent, col_name)
   return out_degree_cent
      

def compute_eigenvector_centrality(G : nx.Graph, col_name : str = "eigenvector_centrality") -> dict :
   """
    Computes and sets Eigenvector centrality metric for the nodes in the network graph.
    
    Args:
        network (nx.Graph): The network graph on which to compute centrality.
    
    Returns:
        None
    """
   ### CALCUL DE LA CENTRALITE DE VECTEUR PROPRE
   try:
      eigenvector_centrality = nx.eigenvector_centrality(G)
      nx.set_node_attributes(G, eigenvector_centrality, col_name)
      # print("Calcul de la centralité de vecteur propre effectué")
   except Exception as e:
      pass
      # print(e, "Calcul de la centralité de vecteur propre impossible")
      # Set a default value for centrality
      eigenvector_centrality = {node: 0 for node in G.nodes()}
      nx.set_node_attributes(G, eigenvector_centrality, col_name)
   return eigenvector_centrality

def compute_betweenness_centrality(G : nx.Graph, col_name : str = "betweenness_centrality") -> dict :
   """
   Computes and sets Betweeness centrality metric for the nodes in the network graph.
   
   Args:
      network (nx.Graph): The network graph on which to compute centrality.
   
   Returns:
      None
   """
   try:
      betweenness_cent = nx.betweenness_centrality(G, k=None, normalized=True, weight='weight', endpoints=False, seed=None)
      nx.set_node_attributes(G, betweenness_cent, col_name)
      # print("Calcul de l'intermédiarité effectué")
   except Exception as e:
      pass
      # print(e, "Calcul de l'intermédiarité impossible")
      # Set a default value for betweenness centrality
      betweenness_cent = {node: 0 for node in G.nodes()}
      nx.set_node_attributes(G, betweenness_cent, col_name)
   return betweenness_cent

def calcul_composantes_connexes(G : nx.Graph, col_name : str = "composante") -> dict:
   """
   Calculate weakly connected components in a graph and assign component labels as node attributes.

   Args:
        G (nx.Graph): The input graph.
        col_name (str, optional): The name of the node attribute to store component labels. Default is "composante".

   Returns:
        List[set]: A list of sets, each set containing nodes belonging to a weakly connected component.
   """
   composantes_connexes = sorted(nx.weakly_connected_components(G),
                                  key=len, # clé de tri - len = longueur de la composante
                                  reverse=True)
    
   composantes_dict = transform_dict_of_nodes(composantes_connexes)
   nx.set_node_attributes(G, composantes_dict, col_name)
   return composantes_connexes

def filtrer_composante_principale(G: nx.Graph, composantes_connexes : dict) -> nx.Graph:
   """
    Filter the main component (largest weakly connected component) from a graph.

    Args:
        G (nx.Graph): The input graph.
        composantes_connexes (Dict[int, set]): Dictionary mapping component indices to sets of nodes.

    Returns:
        nx.Graph: The largest weakly connected component as a subgraph of the original graph.
   """
   composante_principale = G.subgraph(composantes_connexes[0])
   return composante_principale

def select_mutual_relationships(G: nx.Graph)  -> set:
   """
    Select mutual relationships (edges) in a graph.

    Args:
        G (nx.Graph): The input graph.

    Returns:
        Set[Tuple[int, int]]: A set of tuples representing mutual edges.
   """
   mutual_edges = set()
   for u, v in G.edges():
      if G.has_edge(v, u):
         mutual_edges.add((u, v))
         mutual_edges.add((v, u))
   return mutual_edges

def select_top_nodes_by_metric(G: nx.Graph, metric : str = "degree_centrality", N : int =1000) -> nx.Graph:
    """
    Selects the top N nodes in the graph based on a specified node attribute (metric) and returns the subgraph of these nodes.

    Args:
        G (nx.Graph): The input graph.
        metric (str, optional): The node attribute used to rank and select the top nodes. Default is "degree_centrality".
        N (int, optional): The number of top nodes to select. Default is 1000.

    Returns:
        subgraph (Optional[nx.Graph]): A subgraph containing the top N nodes based on the specified metric. Returns None if the metric is not found.

    """
    if metric in G.nodes[list(G.nodes)[0]].keys():
        metric_selection = select_attribute(G, metric)
        sorted_nodes = sorted(dict(metric_selection).items(), key=lambda x: x[1], reverse=True)
        top_N_nodes = [node for node, degree in sorted_nodes[:N]]
        subgraph = G.subgraph(top_N_nodes)
        return subgraph
    else:
        print(metric, "not found in nodes attribute")
        return None
    
def select_attribute(G : nx.Graph, attribute : str) -> dict:
    """
    Extracts a specified attribute from each node in the graph and returns it as a dictionary.

    Args:
        G (nx.Graph): The input graph.
        attribute (str): The node attribute to extract.

    Returns:
        attribute_dict (Dict): A dictionary where keys are node identifiers and values are the attribute values.
    """
    attribute_dict = {node[0] : node[1][attribute] for node in G.nodes(data=True)}
    return attribute_dict

def select_top_nodes_by_degrees(G: nx.Graph, degree_type : str = "degree", N : int = 1000) -> nx.Graph:
    """
    Selects the top N nodes from a graph based on their degree and returns a subgraph.

    Args:
      G : nx.Graph The input graph, which can be undirected or directed.
      degree_type : str, optional, default="degree". The type of degree to consider for selection. Valid values are "degree", "in degree", and "out degree".
      N : int, optional, default=1000. The number of top nodes to select based on degree.
    Returns:
       nx.Graph : A subgraph containing the top N nodes based on the specified degree type.
    
    Raises:
      ValueError : If an invalid degree_type is provided.
    """
    if degree_type == "degree":
        degree_selection = G.degree()
    elif degree_type == "in degree":
        degree_selection = G.in_degree()
    elif degree_type == "out degree":
        degree_selection = G.out_degree()
    else:
        raise ValueError("Invalid degree_type. Must be one of: 'degree', 'in degree', 'out degree'.")
    
    sorted_nodes_by_degree = sorted(dict(degree_selection).items(), key=lambda x: x[1], reverse=True)
    top_N_nodes = [node for node, degree in sorted_nodes_by_degree[:N]]
    subgraph = G.subgraph(top_N_nodes)

    return subgraph



def scale_size(G, size_attribute, min_node_size = 10, max_node_size = 100):
    """
    Scale the sizes of nodes in a graph based on a specified attribute.

    Args:
        G (nx.Graph): The graph containing nodes with attributes.
        size_attribute (str): The node attribute to scale the sizes by.
        min_node_size (int, optional): The minimum size to scale to. Default is 10.
        max_node_size (int, optional): The maximum size to scale to. Default is 100.

    Returns:
        List[int]: A list of scaled node sizes.
    """
    sizes=[n[1].get(size_attribute,0) for n in G.nodes(data=True)]
    scaled_sizes = scale_list(sizes, min_node_size, max_node_size)
    return scaled_sizes

def transform_dict_of_nodes(dict_of_nodes : dict) -> dict:
   """
   Dictionnary format transformation
   Args:
      dict_of_nodes (dict) : dictionnary returned by networkx
   Returns:
      transformed_dict (dict)

   """
   transformed_dict={}
   for idx, nodes in enumerate(dict_of_nodes):
      for node_id in nodes:
         transformed_dict[node_id] = idx
   return transformed_dict

def layout_forceatlas(G: nx.Graph, dissuade_hubs: bool = True, edge_weight_influence: float = 1.0, scalingRatio: float = 5.0, gravity: float = 0.5, iterations: int = 200) -> dict:
    """
    Computes a ForceAtlas2 layout for a NetworkX graph.

    Args:
      G : nx.Graph
         The input graph.
      dissuade_hubs : bool, optional, default=True
         Whether to apply the outbound attraction distribution, which dissuades hubs.
      edge_weight_influence : float, optional, default=1.0
         The influence of edge weights on the layout.
      scalingRatio : float, optional, default=5.0
         The scaling ratio for the layout.
      gravity : float, optional, default=0.5
         The gravity force applied to the layout.
      iterations : int, optional, default=200
         The number of iterations to run the layout algorithm.

    Returns:
      dict : a dictionary mapping node IDs to their positions in 2D space.
    """
    
    forceatlas2 = ForceAtlas2(
                        # Behavior alternatives
                        outboundAttractionDistribution=dissuade_hubs,  # Dissuade hubs
                        linLogMode=False,  # NOT IMPLEMENTED
                        adjustSizes=False,  # Prevent overlap (NOT IMPLEMENTED)
                        edgeWeightInfluence=edge_weight_influence,

                        # Performance
                        jitterTolerance=1.0,  # Tolerance
                        barnesHutOptimize=True,
                        barnesHutTheta=1.2,
                        multiThreaded=False,  # NOT IMPLEMENTED

                        # Tuning
                        scalingRatio=scalingRatio,
                        strongGravityMode=False,
                        gravity=gravity,

                        # Log
                        verbose=True)

    layout_positions = forceatlas2.forceatlas2_networkx_layout(G, pos=None, iterations=iterations)
    return layout_positions

def distribution(metric_dict : dict, metric_name : str) -> tuple:
   """
    Generate a distribution DataFrame and a boxplot for a given metric.

    Args:
        metric_dict (dict): Dictionary containing metric data, with keys as nodes and values as metric values.
        metric_name (str): The name of the metric to be used as the column name in the DataFrame and plot titles.

    Returns:
        DataFrame containing the distribution of metric values.
        Boxplot figure visualizing the distribution of the metric.
   """
   metric_count = Counter(metric_dict.values())
   df = pd.DataFrame(list(metric_count.items()), columns=[metric_name, "nodes"]).sort_values(by="nodes", ascending=False)
   fig =  boxplot(df, col_y = metric_name, title =f"{metric_name} - Nodes distribution", yaxis_title = metric_name)
   return df, fig


def create_collocations(lst_text : list, word_freq : int, coloc_freq : int, stop_words : list) -> tuple:
    """
    Creates collocations (bigrams) from a list of texts and returns their relative frequencies and a DataFrame of word sizes.
    
    Args:
        lst_text (List[str]): A list of text documents.
        word_freq (int): Minimum document frequency for words to be included.
        coloc_freq (int): Minimum frequency for collocations (bigrams) to be included.
        stop_words (Set[str]): A set of stop words to be excluded from tokenization.
    
    Returns:
        Tuple[List[Tuple[str, str, float]], pd.DataFrame]:
            - A list of tuples where each tuple contains two words and their relative bigram frequency.
            - A DataFrame containing words and their sizes based on their counts in the documents.
    """
    # Tokenize the documents into words using scikit-learn's CountVectorizer
    vectorizer = CountVectorizer(token_pattern=r'[^\s]+', stop_words=stop_words, min_df=word_freq)
    tokenized_documents = vectorizer.fit_transform(lst_text)
    feature_names = vectorizer.get_feature_names_out()
    word_count = tokenized_documents.sum(axis=0)
    df_nodes = pd.DataFrame(zip(list(feature_names), word_count.tolist()[0]), columns=["word","size"])

    # Convert the tokenized documents into lists of words
    tokenized_documents = tokenized_documents.toarray().tolist()
    tokenized_documents = [[feature_names[i] for i, count in enumerate(doc) if count > 0] for doc in tokenized_documents]

    # Create a BigramCollocationFinder from the tokenized documents
    finder = BigramCollocationFinder.from_documents(tokenized_documents)

    # Filter by frequency
    finder.apply_freq_filter(coloc_freq)
    
     # Calculate the total number of bigrams
    total_bigrams = sum(finder.ngram_fd.values())
    
    # Create the list of tuples with desired format and relative frequency
    edges = [(pair[0][0], pair[0][1], pair[1] / total_bigrams) for pair in finder.ngram_fd.items()]
    
    # Sort the tuples by relative frequency
    edges = sorted(edges, key=lambda t: (-t[2], t[0], t[1]))
    
    # List the distinct tokens
    unique_tokens = list(set(pair[0] for pair in edges) | set(pair[1] for pair in edges))
    df_nodes=df_nodes[df_nodes['word'].isin(unique_tokens)]
    
    return edges, df_nodes


def create_maximum_tree(edges : list, df_nodes : pd.DataFrame) -> tuple:
    """
    Creates a network graph from edges and node attributes, then generates its maximum spanning tree.
    
    Args:
        edges (List[Tuple[str, str, float]]): A list of tuples where each tuple contains two nodes and the weight of the edge between them.
        df_nodes (pd.DataFrame): A DataFrame containing node attributes, where 'word' is the node identifier.
    
    Returns:
        Tuple[nx.Graph, nx.Graph]:
            - The original network graph with node attributes.
            - The maximum spanning tree of the network graph.
    """
    attributs=df_nodes.set_index('word')
    dictionnaire=attributs.to_dict('index')

    network=nx.Graph()
    network.add_weighted_edges_from(edges)
    nx.set_node_attributes(network, dictionnaire)
    
    tree = nx.maximum_spanning_tree(network)

    return network, tree

def words_partitions(network : nx.Graph, resolution : float = 1.0) -> None:
    """
    Partitions the network using the Louvain method and calculates the modularity of the partition.
    
    Args:
        network (nx.Graph): The network graph to partition.
        resolution (float): The resolution parameter for the Louvain method. Higher values lead to smaller communities.
    
    Returns:
        None
    """
    try:
        partition = community_louvain.best_partition(network, resolution=resolution)
        modularity = community_louvain.modularity(partition, network)
        nx.set_node_attributes(network, partition, "modularity")
        print("Partitioning and modularity calculation successful")
    except Exception as e:
        pass
        print(e, "Partitioning and modularity calculation failed")
        # Set a default value for partition and modularity
        partition = {node: 0 for node in network.nodes()}
        modularity = 0
        nx.set_node_attributes(network, partition, "modularity")

    
def compute_metrics(network : nx.Graph) -> None :
    """
    Computes and sets centrality metrics for the nodes in the network graph.
    
    Args:
        network (nx.Graph): The network graph on which to compute centrality.
    
    Returns:
        None
    """
    try:
        degree_cent = nx.degree_centrality(network)
        nx.set_node_attributes(network, degree_cent, "degree_centrality")
        print("Calcul de la centralité de degrés effectué")
    except Exception as e:
        pass
        print(e, "Calcul de la centralité de degrés impossible")
        # Set a default value for degree centrality
        degree_cent = {node: 0 for node in network.nodes()}
        nx.set_node_attributes(network, degree_cent, "degree_centrality")

    ### CALCUL DE LA CENTRALITE DE VECTEUR PROPRE
    try:
        centrality = nx.eigenvector_centrality(network)
        nx.set_node_attributes(network, centrality, "eigenvector_centrality")
        print("Calcul de la centralité de vecteur propre effectué")
    except Exception as e:
        pass
        print(e, "Calcul de la centralité de vecteur propre impossible")
        # Set a default value for centrality
        centrality = {node: 0 for node in network.nodes()}
        nx.set_node_attributes(network, centrality, "eigenvector_centrality")
        
    try:
        betweenness_cent = nx.betweenness_centrality(network, k=None, normalized=True, weight='weight', endpoints=False, seed=None)
        nx.set_node_attributes(network, betweenness_cent, "betweenness_centrality")
        print("Calcul de l'intermédiarité effectué")
    except Exception as e:
        pass
        print(e, "Calcul de l'intermédiarité impossible")
        # Set a default value for betweenness centrality
        betweenness_cent = {node: 0 for node in network.nodes()}
        nx.set_node_attributes(network, betweenness_cent, "betweenness_centrality")

def prepare_nodes(T : nx.Graph, layout_positions : dict, colormap : str, min_node_size : int = 8, max_node_size : int = 40) -> None:
    """
    Prepares and sets node attributes for a graph based on various centrality measures and colors them using a colormap.
    
    Args:
        T (nx.Graph): The input graph.
        layout_positions (Dict[str, Tuple[float, float]]): A dictionary of node positions for layout.
        colormap (Colormap): A colormap for generating node colors.
        min_node_size (int): Minimum node size for scaling. Default is 8.
        max_node_size (int): Maximum node size for scaling. Default is 40.
    
    Returns:
        None
    """

    # on génère une palette de couleur à partir de colormap
    modularity_palette = generate_color_palette_with_colormap(set(nx.get_node_attributes(T,"modularity").values()), colormap=colormap)
    dc_palette = generate_color_palette_with_colormap(set(nx.get_node_attributes(T,"degree_centrality").values()), colormap=colormap)
    ec_palette = generate_color_palette_with_colormap(set(nx.get_node_attributes(T,"eigenvector_centrality").values()), colormap=colormap)
    bc_palette = generate_color_palette_with_colormap(set(nx.get_node_attributes(T,"betweenness_centrality").values()), colormap=colormap)

    # on scale nos métriques
    sizes = []
    degree_centralities = []
    eigenvector_centralities = []
    betweenness_centralities = []
    for n in T.nodes(data=True):
        sizes.append(n[1].get('size',0))
        degree_centralities.append(n[1].get('degree_centrality',0))
        eigenvector_centralities.append(n[1].get('eigenvector_centrality',0))
        betweenness_centralities.append(n[1].get('betweenness_centrality',0))

    scaled_sizes = scale_list(sizes, min_node_size, max_node_size)
    scaled_dc = scale_list(degree_centralities, min_node_size, max_node_size)
    scaled_ec = scale_list(eigenvector_centralities, min_node_size, max_node_size)
    scaled_bc = scale_list(betweenness_centralities, min_node_size, max_node_size)
    # sizes = [n[1]['size'] for n in T.nodes(data=True)]
    
    # on ajoute les attributs à nos nodes
    node_attributes = {n[0]: {'scaled_size': math.ceil(scaled_sizes[i]), 
                              'modularity_color': modularity_palette.get(n[1]["modularity"], generate_random_hexadecimal_color()),
                              'scaled_degree_centrality' : scaled_dc[i],
                              'degree_centrality_color': dc_palette.get(n[1]["degree_centrality"], generate_random_hexadecimal_color()),
                              'scaled_eigenvector_centrality' : scaled_ec[i],
                              'eigenvector_centrality_color': ec_palette.get(n[1]["eigenvector_centrality"], generate_random_hexadecimal_color()),
                              'scaled_betweenness_centrality' : scaled_bc[i],
                             'betweenness_centrality_color': bc_palette.get(n[1]["betweenness_centrality"], generate_random_hexadecimal_color()),
                              } for i, n in enumerate(T.nodes(data=True))}

    nx.set_node_attributes(T, node_attributes)

    for n, p in layout_positions.items():
        T.nodes[n]['pos'] = p

def prepare_edges(T : nx.Graph, min_edge_size : int =1, max_edge_size : int =5) -> None:
    """
    Prepares and sets edge attributes for a graph by scaling edge weights.
    
    Args:
        T (nx.Graph): The input graph.
        min_edge_size (int): Minimum edge size for scaling. Default is 1.
        max_edge_size (int): Maximum edge size for scaling. Default is 5.
    
    Returns:
        None
    """
    w = [e[2]['weight'] for e in T.edges(data=True)]
    scaled_w = scale_list(w, min_edge_size, max_edge_size)
    edges_attributes_dict = {(e[0], e[1]): {'scaled_weight': scaled_w[i]} for i, e in enumerate(T.edges(data=True))}
    nx.set_edge_attributes(T, edges_attributes_dict)
    

def layout_graphviz(network : nx.Graph, layout : str = "fdp", args : str ="") -> dict:
    """
    Generates node positions for a graph using Graphviz layout algorithms.
    
    Args:
        network (nx.Graph): The input graph.
        layout (str): The Graphviz layout algorithm to use (e.g., "dot", "fdp", "sfdp"). Default is "fdp".
        args (str): Additional arguments to pass to the Graphviz layout algorithm. Default is an empty string.
    
    Returns:
        Dict[str, Tuple[float, float]]: A dictionary of node positions.
    """
    layout_positions = nx.nx_agraph.graphviz_layout(network, prog=layout, args=args)
    return layout_positions

def layout_spring(network : nx.Graph, k : float = 0.08, scale : int = 2, iterations : int = 200, weight : str ="weight") -> dict:
    """
    Generates node positions for a graph using the spring layout algorithm.
    
    Args:
        network (nx.Graph): The input graph.
        k (float): Optimal distance between nodes. Default is 0.08.
        scale (float): Scale factor for the layout. Default is 2.
        iterations (int): Number of iterations for the spring layout algorithm. Default is 200.
        weight (str): Edge attribute to use as weight. Default is "weight".
    
    Returns:
        Dict[str, Tuple[float, float]]: A dictionary of node positions.
    """
    layout_positions = nx.spring_layout(network, k=k,  scale=scale, iterations=iterations, weight=weight)
    return layout_positions