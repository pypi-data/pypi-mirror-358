from plotly.subplots import make_subplots
import plotly.graph_objects as go
import textwrap
import numpy as np
from scipy import interpolate
from scipy.spatial import ConvexHull
import random
from sklearn.metrics.pairwise import cosine_similarity
import plotly.express as px
import chart_studio.tools as tls
import chart_studio.plotly as py
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import math
import pandas as pd
from opsci_toolbox.helpers.nlp import sample_most_engaging_posts, create_frequency_table
from matplotlib.colors import to_hex
import networkx as nx

def general_kwargs():
    """
    Returns a dictionary containing default parameters for plotting functions.

    Returns:
        dict: A dictionary with default plotting parameters.
    """
    params = {
        "mode": "markers",  # mode
        "textposition": "bottom center",  # markers position
        "orientation" : "h",
        "bargap":0.3,

        # HOVER
        "col_hover": [],  # cols to display on hover
        "trace_name" : "verbatims",
        "xaxis_tickvals" : [-1, -0.75, -0.50, -0.25, 0, 0.25, 0.50, 0.75, 1],
        "yaxis_tickvals" : [-1, -0.75, -0.50, -0.25, 0, 0.25, 0.50, 0.75, 1],
        "xaxis_ticktext" : ['100', '75', '50', '25', '0', '25', '50', '75', '100'],
        "yaxis_ticktext" : ['100', '75', '50', '25', '0', '25', '50', '75', '100'],


        # PIE CHARTS
        "hole" : .4,
    
        # MARKERS
        "marker_color": "#bd66ff",  # markers color
        "marker_opacity": 0.8,  # marker opacity
        "marker_symbol": "circle",  # symbol to use. See : https://plotly.com/python/marker-style/#custom-marker-symbols
        "marker_size": 4,  # dots size
        "marker_sizemin": 1,  # minimum size of dot
        "marker_sizemode": "area",  # possible values are "diameter" or "area"
        "marker_line_width": 0.5,  # line width around dot
        "marker_line_color": "white",  # line color around dot
        "marker_maxdisplayed": 0,  # max number of dots to display (0 = infinite)
        "marker_colorscale": "Viridis",
        # GENERAL LAYOUT
        "font_size": 14,  # font size (ex : title)
        "font_family": "Inria Sans",  # font family
        "title_text": "Scatter Plot",  # title of the main plot
        "showlegend": True,  # display legend
        "showscale": True,  # display scale
        "width": 1000,  # plot width
        "height": 1000,  # plot height
        "plot_bgcolor": "#FFFFFF",  # plot_bgcolor sets the color of plotting area in-between x and y axes.
        "paper_bgcolor": "#FFFFFF",  # paper_bgcolor sets the color of paper where the graph is drawn (= outside of axes but inside of parent div)
        "template": "plotly",  # template. Possible values are "plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none"
        # X AXIS
        "xaxis_title": "X-axis",  # xaxis label
        "xaxis_title_font_size": 14, #font size of the label
        "xaxis_tickangle": 0,  # xaxis text angle
        "xaxis_tickfont_size": 12,  # xaxis ticks font size
        "xaxis_range": None,  # xaxis range
        "xaxis_showline": False,  # display the xaxis line
        "xaxis_showgrid": False,  # display the xaxis grid
        "xaxis_zeroline": False,  # display the xaxis zeroline
        "xaxis_gridwidth": 0.5,  # width of the grid
        "xaxis_gridcolor": "#D7DBDD",  # color of the grid
        "xaxis_linewidth": 2,  # width of the line
        "xaxis_linecolor": "#D7DBDD",  # color of the line
        "xaxis_mirror": False,  # mirror the axis
        # Y AXIS
        "yaxis_title": "Y-axis",
        "yaxis_title_font_size": 14, #font size of the label
        "yaxis_tickfont_size": 12,
        "yaxis_range": None,
        "yaxis_tickangle": 0,
        "yaxis_showline": False,
        "yaxis_showgrid": False,
        "yaxis_gridwidth": 0.5,
        "yaxis_gridcolor": "#D7DBDD",
        "yaxis_zeroline": False,
        "yaxis_linewidth": 2,
        "yaxis_linecolor": "#D7DBDD",
        "yaxis_mirror": False,
        # Z AXIS
        "zaxis_title": "Z-axis",
        "zaxis_title_font_size": 14, #font size of the label
        "zaxis_tickfont_size": 12,
        "zaxis_range": None,
        "zaxis_tickangle": 0,
        "zaxis_showline": False,
        "zaxis_showgrid": False,
        "zaxis_gridwidth": 0.5,
        "zaxis_gridcolor": "#D7DBDD",
        "zaxis_zeroline": False,
        "zaxis_linewidth": 2,
        "zaxis_linecolor": "#D7DBDD",
        "zaxis_mirror": False,
        # SUBPLOTS
        "n_rows": 3,
        "n_cols": 3,
        "vertical_spacing": 0.1,
        "horizontal_spacing": 0.1,
        "uniformtext_minsize": 8,
        "uniformtext_mode": "hide",
        "shared_xaxes":False,
        "shared_yaxes":False
    }
    return params

def pyramide(df:pd.DataFrame, col_x: str, col_y: str, col_cat:str, color_palette:dict, trace_names : list = ["users", "verbatims"], lightness_factor : float = 1.4, **kwargs) -> go.Figure:
    """
    Generates a pyramid chart using the provided data.

    Args:
        df (pd.DataFrame): The data frame containing the data.
        col_x (str): The name of the column to be used for the x-axis values.
        col_y (str): The name of the column to be used for the y-axis values.
        col_cat (str): The name of the column to be used for categories.
        color_palette (dict): A dictionary mapping categories to colors.
        trace_names (list): A list containing names for the traces (default is ["users", "verbatims"]).
        lightness_factor (float): A factor to adjust the lightness of the colors (default is 1.4).
        **kwargs: Additional keyword arguments to customize the chart.

    Returns:
        plotly.graph_objects.Figure: The pyramid chart figure.
    """
    params = general_kwargs()
    params.update(kwargs)

    # reduced_color_palette = {k: adjust_lightness(v, factor=lightness_factor) for k, v in color_users_categories.items()}
    col_hover = params["col_hover"]
    fig = go.Figure()

    for i, cat in enumerate(df[col_cat].unique()):
        current_df = df[df[col_cat] == cat]

        hovertemplate = ""
        for c in col_hover:
            hovertemplate += (
                "<br><b>" + str(c) + "</b>:" + current_df[c].apply(format_input).astype(str)
        )

        if color_palette:
            color = color_palette.get(cat, generate_random_hexadecimal_color())
            reduced_color = adjust_lightness(color, factor=lightness_factor)
        else : 
            color = generate_random_hexadecimal_color()
            reduced_color = adjust_lightness(color, factor=lightness_factor)

        if i==0:
            showlegend=True
        else :
            showlegend=False

        # Add users bar (mirrored to create pyramid effect)
        fig.add_trace(go.Bar(
            y=current_df[col_cat],
            x=-current_df[col_x],
            name=trace_names[0],
            text = current_df[col_x].apply(format_number) +'<br>'+trace_names[0],
            textposition=params["textposition"],
            orientation=params['orientation'],
            marker_color = color,
            hovertemplate=hovertemplate+"<extra></extra>",
            legendgroup="Users",
            showlegend = showlegend
        ))

        # Add tweets bar
        fig.add_trace(go.Bar(
            y=current_df[col_cat],
            x=current_df[col_y],
            text = current_df[col_y].apply(format_number)+'<br>'+trace_names[1],
            textposition=params["textposition"],
            name=trace_names[1],
            orientation=params['orientation'],
            marker_color = reduced_color,
            hovertemplate=hovertemplate+"<extra></extra>",
            legendgroup="Tweets",
            showlegend = showlegend
        ))

    # Update layout
    fig.update_layout(
        title_text=params['title_text'],
        barmode='overlay',
        bargap=params["bargap"],
        width=params["width"],
        height=params["height"],
        font_family=params["font_family"],
        font_size=params["font_size"],
        template=params["template"],
        plot_bgcolor=params["plot_bgcolor"],  # background color (plot)
        paper_bgcolor=params["paper_bgcolor"],  # background color (around plot)
        showlegend=params["showlegend"],
        uniformtext_minsize=params["uniformtext_minsize"],
        uniformtext_mode=params["uniformtext_mode"],
    )
    fig.update_yaxes(
        title=params["yaxis_title"],
        title_font_size=params["yaxis_title_font_size"],
        tickangle=params["yaxis_tickangle"],
        tickfont_size=params["yaxis_tickfont_size"],
        range=params["yaxis_range"],
        showgrid=params["yaxis_showgrid"],
        showline=params["yaxis_showline"],
        zeroline=params["yaxis_zeroline"],
        gridwidth=params["yaxis_gridwidth"],
        gridcolor=params["yaxis_gridcolor"],
        linewidth=params["yaxis_linewidth"],
        linecolor=params["yaxis_linecolor"],
        mirror=params["yaxis_mirror"],
    )

    fig.update_xaxes(
        title=params["xaxis_title"],
        title_font_size=params["xaxis_title_font_size"],
        tickangle=params["xaxis_tickangle"],
        tickfont_size=params["xaxis_tickfont_size"],
        range=params["xaxis_range"],
        tickvals=params['xaxis_tickvals'],
        ticktext=params["xaxis_ticktext"],
        showgrid=params["xaxis_showgrid"],
        showline=params["xaxis_showline"],
        zeroline=params["xaxis_zeroline"],
        gridwidth=params["xaxis_gridwidth"],
        gridcolor=params["xaxis_gridcolor"],
        linewidth=params["xaxis_linewidth"],
        linecolor=params["xaxis_linecolor"],
        mirror=params["xaxis_mirror"],
    )

    return fig

def subplots_pyramide(df:pd.DataFrame, col_x: str, col_y: str, col_cat:str, col_sub_cat, color_palette:dict, trace_names : list = ["users", "verbatims"], lightness_factor : float = 1.4, **kwargs) -> go.Figure:
    """
    Generates a pyramid chart using the provided data.

    Args:
        df (pd.DataFrame): The data frame containing the data.
        col_x (str): The name of the column to be used for the x-axis values.
        col_y (str): The name of the column to be used for the y-axis values.
        col_cat (str): The name of the column to be used for categories (i.e : representing each subplot)
        col_sub_cat (str) : The name of the column to be used for sub categories  (i.e : representing y axis)
        color_palette (dict): A dictionary mapping categories to colors.
        trace_names (list): A list containing names for the traces (default is ["users", "verbatims"]).
        lightness_factor (float): A factor to adjust the lightness of the colors (default is 1.4).
        **kwargs: Additional keyword arguments to customize the chart.

    Returns:
        plotly.graph_objects.Figure: The pyramid chart figure.
    """
    params = general_kwargs()
    params.update(kwargs)

    # reduced_color_palette = {k: adjust_lightness(v, factor=lightness_factor) for k, v in color_users_categories.items()}
    col_hover = params["col_hover"]

    n_cols = params["n_cols"]
    col_hover=params["col_hover"]
    showlegend=params["showlegend"]
    categories = df[col_cat].unique()

    # user define a number of columns, we compute the number of rows required
    n_rows = math.ceil(len(categories) / n_cols)

    fig = make_subplots(
        rows=n_rows,  # number of rows
        cols=n_cols,  # number of columns
        vertical_spacing=params["vertical_spacing"],  # space between subplots
        horizontal_spacing=params["horizontal_spacing"],
        subplot_titles=categories,
        shared_xaxes=params["shared_xaxes"],
        shared_yaxes=params["shared_yaxes"]
    )

    row_id = 0
    col_id = 0

    for i, cat in enumerate(categories):
        df_tmp = df[df[col_cat] == cat]

        # define row and column position
        col_id += 1
        if i % n_cols == 0:
            row_id += 1
        if col_id > n_cols:
            col_id = 1

        for i, sub_cat in enumerate(df_tmp[col_sub_cat].unique()):
            current_df = df_tmp[df_tmp[col_sub_cat] == sub_cat]

            hovertemplate = ""
            for c in col_hover:
                hovertemplate += (
                    "<br><b>" + str(c) + "</b>:" + current_df[c].apply(format_input).astype(str)
            )

            if color_palette:
                color = color_palette.get(sub_cat, generate_random_hexadecimal_color())
                reduced_color = adjust_lightness(color, factor=lightness_factor)
            else : 
                color = generate_random_hexadecimal_color()
                reduced_color = adjust_lightness(color, factor=lightness_factor)

            if (showlegend) & i > 0:
                showlegend=False
       
            # Add users bar (mirrored to create pyramid effect)
            fig.add_trace(go.Bar(
                y=current_df[col_sub_cat],
                x=-current_df[col_x],
                name=trace_names[0],
                text = current_df[col_x].apply(format_number) +'<br>'+trace_names[0],
                textposition=params["textposition"],
                orientation=params['orientation'],
                marker_color = color,
                hovertemplate=hovertemplate+"<extra></extra>",
                legendgroup="Users",
                showlegend = showlegend
            ),
            row=row_id,
            col=col_id,
            )

            # Add tweets bar
            fig.add_trace(go.Bar(
                y=current_df[col_sub_cat],
                x=current_df[col_y],
                text = current_df[col_y].apply(format_number)+'<br>'+trace_names[1],
                textposition=params["textposition"],
                name=trace_names[1],
                orientation=params['orientation'],
                marker_color = reduced_color,
                hovertemplate=hovertemplate+"<extra></extra>",
                legendgroup="Tweets",
                showlegend = showlegend
            ),
            row=row_id,
            col=col_id,
            )

    for row_id in range(1, n_rows+1):
        for col_id in range(1, n_cols+1):
            fig.update_yaxes(title=params["yaxis_title"], row=row_id, col=1)
            fig.update_xaxes(title=params["xaxis_title"], row=row_id, col=col_id)

    # Update layout
    fig.update_layout(
        title_text=params['title_text'],
        barmode='overlay',
        bargap=params["bargap"],
        width=params["width"] * n_cols,
        height=params["height"] * n_rows,
        font_family=params["font_family"],
        font_size=params["font_size"],
        template=params["template"],
        plot_bgcolor=params["plot_bgcolor"],  # background color (plot)
        paper_bgcolor=params["paper_bgcolor"],  # background color (around plot)
        showlegend=params["showlegend"],
        uniformtext_minsize=params["uniformtext_minsize"],
        uniformtext_mode=params["uniformtext_mode"],
    )
    fig.update_yaxes(
        title_font_size=params["yaxis_title_font_size"],
        tickangle=params["yaxis_tickangle"],
        tickfont_size=params["yaxis_tickfont_size"],
        range=params["yaxis_range"],
        showgrid=params["yaxis_showgrid"],
        showline=params["yaxis_showline"],
        zeroline=params["yaxis_zeroline"],
        gridwidth=params["yaxis_gridwidth"],
        gridcolor=params["yaxis_gridcolor"],
        linewidth=params["yaxis_linewidth"],
        linecolor=params["yaxis_linecolor"],
        mirror=params["yaxis_mirror"],
    )

    fig.update_xaxes(
        title_font_size=params["xaxis_title_font_size"],
        tickangle=params["xaxis_tickangle"],
        tickfont_size=params["xaxis_tickfont_size"],
        range=params["xaxis_range"],
        tickvals=params['xaxis_tickvals'],
        ticktext=params["xaxis_ticktext"],
        showgrid=params["xaxis_showgrid"],
        showline=params["xaxis_showline"],
        zeroline=params["xaxis_zeroline"],
        gridwidth=params["xaxis_gridwidth"],
        gridcolor=params["xaxis_gridcolor"],
        linewidth=params["xaxis_linewidth"],
        linecolor=params["xaxis_linecolor"],
        mirror=params["xaxis_mirror"],
    )

    return fig


def bar(df: pd.DataFrame, 
        col_x: str, 
        col_y: str, 
       **kwargs) -> go.Figure:
    """
    Creates a Plotly vertical bar chart.

    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        col_x (str): The name of the column containing the x-axis values.
        col_y (str): The name of the column containing the y-axis values.
        **kwargs: Additional keyword arguments to update default plotting parameters.

    Returns:
        fig (go.Figure): The Plotly Figure object representing the vertical bar chart.
    """

    params = general_kwargs()
    params.update(kwargs)
    col_hover = params["col_hover"]

    hovertemplate = str(col_x) +" : "+df[col_x].astype(str)+"<br>"+str(col_y)+" : "+df[col_y].astype(str)
    for c in col_hover:
        hovertemplate += (
            "<br><b>" + str(c) + "</b>:" + df[c].astype(str).apply(wrap_text)
        )

    fig = go.Figure(
        go.Bar(
                x=df[col_x], 
                y=df[col_y],
                orientation=params["orientation"],
                name=params["yaxis_title"], 
                marker_color=params["marker_color"],
                hovertemplate = hovertemplate+'<extra></extra>',
                
        )
    )

    fig.update_layout(
            title_text=params["title_text"],
            width=params["width"],
            height=params["height"],
            font_family=params["font_family"],
            font_size=params["font_size"],
            template=params["template"],
            plot_bgcolor=params["plot_bgcolor"],  # background color (plot)
            paper_bgcolor=params["paper_bgcolor"],  # background color (around plot)
            showlegend=params["showlegend"],
            uniformtext_minsize=params["uniformtext_minsize"],
            uniformtext_mode=params["uniformtext_mode"],
            bargap=params["bargap"]
        )

    fig.update_yaxes(
        title=params["yaxis_title"],
        title_font_size=params["yaxis_title_font_size"],
        tickangle=params["yaxis_tickangle"],
        tickfont_size=params["yaxis_tickfont_size"],
        range=params["yaxis_range"],
        showgrid=params["yaxis_showgrid"],
        showline=params["yaxis_showline"],
        zeroline=params["yaxis_zeroline"],
        gridwidth=params["yaxis_gridwidth"],
        gridcolor=params["yaxis_gridcolor"],
        linewidth=params["yaxis_linewidth"],
        linecolor=params["yaxis_linecolor"],
        mirror=params["yaxis_mirror"],
    )

    fig.update_xaxes(
        title=params["xaxis_title"],
        title_font_size=params["xaxis_title_font_size"],
        tickangle=params["xaxis_tickangle"],
        tickfont_size=params["xaxis_tickfont_size"],
        range=params["xaxis_range"],
        showgrid=params["xaxis_showgrid"],
        showline=params["xaxis_showline"],
        zeroline=params["xaxis_zeroline"],
        gridwidth=params["xaxis_gridwidth"],
        gridcolor=params["xaxis_gridcolor"],
        linewidth=params["xaxis_linewidth"],
        linecolor=params["xaxis_linecolor"],
        mirror=params["xaxis_mirror"],
    )
    return fig

def trends_subplot(
    df: pd.DataFrame,
    col_date: str,
    col_cat: str,
    col_metric: str,
    dict_color: dict,
    **kwargs
) -> go.Figure:
    """
        Creates a subplot figure showing trends for different categories over time.

    Args:
        df (pd.DataFrame): The input DataFrame containing the data.
        col_date (str): The name of the column containing date values.
        col_cat (str): The name of the column containing category values.
        col_metric (str): The name of the column containing metric values.
        dict_color (dict): A dictionary mapping categories to colors.
        **kwargs: Additional keyword arguments to update default plotting parameters.

    Returns:
        plotly.graph_objs._figure.Figure: The generated subplot figure.
    """

    params = general_kwargs()
    params.update(kwargs)

    n_cols = params["n_cols"]
    col_hover=params["col_hover"]

    categories = df[col_cat].unique()

    # user define a number of columns, we compute the number of rows required
    n_rows = math.ceil(len(categories) / n_cols)

    fig = make_subplots(
        rows=n_rows,  # number of rows
        cols=n_cols,  # number of columns
        vertical_spacing=params["vertical_spacing"],  # space between subplots
        horizontal_spacing=params["horizontal_spacing"],
        subplot_titles=categories,
        shared_xaxes=params["shared_xaxes"],
        shared_yaxes=params["shared_yaxes"]
    )

    row_id = 0
    col_id = 0
    for i, cat in enumerate(categories):
        current_df = df[df[col_cat] == cat]

        if dict_color:
            color = dict_color[cat]
        else:
            color = generate_random_hexadecimal_color()

        # define row and column position
        col_id += 1
        if i % n_cols == 0:
            row_id += 1
        if col_id > n_cols:
            col_id = 1

        hovertemplate = (
            "<b>Categorie : </b>"
            + str(cat)
            + "<br><b>Date : </b>"
            + current_df[col_date].astype(str)
            + "<br><b>"
            + col_metric
            + " : "
            + current_df[col_metric].astype(str)
        )

        for c in col_hover:
            hovertemplate += (
                "<br><b>"
                + str(c)
                + "</b>:"
                + current_df[c].astype(str).apply(wrap_text)
            )

        fig.add_trace(
            go.Scatter(
                x=current_df[col_date],
                y=current_df[col_metric],
                name=cat,
                mode=params["mode"],
                line_color=color,
                line_width=params["marker_line_width"],
                hovertemplate=hovertemplate + "<extra></extra>",
                showlegend=params["showlegend"],
                fill="tozeroy",
            ),
            row=row_id,
            col=col_id,
        )
    for row_id in range(1, n_rows+1):
        for col_id in range(1, n_cols+1):
            fig.update_yaxes(title=params["yaxis_title"], row=row_id, col=1)
            fig.update_xaxes(title=params["xaxis_title"], row=row_id, col=col_id)

    fig.update_layout(
        title_text=params["title_text"],
        width=params["width"] * n_cols,
        height=params["height"] * n_rows,
        font_family=params["font_family"],
        font_size=params["font_size"],
        template=params["template"],
        plot_bgcolor=params["plot_bgcolor"],  # background color (plot)
        paper_bgcolor=params["paper_bgcolor"],  # background color (around plot)
    )

    fig.update_yaxes(
        title_font_size=params["yaxis_title_font_size"],
        tickangle=params["yaxis_tickangle"],
        tickfont_size=params["yaxis_tickfont_size"],
        range=params["yaxis_range"],
        showgrid=params["yaxis_showgrid"],
        showline=params["yaxis_showline"],
        zeroline=params["yaxis_zeroline"],
        gridwidth=params["yaxis_gridwidth"],
        gridcolor=params["yaxis_gridcolor"],
        linewidth=params["yaxis_linewidth"],
        linecolor=params["yaxis_linecolor"],
        mirror=params["yaxis_mirror"],
    )

    # if normalize_yaxis:
    #     fig.update_yaxes(range=[0, df[col_metric].max()])

    fig.update_xaxes(
        # title=params["xaxis_title"],
        title_font_size=params["xaxis_title_font_size"],
        tickangle=params["xaxis_tickangle"],
        tickfont_size=params["xaxis_tickfont_size"],
        range=params["xaxis_range"],
        showgrid=params["xaxis_showgrid"],
        showline=params["xaxis_showline"],
        zeroline=params["xaxis_zeroline"],
        gridwidth=params["xaxis_gridwidth"],
        gridcolor=params["xaxis_gridcolor"],
        linewidth=params["xaxis_linewidth"],
        linecolor=params["xaxis_linecolor"],
        mirror=params["xaxis_mirror"],
    )

    return fig



def create_scatter_plot(
    df: pd.DataFrame,
    col_x: str,
    col_y: str,
    col_category: str,
    color_palette: dict,
    col_color: str,
    col_size: str,
    col_text: str,
    **kwargs
) -> go.Figure:
    """
    Create a scatter plot.

    Args:
        df (pd.DataFrame): DataFrame containing all data.
        col_x (str): Name of the column containing X values.
        col_y (str): Name of the column containing Y values.
        col_category (str): Name of the column for colorization.
        color_palette (dict): A dictionary mapping category with color value.
        col_color (str): Name of the column for color. Only used for continuous scale.
        col_size (str): Name of the column for dot sizes.
        col_text (str): Name of the column containing text for legend on hover.
        **kwargs: Additional keyword arguments to update default plotting parameters.

    Returns:
        go.Figure: Plotly scatter plot figure.
    """
    params = general_kwargs()
    params.update(kwargs)
    marker_color = params["marker_color"]
    marker_line_color = params["marker_line_color"]
    marker_size = params["marker_size"]
    col_hover = params["col_hover"]
    xaxis_range = params["xaxis_range"]
    yaxis_range = params["yaxis_range"]

    fig = go.Figure()
    if marker_line_color is None:
        marker_line_color = marker_color

    # col_category is used to colorize dots
    if col_category is not None:
        for i, category in enumerate(df[col_category].unique()):

            if color_palette:
                marker_color = color_palette.get(category, generate_random_hexadecimal_color())  # Default to black if category not found
            else:
                marker_color = generate_random_hexadecimal_color()

            # hovertemplate generation
            # hovertemplate = (
            #     "<b>"
            #     + col_x
            #     + "</b>:"
            #     + df[df[col_category] == category][col_x].astype(str)
            #     + "<br><b>"
            #     + col_y
            #     + "</b>:"
            #     + df[df[col_category] == category][col_y].astype(str)
            #     + "<br><b>"
            #     + col_category
            #     + "</b>:"
            #     + str(category)
            # )
            hovertemplate = ""
            if col_size is None:
                size = marker_size
            else:
                size = df[df[col_category] == category][col_size]
            #     hovertemplate += "<br><b>" + col_size + "</b>:" + size.astype(str)

            if len(col_hover) > 0:
                for c in col_hover:
                    hovertemplate += (
                        "<br><b>"
                        + str(c)
                        + "</b> : "
                        + df[df[col_category] == category][c]
                        .apply(format_input)
                        .astype(str)
                    )

            fig.add_trace(
                go.Scatter(
                    x=df[df[col_category] == category][col_x],
                    y=df[df[col_category] == category][col_y],
                    mode=params["mode"],
                    text=df[df[col_category] == category][col_text],
                    textposition=params["textposition"],
                    marker=dict(
                        color=marker_color,  # dots color
                        size=size,  # dots size
                        opacity=params["marker_opacity"],  # dots opacity
                        line_color=params["marker_line_color"],  # line color around dot
                        line_width=params["marker_line_width"],  # line width around dot
                        sizemode=params["marker_sizemode"],  # size mode
                        sizemin=params["marker_sizemin"],  # minimum size of dot
                        maxdisplayed=params["marker_maxdisplayed"],  # max number of dots to display (0 = infinite)
                        symbol=params["marker_symbol"],  # type of dot
                    ),
                    name=category,  # trace name
                    hovertemplate=hovertemplate + "<extra></extra>",
                )
            )
    # if there is no category for color, we create a simpler plot
    else:
        hovertemplate = (
            "<b>"
            + col_x
            + "</b>:"
            + df[col_x].astype(str)
            + "<br><b>"
            + col_y
            + "</b>:"
            + df[col_y].astype(str)
        )
        if col_size is None:
            size = marker_size

        else:
            size = df[col_size]
            hovertemplate += "<br><b>" + col_size + "</b>:" + size.astype(str)

        if col_color is not None:
            hovertemplate += "<br><b>" + col_color + "</b>:" + df[col_color].astype(str)
            marker_color = df[col_color]
        else:
            if marker_color is None:
                marker_color = generate_random_hexadecimal_color()
        if len(col_hover) > 0:
            for c in col_hover:
                hovertemplate += (
                    "<br><b>" + str(c) + "</b>:" + df[c].astype(str).apply(wrap_text)
                )
        fig = go.Figure(
            go.Scatter(
                x=df[col_x],
                y=df[col_y],
                mode=params["mode"],
                text=df[col_text],
                textposition=params["textposition"],
                marker=dict(
                    color=marker_color,  # dots color
                    size=size,  # dots size
                    opacity=params["marker_opacity"],  # dots opacity
                    line_color=params["marker_line_color"],  # line color around dot
                    line_width=params["marker_line_width"],  # line width arount dot
                    sizemode=params["marker_sizemode"],  # Scale marker sizes
                    sizemin=params["marker_sizemin"],  # minimum size of dot
                    maxdisplayed=params["marker_maxdisplayed"],  # max number of dots to display (0 = infinite)
                    symbol=params["marker_symbol"],  # type of dot
                    colorscale=params["marker_colorscale"],
                    showscale=params["showscale"],
                ),
                name="",
                hovertemplate=hovertemplate + "<extra></extra>",
            )
        )

    # we calculate X and Y axis ranges.
    if yaxis_range is None:
        yaxis_range = [df[col_y].min() - 0.1, df[col_y].max() + 0.1]
    if yaxis_range == "auto":
        yaxis_range = None

    if xaxis_range is None:
        xaxis_range = [df[col_x].min() - 0.1, df[col_x].max() + 0.1]
    if xaxis_range == "auto":
        xaxis_range = None

    # Update layout
    fig.update_layout(
        title_text=params["title_text"],  # graph title
        width=params["width"],  # plot size
        height=params["height"],  # plot size
        template=params["template"],
        plot_bgcolor=params["plot_bgcolor"],  # background color (plot)
        paper_bgcolor=params["paper_bgcolor"],  # background color (around plot)
        font_family=params["font_family"],  # font
        font_size=params["font_size"],
    )
    fig.update_xaxes(
        title=params["xaxis_title"],
        title_font_size=params["xaxis_title_font_size"],
        tickangle=params["xaxis_tickangle"],
        tickfont_size=params["xaxis_tickfont_size"],
        range=xaxis_range,
        showgrid=params["xaxis_showgrid"],
        showline=params["xaxis_showline"],
        zeroline=params["xaxis_zeroline"],
        gridwidth=params["xaxis_gridwidth"],
        gridcolor=params["xaxis_gridcolor"],
        linewidth=params["xaxis_linewidth"],
        linecolor=params["xaxis_linecolor"],
        mirror=params["xaxis_mirror"],
        layer="below traces")  # Ensure x-axis grid is below the data
    
    fig.update_yaxes(
        title=params["yaxis_title"],
        title_font_size=params["yaxis_title_font_size"],
        tickangle=params["yaxis_tickangle"],
        tickfont_size=params["yaxis_tickfont_size"],
        range=yaxis_range,
        showgrid=params["yaxis_showgrid"],
        showline=params["yaxis_showline"],
        zeroline=params["yaxis_zeroline"],
        gridwidth=params["yaxis_gridwidth"],
        gridcolor=params["yaxis_gridcolor"],
        linewidth=params["yaxis_linewidth"],
        linecolor=params["yaxis_linecolor"],
        mirror=params["yaxis_mirror"],
        layer="below traces")  # Ensure y-axis grid is below the data
    
    return fig

def scatter3D(
    df: pd.DataFrame,
    col_x: str,
    col_y: str,
    col_z: str,
    col_category: str,
    color_palette: dict,
    col_size: str,
    col_text: str,
    **kwargs
) -> go.Figure:
    """
    Create a 3D scatter plot.

    Args:
        df (pd.DataFrame): DataFrame containing all data.
        col_x (str): Name of the column containing X values.
        col_y (str): Name of the column containing Y values.
        col_z (str): Name of the column containing Z values.
        col_category (str): Name of the column for colorization.
        color_palette (dict): A dictionary mapping categories with color values.
        col_size (str): Name of the column for dot sizes.
        col_text (str): Name of the column containing text for legend on hover.
        **kwargs: Additional keyword arguments to update default plotting parameters.

    Returns:
        go.Figure: Plotly figure object.
    """

    params = general_kwargs()
    params.update(kwargs)

    marker_size = params["marker_size"]
    marker_color = params["marker_color"]
    marker_size = params["marker_size"]
    col_hover = params["col_hover"]
    xaxis_range = params["xaxis_range"]
    yaxis_range = params["yaxis_range"]
    zaxis_range = params["zaxis_range"]

    fig = go.Figure()
    if col_category is not None:
        for i, category in enumerate(df[col_category].unique()):
            marker_color = color_palette.get(
                category, "rgb(0, 0, 0)"
            )  # Default to black if category not found

            # hovertemplate generation
            hovertemplate = (
                "<b>"
                + col_x
                + "</b>:"
                + df[col_x].astype(str)
                + "<br><b>"
                + col_y
                + "</b>:"
                + df[col_y].astype(str)
                + "<br><b>"
                + col_z
                + "</b>:"
                + df[col_z].astype(str)
            )
            # hovertemplate='<b>X</b>:'+df[df[col_category]==category][col_x].astype(str)+'<br><b>Y</b>:'+df[df[col_category]==category][col_y].astype(str)+'<br><b>Z</b>:'+df[df[col_category]==category][col_z].astype(str)+'<br><b>'+col_category+'</b>:'+str(category)
            if col_size is None:
                size = marker_size
            else:
                size = df[df[col_category] == category][col_size]
                hovertemplate += "<br><b>" + col_size + "</b>:" + size.astype(str)

            if len(col_hover) > 0:
                for c in col_hover:
                    hovertemplate += (
                        "<br><b>"
                        + str(c)
                        + "</b>:"
                        + df[c].astype(str).apply(wrap_text)
                    )

            fig.add_trace(
                go.Scatter3d(
                    x=df[df[col_category] == category][col_x],
                    y=df[df[col_category] == category][col_y],
                    z=df[df[col_category] == category][col_z],
                    text=df[df[col_category] == category][col_text],
                    mode=params["mode"],
                    textposition=params["textposition"],
                    marker=dict(
                        color=marker_color,  # dots color
                        size=size,  # dots size
                        opacity=params["marker_opacity"],  # dots opacity
                        line_color=params["marker_line_color"],  # line color around dot
                        line_width=params["marker_line_width"],  # line width around dot
                        sizemode=params["marker_sizemode"],  # size mode
                        sizemin=params["marker_sizemin"],  # minimum size of dot
                        symbol=params["marker_symbol"],  # type of dot
                    ),
                    name=category,  # trace name
                    hovertemplate=hovertemplate + "<extra></extra>",
                )
            )
    else:
        hovertemplate = (
            "<b>X</b>:"
            + df[col_x].astype(str)
            + "<br><b>Y</b>:"
            + df[col_y].astype(str)
            + "<br><b>Z</b>:"
            + df[col_z].astype(str)
        )
        if col_size is None:
            size = marker_size
        else:
            size = df[col_size]
            hovertemplate += "<br><b>" + col_size + "</b>:" + size.astype(str)

        if len(col_hover) > 0:
            for c in col_hover:
                hovertemplate += (
                    "<br><b>" + str(c) + "</b>:" + df[c].astype(str).apply(wrap_text)
                )

        fig = go.Figure(
            go.Scatter3d(
                x=df[col_x],
                y=df[col_y],
                z=df[col_z],
                text=df[col_text],
                mode=params["mode"],
                textposition=params["textposition"],
                marker=dict(
                    color=marker_color,  # dots color
                    size=size,  # dots size
                    opacity=params["marker_opacity"],  # dots opacity
                    line_color=params["marker_line_color"],  # line color around dot
                    line_width=params["marker_line_width"],  # line width arount dot
                    sizemode=params["marker_sizemode"],  # Scale marker sizes
                    sizemin=params["marker_sizemin"],  # minimum size of dot
                    symbol=params["marker_symbol"],  # type of dot
                    colorscale=params["marker_colorscale"],
                    showscale=params["showscale"],
                ),
                name="",
                hovertemplate=hovertemplate + "<extra></extra>",
            )
        )

    # we calculate X and Y axis ranges.
    if yaxis_range is None:
        yaxis_range = [df[col_y].min() - 0.1, df[col_y].max() + 0.1]
    if xaxis_range is None:
        xaxis_range = [df[col_x].min() - 0.1, df[col_x].max() + 0.1]
    if zaxis_range is None:
        zaxis_range = [df[col_z].min() - 0.1, df[col_z].max() + 0.1]
    if yaxis_range == "auto":
        yaxis_range = None
    if xaxis_range == "auto":
        xaxis_range = None
    if zaxis_range == "auto":
        zaxis_range = None

    fig.update_layout(
        title_text=params["title_text"],  # graph title
        width=params["width"],  # plot size
        height=params["height"],  # plot size
        template=params["template"],
        paper_bgcolor=params["paper_bgcolor"],  # background color (around plot)
        font_family=params["font_family"],  # font
        font_size=params["font_size"],
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.12,
            xanchor="right",
            x=1,
            itemsizing="constant",
        ),
    )

    fig.update_layout(
        scene=dict(
                camera=dict(  # camera orientation at start
                up=dict(x=1, y=0, z=2),
                center=dict(x=0, y=0, z=0),
                eye=dict(x=2, y=1.25, z=0.5),
            ),
            xaxis=dict(
                backgroundcolor=params["plot_bgcolor"],
                title=params["xaxis_title"],
                title_font_size=params["xaxis_title_font_size"],
                tickangle=params["xaxis_tickangle"],
                tickfont_size=params["xaxis_tickfont_size"],
                range=xaxis_range,
                showgrid=params["xaxis_showgrid"],
                showline=params["xaxis_showline"],
                zeroline=params["xaxis_zeroline"],
                gridwidth=params["xaxis_gridwidth"],
                gridcolor=params["xaxis_gridcolor"],
                linewidth=params["xaxis_linewidth"],
                linecolor=params["xaxis_linecolor"],
                mirror=params["xaxis_mirror"],
                
            ),
            yaxis=dict(
                backgroundcolor=params["plot_bgcolor"],
                title=params["yaxis_title"],
                title_font_size=params["yaxis_title_font_size"],
                tickangle=params["yaxis_tickangle"],
                tickfont_size=params["yaxis_tickfont_size"],
                range=yaxis_range,
                showgrid=params["yaxis_showgrid"],
                showline=params["yaxis_showline"],
                zeroline=params["yaxis_zeroline"],
                gridwidth=params["yaxis_gridwidth"],
                gridcolor=params["yaxis_gridcolor"],
                linewidth=params["yaxis_linewidth"],
                linecolor=params["yaxis_linecolor"],
                mirror=params["yaxis_mirror"],
            ),
            zaxis=dict(
                backgroundcolor=params["plot_bgcolor"],
                title=params["zaxis_title"],
                title_font_size=params["zaxis_title_font_size"],
                tickangle=params["zaxis_tickangle"],
                tickfont_size=params["zaxis_tickfont_size"],
                range=zaxis_range,
                showgrid=params["zaxis_showgrid"],
                showline=params["zaxis_showline"],
                zeroline=params["zaxis_zeroline"],
                gridwidth=params["zaxis_gridwidth"],
                gridcolor=params["zaxis_gridcolor"],
                linewidth=params["zaxis_linewidth"],
                linecolor=params["zaxis_linecolor"],
                mirror=params["zaxis_mirror"],
            ),
        )
    )

    return fig


def fig_bar_trend(df: pd.DataFrame, col_x: str, col_bar: str, col_trend: str, **kwargs) -> go.Figure:
    """
    Display a graph that combines bar and trend chart to compare 2 metrics.

    Args:
        df (pd.DataFrame): DataFrame containing all data.
        col_x (str): Name of the column containing X values.
        col_bar (str): Name of the column containing Y values. Data represented as bar diagram.
        col_trend (str): Name of the column containing Z values. Data represented as trend line.
        **kwargs: Additional keyword arguments to update default plotting parameters.

    Returns:
        go.Figure: Plotly figure object.
    """
    
    params = general_kwargs()
    params.update(kwargs)


    xaxis_title = params["xaxis_title"]
    xaxis_range = params["xaxis_range"]
    yaxis_title = params["yaxis_title"]
    yaxis_range = params["yaxis_range"]
    zaxis_title = params["zaxis_title"]
    zaxis_range = params["xaxis_range"]
    col_hover = params['col_hover']

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    hovertemplate="<br><b>"+col_x+"</b> :"+df[col_x].astype(str)+"<br><b>"+col_bar+"</b> - "+df[col_bar].astype(str)+"<br><b>"+col_trend+"</b> : "+df[col_trend].astype(str)+"<extra></extra>"

    for c in col_hover:
        hovertemplate+="<br><b>"+c+"</b> :"+df[c].apply(wrap_text).astype(str)

    fig.add_trace(
        go.Scatter(
            x=df[col_x].apply(wrap_text), 
            y=df[col_trend], 
            name=params["zaxis_title"],
            mode=params["mode"], 
           
            line_color=params["marker_line_color"], 
            line_width=params["marker_line_width"],
            textfont=dict(size=params["font_size"]),
            hovertemplate = hovertemplate,
        ),
        secondary_y=True,
    )
    # Add traces
    fig.add_trace(
        go.Bar(
            x=df[col_x].apply(wrap_text), 
            y = df[col_bar], 
            name = params["yaxis_title"], 
            marker_color=params["marker_color"], 
            opacity = params["marker_opacity"],
            hovertemplate=hovertemplate
        ),
        secondary_y=False,

    )

    if yaxis_range is None:
        try:
            yaxis_range=[-0.5,df[col_bar].max()*1.01]
        except Exception as e:
            pass
            print(e)
            yaxis_range is None
    if xaxis_range is None:
        try:
            xaxis_range = [df[col_x].min() - 0.1, df[col_x].max() + 0.1]
        except Exception as e:
            pass
            print(e)
            xaxis_range=None
    if zaxis_range is None:
        try:
            zaxis_range = [-0.5,df[col_trend].max()*1.01]
        except Exception as e:
            pass
            print(e)
            zaxis_range=None

    if yaxis_range == "auto":
        yaxis_range = None
    if xaxis_range == "auto":
        xaxis_range = None
    if zaxis_range == "auto":
        zaxis_range = None


    # secondary_axis_range=[-0.5,df[col_trend].max()*1.01]

    fig.update_layout(
        title_text=params["title_text"],  # graph title
        width=params["width"],  # plot size
        height=params["height"],  # plot size
        showlegend = params["showlegend"],
        template=params["template"],
        plot_bgcolor=params["plot_bgcolor"],  # background color (plot)
        paper_bgcolor=params["paper_bgcolor"],  # background color (around plot)
        font_family=params["font_family"],  # font
        font_size=params["font_size"],
        xaxis_title=params["xaxis_title"],
        xaxis_title_font_size=params["xaxis_title_font_size"],
        xaxis_tickangle=params["xaxis_tickangle"],
        xaxis_tickfont_size=params["xaxis_tickfont_size"],
        xaxis_range=xaxis_range,
        xaxis_showgrid=params["xaxis_showgrid"],
        xaxis_showline=params["xaxis_showline"],
        xaxis_zeroline=params["xaxis_zeroline"],
        xaxis_gridwidth=params["xaxis_gridwidth"],
        xaxis_gridcolor=params["xaxis_gridcolor"],
        xaxis_linewidth=params["xaxis_linewidth"],
        xaxis_linecolor=params["xaxis_linecolor"],
        xaxis_mirror=params["xaxis_mirror"],
        yaxis_title=params["yaxis_title"],
        yaxis_title_font_size=params["yaxis_title_font_size"],
        yaxis_tickangle=params["yaxis_tickangle"],
        yaxis_tickfont_size=params["yaxis_tickfont_size"],
        yaxis_range=yaxis_range,
        yaxis_showgrid=params["yaxis_showgrid"],
        yaxis_showline=params["yaxis_showline"],
        yaxis_zeroline=params["yaxis_zeroline"],
        yaxis_gridwidth=params["yaxis_gridwidth"],
        yaxis_gridcolor=params["yaxis_gridcolor"],
        yaxis_linewidth=params["yaxis_linewidth"],
        yaxis_linecolor=params["yaxis_linecolor"],
        yaxis_mirror=params["yaxis_mirror"],
    )

    # # Set y-axes titles
    fig.update_yaxes(title_text=yaxis_title, range = yaxis_range, secondary_y=False)
    fig.update_yaxes(title_text=zaxis_title, range = zaxis_range, secondary_y=True)  
    fig.update_xaxes(layer="below traces")  # Ensure x-axis grid is below the data
    fig.update_yaxes(layer="below traces")  # Ensure y-axis grid is below the data
    
    return fig

def bar_subplots(df: pd.DataFrame,
                 col_x: str,
                 col_y: str,
                 col_cat: str,
                 color_palette: dict = None,
                 n_top_words: int = 20,
                 **kwargs
                 ) -> go.Figure:
    """
    Create subplots of horizontal bar charts.

    Args:
        df (pd.DataFrame): DataFrame containing data for bar charts.
        col_x (str): Name of the column containing x-axis values.
        col_y (str): Name of the column containing y-axis values.
        col_cat (str): Name of the column containing categories.
        color_palette (Optional[Dict[str, str]], optional): Dictionary mapping categories to colors. Defaults to None.
        n_cols (int, optional): Number of columns in the subplot grid. Defaults to 4.
        n_top_words (int, optional): Number of top words to display in each bar chart. Defaults to 20.
        **kwargs: Additional keyword arguments to update default plotting parameters.

    Returns:
        go.Figure: Plotly Figure object representing the subplots of horizontal bar charts.
    """

    params = general_kwargs()
    params.update(kwargs)

    marker_color = params['marker_color']
    textposition=params["textposition"]
    vertical_spacing=params['vertical_spacing']
    horizontal_spacing= params["horizontal_spacing"]
    col_hover = params['col_hover']
    n_cols = params['n_cols']
    categories = df[col_cat].unique()

    # user define a number of columns, we compute the number of rows requires
    n_rows =  math.ceil(len(categories) / n_cols)

    # fine tune parameter according to the text position provided
    if textposition == 'inside':
        horizontal_spacing = (horizontal_spacing / n_cols)/2
    else:
        horizontal_spacing = (horizontal_spacing / n_cols)
        
    # create subplots
    fig = make_subplots(
        rows = n_rows,                           # number of rows
        cols = n_cols,                           # number of columns
        subplot_titles = list(categories),       # title for each subplot
        vertical_spacing = vertical_spacing / n_rows,     # space between subplots
        horizontal_spacing = horizontal_spacing  # space between subplots
        )

    # create bar traces for each subplot
    row_id = 0
    col_id = 0
    for i, category in enumerate(categories):
        
        # define bar color or create a random color
        if color_palette:
            marker_color = color_palette.get(category, generate_random_hexadecimal_color())
        else : 
            marker_color = generate_random_hexadecimal_color()

        # define row and column position
        col_id +=1 
        if i % n_cols == 0:
            row_id += 1
        if col_id > n_cols:
            col_id = 1

        # select data
        current_df = df[df[col_cat]==category].sort_values(by=col_x, ascending = True)
        hovertemplate='<b>'+current_df[current_df[col_cat]==category][col_y].astype(str)+"</b><br>"+current_df[current_df[col_cat]==category][col_x].astype(str)
        for col in col_hover:
            hovertemplate += '<br><b>'+col+': '+current_df[current_df[col_cat]==category][col].astype(str)+'</b>'

        if textposition == 'inside':
            # showticklabels = False
            text=current_df[col_y].head(n_top_words)
        else:
            # showticklabels = True
            textposition="auto"
            text=None

        fig.add_trace(
            go.Bar(
                x=current_df[col_x].tail(n_top_words), 
                y=current_df[col_y].tail(n_top_words),
                opacity=params["marker_opacity"],
                orientation=params["orientation"],                                # horizontal bars
                name=category,                                  # trace name for legend
                text=text,                                      # text to display
                textposition=textposition,                      # text position
                textangle=params["xaxis_tickangle"],                                    # text angle
                marker_color = marker_color,                           # bar color
                hovertemplate=hovertemplate+"<extra></extra>"   # hover info
                ),
            row=row_id, 
            col=col_id
            )

        fig.update_layout(
            margin=dict(l=75, r=75, t=75, b=50),
            title_text=params["title_text"],
            width=n_cols * params["width"],  # plot size
            height=n_rows * n_top_words * params["height"],  # plot size
            showlegend = params["showlegend"],
            font_family=params["font_family"],
            font_size=params["font_size"],
            template=params["template"],
            plot_bgcolor=params["plot_bgcolor"],  # background color (plot)
            paper_bgcolor=params["paper_bgcolor"],  # background color (around plot)
            uniformtext_minsize=params["uniformtext_minsize"],
        )

    fig.update_yaxes(
        title=params["yaxis_title"],
        title_font_size=params["yaxis_title_font_size"],
        tickangle=params["yaxis_tickangle"],
        tickfont_size=params["yaxis_tickfont_size"],
        range=params["yaxis_range"],
        showgrid=params["yaxis_showgrid"],
        showline=params["yaxis_showline"],
        zeroline=params["yaxis_zeroline"],
        gridwidth=params["yaxis_gridwidth"],
        gridcolor=params["yaxis_gridcolor"],
        linewidth=params["yaxis_linewidth"],
        linecolor=params["yaxis_linecolor"],
        mirror=params["yaxis_mirror"],
        layer="below traces",
    )

    fig.update_xaxes(
        title=params["xaxis_title"],
        title_font_size=params["xaxis_title_font_size"],
        tickangle=params["xaxis_tickangle"],
        tickfont_size=params["xaxis_tickfont_size"],
        range=params["xaxis_range"],
        showgrid=params["xaxis_showgrid"],
        showline=params["xaxis_showline"],
        zeroline=params["xaxis_zeroline"],
        gridwidth=params["xaxis_gridwidth"],
        gridcolor=params["xaxis_gridcolor"],
        linewidth=params["xaxis_linewidth"],
        linecolor=params["xaxis_linecolor"],
        mirror=params["xaxis_mirror"],
        layer="below traces"
    )
    return fig

def trend_stacked_filled_area(df:pd.DataFrame, col_x:str, col_y:str, col_cat:str, color_palette:dict, **kwargs)->go.Figure:
    """
    Create a filled area trends

    Args:
        df (pd.DataFrame): DataFrame containing data for bar charts.
        col_x (str): Name of the column containing x-axis values.
        col_y (str): Name of the column containing y-axis values.
        col_cat (str): Name of the column containing categories.
        color_palette (Optional[Dict[str, str]], optional): Dictionary mapping categories to colors. Defaults to None.
        **kwargs: Additional keyword arguments to update default plotting parameters.

    Returns:
        go.Figure: Plotly Figure object representing the subplots of horizontal bar charts.
    """

    params = general_kwargs()
    params.update(kwargs)

    col_hover = params["col_hover"]

    categories = list(df[col_cat].unique())
    fig = go.Figure()
    for i, cat in enumerate(categories):
        
        current_df = df[df[col_cat] == cat]

        if color_palette:
            color = color_palette[cat]
        else:
            color = generate_random_hexadecimal_color()
        
        hovertemplate = (
            "<b>"
            + col_cat 
            +"</b>: "
            + str(cat)
            + "<br><b>"
            + col_x
            +"</b>: "
            + current_df[col_x].astype(str)
            + "<br><b>"
            + col_y
            + " </b>: "
            + current_df[col_y].astype(str)
        )
        for col in col_hover:
            hovertemplate+= "<br><b>"+col+"</b>: "+current_df[col].astype(str)

        fig.add_trace(go.Scatter(
            x=current_df[col_x],
            y=current_df[col_y],
            mode='lines',
            line=dict(width=0.5, color=color),
            stackgroup='one',
            name=cat,
            hovertemplate=hovertemplate+"<extra></extra>",
            groupnorm='percent' # sets the normalization for the sum of the stackgroup
        ))

    fig.update_layout(
        title_text=params["title_text"],  # graph title
        width=params["width"],  # plot size
        height=params["height"],  # plot size
        template=params['template'],
        plot_bgcolor=params['plot_bgcolor'],  # background color (plot)
        paper_bgcolor=params['paper_bgcolor'],  # background color (around plot)
        font_family=params['font_family'],  # font
        font_size=params['font_size'],
        showlegend=params['showlegend'],
        xaxis_title=params['xaxis_title'],
        xaxis_title_font_size=params["xaxis_title_font_size"],
        xaxis_tickangle=params['xaxis_tickangle'],
        xaxis_tickfont_size=params['xaxis_tickfont_size'],
        xaxis_range=params['xaxis_range'],
        xaxis_showgrid=params['xaxis_showgrid'],
        xaxis_showline=params['xaxis_showline'],
        xaxis_zeroline=params['xaxis_zeroline'],
        xaxis_gridwidth=params['xaxis_gridwidth'],
        xaxis_gridcolor=params['xaxis_gridcolor'],
        xaxis_linewidth=params['xaxis_linewidth'],
        xaxis_linecolor=params['xaxis_linecolor'],
        xaxis_mirror=params['xaxis_mirror'],
        yaxis_title=params['yaxis_title'],
        yaxis_title_font_size=params["yaxis_title_font_size"],
        yaxis_tickangle=params['yaxis_tickangle'],
        yaxis_tickfont_size=params['yaxis_tickfont_size'],
        yaxis_range=params['yaxis_range'],
        yaxis_showgrid=params['yaxis_showgrid'],
        yaxis_showline=params['yaxis_showline'],
        yaxis_zeroline=params['yaxis_zeroline'],
        yaxis_gridwidth=params['yaxis_gridwidth'],
        yaxis_gridcolor=params['yaxis_gridcolor'],
        yaxis_linewidth=params['yaxis_linewidth'],
        yaxis_linecolor=params['yaxis_linecolor'],
        yaxis_mirror=params['yaxis_mirror'],
        yaxis=dict(
            type='linear',
            range=[1, 100],
            ticksuffix='%')
    )
    fig.update_xaxes(layer="below traces")  # Ensure x-axis grid is below the data
    fig.update_yaxes(layer="below traces")  # Ensure y-axis grid is below the data

    return fig

def subplots_trend_stacked_filled_area(df: pd.DataFrame, col_x: str, col_y:str, col_cat:str, col_sub_cat:str, color_palette:dict, **kwargs)->go.Figure:
    """
    Create subplots of filled area trends

    Args:
        df (pd.DataFrame): DataFrame containing data for bar charts.
        col_x (str): Name of the column containing x-axis values.
        col_y (str): Name of the column containing y-axis values.
        col_cat (str): Name of the column containing categories.
        col_sub_cat (str): Name of the column containing sub categories.
        color_palette (Optional[Dict[str, str]], optional): Dictionary mapping categories to colors. Defaults to None.
        **kwargs: Additional keyword arguments to update default plotting parameters.

    Returns:
        go.Figure: Plotly Figure object representing the subplots of horizontal bar charts.
    """

    params = general_kwargs()
    params.update(kwargs)

    col_hover = params["col_hover"]
    n_cols = params["n_cols"]
    categories = list(df[col_cat].unique())
    
    n_rows = math.ceil(len(categories) / n_cols)

    fig = make_subplots(
        rows=n_rows,  # number of rows
        cols=n_cols,  # number of columns
        vertical_spacing=params["vertical_spacing"],  # space between subplots
        horizontal_spacing=params["horizontal_spacing"],
        subplot_titles=categories,
        shared_xaxes=params["shared_xaxes"],
        shared_yaxes=params["shared_yaxes"]
    )

    row_id = 0
    col_id = 0

    for i, cat in enumerate(categories):
        
        current_df = df[df[col_cat] == cat]

        # define row and column position
        col_id += 1
        if i % n_cols == 0:
            row_id += 1
        if col_id > n_cols:
            col_id = 1
        
        sub_categories = list(current_df[col_sub_cat].unique())

        for j, sub_cat in enumerate(sub_categories):

            df_sentiment  = current_df[current_df[col_sub_cat] == sub_cat]

            if color_palette:
                color = color_palette[sub_cat]
            else:
                color = generate_random_hexadecimal_color()

            hovertemplate = (
                "<b>"
                + col_cat 
                +"</b>: "
                + str(cat)
                + "<br><b>"
                "<b>"
                + col_sub_cat 
                +"</b>: "
                + str(sub_cat)
                + "<br><b>"
                + col_x
                +"</b>: "
                + current_df[col_x].astype(str)
                + "<br><b>"
                + col_y
                + " </b>: "
                + current_df[col_y].astype(str)
            )
            for col in col_hover:
                hovertemplate+= "<br><b>"+col+"</b>: "+current_df[col].astype(str)

            fig.add_trace(
                go.Scatter(
                    x=df_sentiment [col_x],
                    y=df_sentiment [col_y],
                    mode='lines',
                    line=dict(width=0.5, color=color),
                    stackgroup='one',
                    name=f"{cat} - {sub_cat}",
                    hovertemplate=hovertemplate+"<extra></extra>",
                    groupnorm='percent' # sets the normalization for the sum of the stackgroup
                ),
                row=row_id,
                col=col_id,
            )

            fig.update_yaxes(
                # title=params["yaxis_title"],
                # title_font_size=params["yaxis_title_font_size"],
                tickangle=params["yaxis_tickangle"],
                tickfont_size=params["yaxis_tickfont_size"],
                showgrid=params["yaxis_showgrid"],
                showline=params["yaxis_showline"],
                zeroline=params["yaxis_zeroline"],
                gridwidth=params["yaxis_gridwidth"],
                gridcolor=params["yaxis_gridcolor"],
                linewidth=params["yaxis_linewidth"],
                linecolor=params["yaxis_linecolor"],
                mirror=params["yaxis_mirror"],
                type='linear',
                range=[1, 100],
                ticksuffix='%',
                row=row_id,
                col=col_id,
                layer="below traces"
            )


            fig.update_xaxes(
                # title=params["xaxis_title"],
                # title_font_size=params["xaxis_title_font_size"],
                tickangle=params["xaxis_tickangle"],
                tickfont_size=params["xaxis_tickfont_size"],
                range=params["xaxis_range"],
                showgrid=params["xaxis_showgrid"],
                showline=params["xaxis_showline"],
                zeroline=params["xaxis_zeroline"],
                gridwidth=params["xaxis_gridwidth"],
                gridcolor=params["xaxis_gridcolor"],
                linewidth=params["xaxis_linewidth"],
                linecolor=params["xaxis_linecolor"],
                mirror=params["xaxis_mirror"],
                row=row_id,
                col=col_id,
                layer="below traces"
            )

    fig.update_layout(
            title_text=params["title_text"],
            width=params["width"]*n_cols,
            height=params["height"]*n_rows,
            font_family=params["font_family"],
            font_size=params["font_size"],
            template=params["template"],
            plot_bgcolor=params["plot_bgcolor"],  # background color (plot)
            paper_bgcolor=params["paper_bgcolor"],  # background color (around plot)
            showlegend=params["showlegend"]
        )
    for r_id in range(1, n_rows+1):
        for c_id in range(1, n_cols+1):
            fig.update_yaxes(title=params["yaxis_title"], title_font_size=params["yaxis_title_font_size"], row=r_id, col=1)
            fig.update_xaxes(title=params["xaxis_title"], title_font_size=params["xaxis_title_font_size"], row=r_id, col=c_id)

    return fig

def pie(df: pd.DataFrame, 
        col_x: str, 
        col_y: str, 
        col_color: str, 
        **kwargs
        ) -> go.Figure:
    """
    Creates a Plotly pie chart.

    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        col_x (str): The name of the column containing the labels for the pie chart slices.
        col_y (str): The name of the column containing the values for the pie chart slices.
        col_color (str): The name of the column containing the colors for the pie chart slices.
        **kwargs: Additional keyword arguments to update default plotting parameters.

    Returns:
        fig (go.Figure): The Plotly Figure object representing the pie chart.
    """    
    params = general_kwargs()
    params.update(kwargs)

    col_hover = params["col_hover"]

    hovertemplate='<b>'+ df[col_x].astype(str) +"</b><br>"+ str(col_y) + " : "+df[col_y].astype(str) 
    for c in col_hover:
        hovertemplate += (
            "<br><b>"
            + str(c)
            + "</b>:"
            + df[c].astype(str).apply(wrap_text)
        )


    fig = go.Figure()
    fig.add_trace(go.Pie(
        labels=df[col_x],
        values=df[col_y],
        name="",
        hole=params["hole"],
        hovertemplate=hovertemplate+ "<extra></extra>",
        marker=dict(colors=list(df[col_color])),
        textfont_size = 18,
        sort=False 
        ),
    )

    # Update layout and axes
    fig.update_layout(
        margin=dict(l=75, r=75, t=75, b=50),
        title_text=params["title_text"], 
        showlegend = params["showlegend"],
        width = params["width"],
        height= params["height"],
        font_family=params["font_family"],
        font_size=params["font_size"],
        template=params["template"],
        plot_bgcolor=params["plot_bgcolor"],  # background color (plot)
        paper_bgcolor=params["paper_bgcolor"],  # background color (around plot)
        uniformtext_minsize=params["uniformtext_minsize"],
        uniformtext_mode=params["uniformtext_mode"],
    )
    fig.update_yaxes(
        title=params["yaxis_title"],
        title_font_size=params["yaxis_title_font_size"],
        tickangle=params["yaxis_tickangle"],
        tickfont_size=params["yaxis_tickfont_size"],
        range=params["yaxis_range"],
        showgrid=params["yaxis_showgrid"],
        showline=params["yaxis_showline"],
        zeroline=params["yaxis_zeroline"],
        gridwidth=params["yaxis_gridwidth"],
        gridcolor=params["yaxis_gridcolor"],
        linewidth=params["yaxis_linewidth"],
        linecolor=params["yaxis_linecolor"],
        mirror=params["yaxis_mirror"],
    )

    fig.update_xaxes(
        title=params["xaxis_title"],
        title_font_size=params["xaxis_title_font_size"],
        tickangle=params["xaxis_tickangle"],
        tickfont_size=params["xaxis_tickfont_size"],
        range=params["xaxis_range"],
        showgrid=params["xaxis_showgrid"],
        showline=params["xaxis_showline"],
        zeroline=params["xaxis_zeroline"],
        gridwidth=params["xaxis_gridwidth"],
        gridcolor=params["xaxis_gridcolor"],
        linewidth=params["xaxis_linewidth"],
        linecolor=params["xaxis_linecolor"],
        mirror=params["xaxis_mirror"],
    )
    return fig

def pie_subplots(df: pd.DataFrame,
                 col_x: str,
                 col_y: str,
                 col_cat: str,
                 col_color: str,
                 **kwargs) -> go.Figure:
    """
    Create subplots of pie charts.

    Args:
        df (pd.DataFrame): DataFrame containing data for pie charts.
        col_x (str): Name of the column containing labels.
        col_y (str): Name of the column containing values.
        col_cat (str): Name of the column containing categories.
        col_color (str): Name of the column containing colors.
        **kwargs: Additional keyword arguments to update default plotting parameters.

    Returns:
        go.Figure: Plotly Figure object representing the subplots of pie charts.
    """    

    params = general_kwargs()
    params.update(kwargs)

    n_cols=params["n_cols"]
    col_hover=params["col_hover"]

    categories = df[col_cat].unique()

    # user define a number of columns, we compute the number of rows requires
    n_rows =  math.ceil(len(categories) / n_cols)
        
    specs = [[{'type':'domain'}] * n_cols] * n_rows
    # create subplots
    fig = make_subplots(
        rows=n_rows,
        cols=n_cols,
        subplot_titles=list(categories),
        horizontal_spacing=params["horizontal_spacing"] / n_cols,
        vertical_spacing=params["vertical_spacing"] / n_rows,
        specs=specs
    )

    # create pie chart subplots
    for i, category in enumerate(categories):
        col_id = i % n_cols + 1
        row_id = i // n_cols + 1 

        current_df = df[df[col_cat] == category]
        hovertemplate = '<b>' + current_df[current_df[col_cat] == category][col_y].astype(str) + "</b><br>" + current_df[current_df[col_cat] == category][col_x].astype(str)
        for c in col_hover:
            hovertemplate += (
                "<br><b>"
                + str(c)
                + "</b> : "
                + current_df[current_df[col_cat] == category][c].astype(str).apply(wrap_text)
            )

        fig.add_trace(
            go.Pie(
            labels=current_df[col_x],
            values=current_df[col_y],
            name=category,
            hole=params["hole"],
            hovertemplate=hovertemplate+"<extra></extra>",
            marker=dict(colors=list(current_df[col_color])),
            sort=False 
            ),
        row=row_id,
        col=col_id,
        )

    # Update layout and axes
    fig.update_layout(
        height=n_rows * params["height"],
        width=n_cols * params["width"],
        uniformtext_minsize=params["uniformtext_minsize"],
        margin=dict(l=75, r=75, t=75, b=50),
        showlegend=params["showlegend"],
        font_family=params["font_family"],
        font_size=params["font_size"],
        template=params["template"],
        plot_bgcolor=params["plot_bgcolor"],  # background color (plot)
        paper_bgcolor=params["paper_bgcolor"],
        title_text=params["title_text"]
    )
    fig.update_yaxes(
        title=params["yaxis_title"],
        title_font_size=params["yaxis_title_font_size"],
        tickangle=params["yaxis_tickangle"],
        tickfont_size=params["yaxis_tickfont_size"],
        range=params["yaxis_range"],
        showgrid=params["yaxis_showgrid"],
        showline=params["yaxis_showline"],
        zeroline=params["yaxis_zeroline"],
        gridwidth=params["yaxis_gridwidth"],
        gridcolor=params["yaxis_gridcolor"],
        linewidth=params["yaxis_linewidth"],
        linecolor=params["yaxis_linecolor"],
        mirror=params["yaxis_mirror"],
    )

    fig.update_xaxes(
        title=params["xaxis_title"],
        title_font_size=params["xaxis_title_font_size"],
        tickangle=params["xaxis_tickangle"],
        tickfont_size=params["xaxis_tickfont_size"],
        range=params["xaxis_range"],
        showgrid=params["xaxis_showgrid"],
        showline=params["xaxis_showline"],
        zeroline=params["xaxis_zeroline"],
        gridwidth=params["xaxis_gridwidth"],
        gridcolor=params["xaxis_gridcolor"],
        linewidth=params["xaxis_linewidth"],
        linecolor=params["xaxis_linecolor"],
        mirror=params["xaxis_mirror"],
    )

    return fig

def horizontal_stacked_bars(df: pd.DataFrame,
                             col_x: str,
                             col_y: str,
                             col_percentage: str,
                             col_cat: str,
                             col_color: str,
                             **kwargs) -> go.Figure:
    """
    Create horizontal stacked bar plots.

    Args:
        df (pd.DataFrame): DataFrame containing data for the bar plots.
        col_x (str): Name of the column containing x-axis values.
        col_y (str): Name of the column containing y-axis values.
        col_percentage (str): Name of the column containing percentage values.
        col_cat (str): Name of the column containing categories.
        col_color (str): Name of the column containing colors.
        **kwargs: Additional keyword arguments to update default plotting parameters.

    Returns:
        go.Figure: Plotly Figure object representing the horizontal stacked bar plots.
    """
    params = general_kwargs()
    params.update(kwargs)

    categories = df[col_cat].unique()

    col_hover = params["col_hover"]

    n_cols=2
    fig = make_subplots(
        rows = 1,                           # number of rows
        cols = 2,                           # number of columns
        # subplot_titles = list(categories),       # title for each subplot
        vertical_spacing = params["vertical_spacing"],     # space between subplots
        horizontal_spacing = params["horizontal_spacing"] / n_cols # space between subplots
        )
    
    for cat in categories:
        current_df = df[df[col_cat] == cat]
        hovertemplate= "<b>Catégorie</b> : "+str(cat)+"<br><b>"+str(col_x)+"</b> : "+current_df[col_x].astype(str)+" ("+current_df[col_percentage].map("{:.1%}".format).astype(str)+")<br><b>"+ str(col_y) + "</b> : "+current_df[col_y].astype(str)

        for c in col_hover:
            hovertemplate += (
                "<br><b>"
                + str(c)
                + "</b>:"
                + current_df[c].astype(str).apply(wrap_text)
            )

        fig.add_trace(
            go.Bar(
                x=current_df[col_x], 
                y=current_df[col_y],
                orientation=params['orientation'],
                text = current_df[col_x],
                textposition=params["textposition"],
                name=cat, 
                marker=dict(color=current_df[col_color]),
                hovertemplate=hovertemplate+'<extra></extra>',
                textangle=params["xaxis_tickangle"],
                ),
            row=1,
            col=1,
        )

        fig.add_trace(
            go.Bar(
                
                x=current_df[col_percentage], 
                y=current_df[col_y],
                orientation=params['orientation'],
                textposition=params["textposition"],
                text = current_df[col_percentage].map("{:.1%}".format),
                textangle=params["xaxis_tickangle"],
                name="",
                marker=dict(color=current_df[col_color]),
                hovertemplate=hovertemplate+'<extra></extra>',
                showlegend = False
                ),
            row=1,
            col=2,
        )

    fig.update_layout(
            barmode='stack',
            title_text=params["title_text"], 
            showlegend=params['showlegend'],
            width = params["width"],
            height= params["height"],
            font_family=params["font_family"],
            font_size=params["font_size"],
            template=params["template"],
            plot_bgcolor=params["plot_bgcolor"],  # background color (plot)
            paper_bgcolor=params["paper_bgcolor"],
            uniformtext_minsize=params["uniformtext_minsize"],
            uniformtext_mode=params["uniformtext_mode"],

        )
    
    fig.update_yaxes(
        # title=params["yaxis_title"],
        title_font_size=params["yaxis_title_font_size"],
        tickangle=params["yaxis_tickangle"],
        tickfont_size=params["yaxis_tickfont_size"],
        range=params["yaxis_range"],
        showgrid=params["yaxis_showgrid"],
        showline=params["yaxis_showline"],
        zeroline=params["yaxis_zeroline"],
        gridwidth=params["yaxis_gridwidth"],
        gridcolor=params["yaxis_gridcolor"],
        linewidth=params["yaxis_linewidth"],
        linecolor=params["yaxis_linecolor"],
        mirror=params["yaxis_mirror"],
    )

    fig.update_xaxes(
        # title=params["xaxis_title"],
        title_font_size=params["xaxis_title_font_size"],
        tickangle=params["xaxis_tickangle"],
        tickfont_size=params["xaxis_tickfont_size"],
        # range=params["xaxis_range"],
        showgrid=params["xaxis_showgrid"],
        showline=params["xaxis_showline"],
        zeroline=params["xaxis_zeroline"],
        gridwidth=params["xaxis_gridwidth"],
        gridcolor=params["xaxis_gridcolor"],
        linewidth=params["xaxis_linewidth"],
        linecolor=params["xaxis_linecolor"],
        mirror=params["xaxis_mirror"]
    )
    fig.update_xaxes(title_text=params["xaxis_title"])
    fig.update_yaxes(title_text=params["yaxis_title"], row=1,col=1)
    fig.update_xaxes(title_text=params["xaxis_title"], range=[0,1], tickformat=".0%", row=1,col=2)
    fig.update_yaxes(showticklabels = False, row=1,col=2)
    
    return fig

def bar_stacked(df: pd.DataFrame,
                             col_x: str,
                             col_y: str,
                             col_cat: str,
                             col_color: str,
                             **kwargs) -> go.Figure:
    """
    Create horizontal stacked bar plots.

    Args:
        df (pd.DataFrame): DataFrame containing data for the bar plots.
        col_x (str): Name of the column containing x-axis values.
        col_y (str): Name of the column containing y-axis values.
        col_percentage (str): Name of the column containing percentage values.
        col_cat (str): Name of the column containing categories.
        col_color (str): Name of the column containing colors.
        **kwargs: Additional keyword arguments to update default plotting parameters.

    Returns:
        go.Figure: Plotly Figure object representing the horizontal stacked bar plots.
    """
    params = general_kwargs()
    params.update(kwargs)

    categories = df[col_cat].unique()

    col_hover = params["col_hover"]

    fig = go.Figure()
    
    for cat in categories:
        current_df = df[df[col_cat] == cat]
        hovertemplate= "<b>Catégorie</b> : "+str(cat)+"<br><b>"+str(col_x)+"</b> : "+current_df[col_x].astype(str)+ str(col_y) + "</b> : "+current_df[col_y].astype(str)

        for c in col_hover:
            hovertemplate += (
                "<br><b>"
                + str(c)
                + "</b>:"
                + current_df[c].astype(str).apply(wrap_text)
            )

        fig.add_trace(
            go.Bar(
                x=current_df[col_x], 
                y=current_df[col_y],
                orientation=params['orientation'],
                text = current_df[col_x],
                textposition=params["textposition"],
                name=cat, 
                marker=dict(color=current_df[col_color]),
                hovertemplate=hovertemplate+'<extra></extra>',
                textangle=params["xaxis_tickangle"],
                )
        )

    fig.update_layout(
            barmode='stack',
            title_text=params["title_text"], 
            showlegend=params['showlegend'],
            width = params["width"],
            height= params["height"],
            font_family=params["font_family"],
            font_size=params["font_size"],
            template=params["template"],
            plot_bgcolor=params["plot_bgcolor"],  # background color (plot)
            paper_bgcolor=params["paper_bgcolor"],
            uniformtext_minsize=params["uniformtext_minsize"],
            uniformtext_mode=params["uniformtext_mode"],

        )
    
    fig.update_yaxes(
        # title=params["yaxis_title"],
        title_font_size=params["yaxis_title_font_size"],
        tickangle=params["yaxis_tickangle"],
        tickfont_size=params["yaxis_tickfont_size"],
        range=params["yaxis_range"],
        showgrid=params["yaxis_showgrid"],
        showline=params["yaxis_showline"],
        zeroline=params["yaxis_zeroline"],
        gridwidth=params["yaxis_gridwidth"],
        gridcolor=params["yaxis_gridcolor"],
        linewidth=params["yaxis_linewidth"],
        linecolor=params["yaxis_linecolor"],
        mirror=params["yaxis_mirror"],
    )

    fig.update_xaxes(
        # title=params["xaxis_title"],
        title_font_size=params["xaxis_title_font_size"],
        tickangle=params["xaxis_tickangle"],
        tickfont_size=params["xaxis_tickfont_size"],
        # range=params["xaxis_range"],
        showgrid=params["xaxis_showgrid"],
        showline=params["xaxis_showline"],
        zeroline=params["xaxis_zeroline"],
        gridwidth=params["xaxis_gridwidth"],
        gridcolor=params["xaxis_gridcolor"],
        linewidth=params["xaxis_linewidth"],
        linecolor=params["xaxis_linecolor"],
        mirror=params["xaxis_mirror"]
    )
    fig.update_xaxes(title_text=params["xaxis_title"])
    fig.update_yaxes(title_text=params["yaxis_title"])
    fig.update_yaxes(showticklabels = False)
    
    return fig

def bar_trend_per_cat(df: pd.DataFrame, 
                              col_x: str, 
                              col_cat: str, 
                              col_y: str, 
                              col_z: str, 
                              col_color: str, 
                              **kwargs
                              ) -> go.Figure:
    """
    Creates a Plotly stacked bar chart with multiple categories, each represented as a separate subplot.

    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        col_x (str): The name of the column containing dates.
        col_cat (str): The name of the column containing categories.
        col_y (str): The name of the column containing the first metric values, represented as Bar.
        col_z (str): The name of the column containing the second metric values, represented as Bar.
        col_color (str): The name of the column containing the color codes for each category.
        **kwargs: Additional keyword arguments to update default plotting parameters.

    Returns:
        fig (go.Figure): The Plotly Figure object representing the stacked bar chart with subplots for each category.
    """

    params = general_kwargs()
    params.update(kwargs)

    xaxis_title = params["xaxis_title"]
    yaxis_title = params["yaxis_title"]
    zaxis_title = params["zaxis_title"]
    col_hover = params['col_hover']

    n_rows=2
    fig = make_subplots(
        rows = n_rows,                           # number of rows
        cols = 1,                           # number of columns
        vertical_spacing = params["vertical_spacing"],
        horizontal_spacing = params["horizontal_spacing"],     # space between subplots
        shared_xaxes=params["shared_xaxes"],
        shared_yaxes=params["shared_yaxes"]
    )

    categories = df[col_cat].unique()
    for cat in categories:
        current_df = df[df[col_cat] == cat]


        hovertemplate="<br><b>"+xaxis_title+"</b> :"+current_df[col_x].astype(str)+"<br><b>"+yaxis_title+"</b> - "+current_df[col_y].astype(str)+"<br><b>"+zaxis_title+"</b> : "+current_df[col_z].astype(str)
        # hovertemplate='<b>Categorie : </b>'+str(cat)+'<br><b>Date : </b>'+ current_df[col_x].astype(str) + '<br><b>'+y1_axis_title+'</b> : '+ current_df[col_metric1].astype(str)+' ('+current_df["per_"+col_metric1].map("{:.1%}".format).astype(str)+')' +'<br><b>'+y2_axis_title+'</b> : '+ current_df[col_metric2].astype(int).astype(str)+' ('+current_df["per_"+col_metric2].map("{:.1%}".format).astype(str)+')'
        for c in col_hover:
            hovertemplate += (
                "<br><b>"
                + str(c)
                + "</b>:"
                + current_df[c].astype(str).apply(wrap_text)
            )

        fig.add_trace(
            go.Bar(
                x=current_df[col_x], 
                y=current_df[col_y],
                orientation=params["orientation"],
                name=cat, 
                marker=dict(color=current_df[col_color]),
                hovertemplate=hovertemplate+'<extra></extra>',
                textfont_size=14,
                legendgroup=cat
                ),
            row=1,
            col=1,
        )

        fig.add_trace(
            go.Bar(
                
                x=current_df[col_x], 
                y=current_df[col_z],
                orientation=params["orientation"],
                name="",
                marker=dict(color=current_df[col_color]),
                hovertemplate=hovertemplate+'<extra></extra>',
                showlegend = False,
                legendgroup=cat
                ),
            row=2,
            col=1,
        )

    fig.update_layout(
            barmode='stack',
            title_text=params["title_text"], 
            showlegend = params["showlegend"],
            width = params["width"],
            height= params["height"]*n_rows,
            font_family=params["font_family"],
            font_size=params["font_size"],
            template=params["template"],
            plot_bgcolor=params["plot_bgcolor"],  # background color (plot)
            paper_bgcolor=params["paper_bgcolor"],  # background color (around plot)
            uniformtext_minsize=params["uniformtext_minsize"],
            uniformtext_mode=params["uniformtext_mode"],
            legend_tracegroupgap=0
        )
    
    fig.update_yaxes(
        title_font_size=params["yaxis_title_font_size"],
        tickangle=params["yaxis_tickangle"],
        tickfont_size=params["yaxis_tickfont_size"],
        range=params["yaxis_range"],
        showgrid=params["yaxis_showgrid"],
        showline=params["yaxis_showline"],
        zeroline=params["yaxis_zeroline"],
        gridwidth=params["yaxis_gridwidth"],
        gridcolor=params["yaxis_gridcolor"],
        linewidth=params["yaxis_linewidth"],
        linecolor=params["yaxis_linecolor"],
        mirror=params["yaxis_mirror"],
    )

    fig.update_xaxes(
        title_font_size=params["xaxis_title_font_size"],
        tickangle=params["xaxis_tickangle"],
        tickfont_size=params["xaxis_tickfont_size"],
        range=params["xaxis_range"],
        showgrid=params["xaxis_showgrid"],
        showline=params["xaxis_showline"],
        zeroline=params["xaxis_zeroline"],
        gridwidth=params["xaxis_gridwidth"],
        gridcolor=params["xaxis_gridcolor"],
        linewidth=params["xaxis_linewidth"],
        linecolor=params["xaxis_linecolor"],
        mirror=params["xaxis_mirror"],
    )

    fig.update_xaxes(showticklabels = False, row=1,col=1)
    fig.update_xaxes(title_text=params["xaxis_title"], row=2,col=1)
    fig.update_yaxes(title_text=params["yaxis_title"], row=1,col=1)
    fig.update_yaxes(title_text=params["zaxis_title"], row=2,col=1)

    return fig

def boxplot(df : pd.DataFrame, col_y : str = "degrees" , **kwargs) -> go.Figure:
    """
    Generates a box plot using Plotly Express with customization options.

    Args:
        df (pd.DataFrame): The DataFrame containing the data to plot.
        col_y (str, optional): The column name in the DataFrame to plot on the y-axis. Default is "degrees".
        **kwargs: Additional keyword arguments to update default plotting parameters.

    Returns:
        fig (go.Figure): The Plotly Figure object for the box plot.
    """
    params = general_kwargs()
    params.update(kwargs)
    col_hover = params["col_hover"]


    hovertemplate = "<b>"+str(col_y) +"</b> : "+df[col_y].astype(str)+"<br>"
    for c in col_hover:
        hovertemplate += (
            "<br><b>" + str(c) + "</b>:" + df[c].astype(str).apply(wrap_text)
        )

    # Box plot using Plotly Express
    fig = go.Figure(
        go.Box(
            y=df[col_y],
            name=params["yaxis_title"],
            orientation = params["orientation"],
            hovertemplate = hovertemplate+"<extra></extra>",
            marker_color = params["marker_color"],
            marker_size = params["marker_size"],
            marker_opacity = params["marker_opacity"],
            marker_symbol =  params["marker_symbol"],
            marker_line_width =  params["marker_line_width"],
            marker_line_color =  params["marker_color"],
        )
    )
    # fig = px.box(df, 
    #              y = col_y)

    # Customize the plot (optional)
    fig.update_layout(
        title_text=params["title_text"],
        width=params["width"],
        height=params["height"],
        font_family=params["font_family"],
        font_size=params["font_size"],
        template=params["template"],
        plot_bgcolor=params["plot_bgcolor"],  # background color (plot)
        paper_bgcolor=params["paper_bgcolor"],  # background color (around plot)
        showlegend=params["showlegend"],
        uniformtext_minsize=params["uniformtext_minsize"],
        uniformtext_mode=params["uniformtext_mode"],
    )
    fig.update_yaxes(
        title=params["yaxis_title"],
        title_font_size=params["yaxis_title_font_size"],
        tickangle=params["yaxis_tickangle"],
        tickfont_size=params["yaxis_tickfont_size"],
        range=params["yaxis_range"],
        showgrid=params["yaxis_showgrid"],
        showline=params["yaxis_showline"],
        zeroline=params["yaxis_zeroline"],
        gridwidth=params["yaxis_gridwidth"],
        gridcolor=params["yaxis_gridcolor"],
        linewidth=params["yaxis_linewidth"],
        linecolor=params["yaxis_linecolor"],
        mirror=params["yaxis_mirror"],
    )

    fig.update_xaxes(
        title=params["xaxis_title"],
        title_font_size=params["xaxis_title_font_size"],
        tickangle=params["xaxis_tickangle"],
        tickfont_size=params["xaxis_tickfont_size"],
        range=params["xaxis_range"],
        showgrid=params["xaxis_showgrid"],
        showline=params["xaxis_showline"],
        zeroline=params["xaxis_zeroline"],
        gridwidth=params["xaxis_gridwidth"],
        gridcolor=params["xaxis_gridcolor"],
        linewidth=params["xaxis_linewidth"],
        linecolor=params["xaxis_linecolor"],
        mirror=params["xaxis_mirror"],
    )
    return fig

def subplots_bar_per_day_per_cat(df: pd.DataFrame, 
                                 col_date: str, 
                                 col_cat: str, 
                                 metrics: list, 
                                 col_color: str, 
                                 **kwargs) -> go.Figure:
    """
    Creates subplots of stacked bar charts per day and category using Plotly.

    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        col_date (str): The name of the column representing dates.
        col_cat (str): The name of the column representing categories.
        metrics (List[str]): A list of column names representing metrics to be plotted.
        col_color (str): The name of the column representing colors for bars.
        y_axis_titles (List[str]): A list of titles for the y-axes of subplots. 
        **kwargs: Additional keyword arguments to update default plotting parameters.

    Returns:
        fig (go.Figure): The Plotly Figure object representing the subplots of stacked bar charts.
    """
    params = general_kwargs()
    params.update(kwargs)

    fig = make_subplots(
        rows = len(metrics),                           # number of rows
        cols = 1,                           # number of columns
        vertical_spacing = params["vertical_spacing"],     # space between subplots
        horizontal_spacing = params["horizontal_spacing"],     # space between subplots
        shared_xaxes = params["shared_xaxes"],
        shared_yaxes = params["shared_yaxes"]
    )

    categories = df[col_cat].unique()
    for cat in categories:
        current_df = df[df[col_cat] == cat]
    
        hovertemplate='<b>Categorie : </b>'+str(cat)+'<br><b>Date : </b>'+ current_df[col_date].astype(str)

        for i, metric in enumerate(metrics):
            hovertemplate +=  '<br><b>'+ metric + " : "+current_df[metric].astype(str) 
            if i==0:
                showlegend = True
            else:
                showlegend = False

            fig.add_trace(
                go.Bar(
                    x=current_df[col_date], 
                    y=current_df[metric],
                    orientation='v',
                    name=cat, 
                    marker=dict(color=current_df[col_color]),
                    hovertemplate=hovertemplate+'<extra></extra>',
                    textfont_size=14,
                    showlegend = showlegend,
                    legendgroup=cat
                    ),
                row = i+1,
                col=1,
            )

    fig.update_layout(
            barmode='stack',
            title_text=params["title_text"],  # graph title
            width=params["width"],  # plot size
            height=params["height"]  * len(metrics), # plot size
            showlegend = params["showlegend"],
            template=params["template"],
            plot_bgcolor=params["plot_bgcolor"],  # background color (plot)
            paper_bgcolor=params["paper_bgcolor"],  # background color (around plot)
            font_family=params["font_family"],  # font
            font_size=params["font_size"],
            uniformtext_minsize=params["uniformtext_minsize"],
            uniformtext_mode=params["uniformtext_mode"],
            legend_tracegroupgap=0,
            xaxis_tickangle=params["xaxis_tickangle"],
            xaxis_title_font_size=params["xaxis_title_font_size"],
            xaxis_tickfont_size=params["xaxis_tickfont_size"],
            xaxis_showgrid=params["xaxis_showgrid"],
            xaxis_showline=params["xaxis_showline"],
            xaxis_zeroline=params["xaxis_zeroline"],
            xaxis_gridwidth=params["xaxis_gridwidth"],
            xaxis_gridcolor=params["xaxis_gridcolor"],
            xaxis_linewidth=params["xaxis_linewidth"],
            xaxis_linecolor=params["xaxis_linecolor"],
            xaxis_mirror=params["xaxis_mirror"],
            yaxis_title_font_size=params["yaxis_title_font_size"],
            yaxis_tickangle=params["yaxis_tickangle"],
            yaxis_tickfont_size=params["yaxis_tickfont_size"],
            yaxis_showgrid=params["yaxis_showgrid"],
            yaxis_showline=params["yaxis_showline"],
            yaxis_zeroline=params["yaxis_zeroline"],
            yaxis_gridwidth=params["yaxis_gridwidth"],
            yaxis_gridcolor=params["yaxis_gridcolor"],
            yaxis_linewidth=params["yaxis_linewidth"],
            yaxis_linecolor=params["yaxis_linecolor"],
            yaxis_mirror=params["yaxis_mirror"],

        )

    for i, title in enumerate(metrics):
        fig.update_xaxes(title_text=params["xaxis_title"], row=i+1,col=1)

        fig.update_yaxes(title_text=title, row=i+1,col=1)

    return fig

def add_shape(fig: go.Figure, 
              shape_type: str = "rect", 
              x0: float = -1, 
              y0: float = -1, 
              x1: float = 0, 
              y1: float = 0, 
              fillcolor: str = 'Silver', 
              opacity: float = 0.1, 
              line_width: float = 0, 
              line_color: str = 'white', 
              dash: str = None, 
              layer: str = "below") -> go.Figure:
    """
    Adds a shape to a Plotly figure.

    Args:
        fig (go.Figure): The Plotly Figure object.
        shape_type (str, optional): The type of shape to add. Defaults to "rect".
        x0 (float, optional): The x-coordinate of the lower left corner of the shape. Defaults to -1.
        y0 (float, optional): The y-coordinate of the lower left corner of the shape. Defaults to -1.
        x1 (float, optional): The x-coordinate of the upper right corner of the shape. Defaults to 0.
        y1 (float, optional): The y-coordinate of the upper right corner of the shape. Defaults to 0.
        fillcolor (str, optional): The fill color of the shape. Defaults to 'Silver'.
        opacity (float, optional): The opacity of the shape. Defaults to 0.1.
        line_width (float, optional): The width of the shape's outline. Defaults to 0.
        line_color (str, optional): The color of the shape's outline. Defaults to 'white'.
        dash (str, optional): The dash style of the shape's outline. Defaults to None.
        layer (str, optional): The layer on which the shape is added, either 'below' or 'above' the data. Defaults to "below".

    Returns:
        fig (go.Figure): The modified Plotly Figure object with the added shape.
    """
    fig.add_shape(
            # Shape for the area between (-1, 0)
            {
                'type': shape_type,
                'x0': x0,
                'y0': y0,
                'x1': x1,
                'y1': y1,
                'fillcolor': fillcolor,
                'opacity': opacity,
                "layer": layer,
                'line': {
                    'width': line_width, 
                    "color": line_color,
                    "dash" : dash,
                    },
                
            }
        )
    return fig

def add_image(fig: go.Figure, 
              xref: str = "paper", 
              yref: str = "paper", 
              x: float = 0, 
              y: float = 0, 
              sizex: float = 0.08, 
              sizey: float = 0.08, 
              xanchor: str = "right", 
              yanchor: str = "bottom", 
              source: str = "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDc1IiBoZWlnaHQ9IjM4OCIgdmlld0JveD0iMCAwIDQ3NSAzODgiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xMDUuNzI3IDI5My4zOTFDMTA1LjcyNyAyNjYuNzc0IDg0LjEyOTMgMjQ1LjE3NyA1Ny42MDEzIDI0NS4xNzdDMzAuOTg0IDI0NS4xNzcgOS4yOTYgMjY2Ljc3NCA5LjI5NiAyOTMuMzkxQzkuMjk2IDMyMC4wMDkgMzAuOTg0IDM0MS42MDcgNTcuNjAxMyAzNDEuNjA3Qzg0LjEyOTMgMzQxLjYwNyAxMDUuNzI3IDMyMC4wMDkgMTA1LjcyNyAyOTMuMzkxWk0wLjg3MDY2NyAyOTMuMzkxQzAuODcwNjY3IDI2Mi4yMDMgMjYuMzI0IDIzNi43NTMgNTcuNjAxMyAyMzYuNzUzQzg4LjY5ODcgMjM2Ljc1MyAxMTQuMTUxIDI2Mi4yMDMgMTE0LjE1MSAyOTMuMzkxQzExNC4xNTEgMzI0LjU3OSA4OC42OTg3IDM1MC4wMyA1Ny42MDEzIDM1MC4wM0MyNi4zMjQgMzUwLjAzIDAuODcwNjY3IDMyNC41NzkgMC44NzA2NjcgMjkzLjM5MVoiIGZpbGw9ImJsYWNrIi8+CjxwYXRoIGQ9Ik0yMzIuNTMxIDI5My40ODFDMjMyLjUzMSAyNjMuNjM3IDIwOS4zMTkgMjQ1LjI2NSAxODYuMjg2IDI0NS4yNjVDMTY2LjU3IDI0NS4yNjUgMTQ3LjQ4MiAyNTguNjIgMTQ1LjI0MSAyODAuMDM4VjMwNi42NTZDMTQ3LjM5MyAzMjguOTcgMTY2LjM5MSAzNDEuNjk2IDE4Ni4yODYgMzQxLjY5NkMyMDkuMzE5IDM0MS42OTYgMjMyLjUzMSAzMjMuMzI1IDIzMi41MzEgMjkzLjQ4MVpNMjQwLjg2NiAyOTMuNDgxQzI0MC44NjYgMzI4LjA3NCAyMTQuNjk3IDM1MC4xMiAxODcuMTgzIDM1MC4xMkMxNjkuOTc3IDM1MC4xMiAxNTMuNTc1IDM0Mi4zMjQgMTQ1LjI0MSAzMjcuNjI1VjM4Ny40OTNIMTM2Ljk5N1YyMzkuNjJIMTQ0Ljg4M0wxNDUuMjQxIDI1Ny41NDRWMjYwLjE0MkMxNTMuNjY2IDI0NS42MjQgMTcwLjE1NSAyMzYuODQyIDE4Ny4yNzMgMjM2Ljg0MkMyMTQuNjA3IDIzNi44NDIgMjQwLjg2NiAyNTguODg4IDI0MC44NjYgMjkzLjQ4MVoiIGZpbGw9ImJsYWNrIi8+CjxwYXRoIGQ9Ik0yNTUuNjQyIDMyOC40MzNMMjYwLjc1MSAzMjIuNzg4QzI2OC4xMDEgMzM1LjUxMyAyODEuMDk1IDM0MS45NjUgMjk0LjE3OCAzNDEuOTY1QzMwOC41MTggMzQxLjk2NSAzMjMuMTI2IDMzMy42MyAzMjMuMTI2IDMxOS41NjFDMzIzLjEyNiAzMDUuNDkgMzA0LjkzNCAyOTkuNjY1IDI4OS43ODcgMjkzLjc0OUMyODAuMzc4IDI4OS45ODYgMjYwLjc1MSAyODMuMzUzIDI2MC43NTEgMjY0LjYyNEMyNjAuNzUxIDI0OS41NjggMjc0LjI4MyAyMzYuNjYyIDI5NC4yNjkgMjM2LjY2MkMzMDkuODYyIDIzNi42NjIgMzIzLjEyNiAyNDUuMzU0IDMyNy41MTggMjU2LjM3OEwzMjEuNjAzIDI2MS4wMzhDMzE2LjMxNSAyNDkuODM3IDMwNC4yMTcgMjQ0LjkwNiAyOTQuMDAxIDI0NC45MDZDMjc5LjEyMiAyNDQuOTA2IDI2OS4xNzQgMjU0LjEzNyAyNjkuMTc0IDI2NC4yNjVDMjY5LjE3NCAyNzcuNDQgMjg0LjIzMSAyODIuOTA1IDI5OS4xMDkgMjg4LjU1MkMzMTEuMDI3IDI5My4yMTIgMzMxLjU1MSAzMDAuNjUgMzMxLjU1MSAzMTkuMDIyQzMzMS41NTEgMzM4LjExMiAzMTMuMjY5IDM1MC4yMSAyOTQuMDAxIDM1MC4yMUMyNzYuNzAzIDM1MC4yMSAyNjEuODI3IDM0MC40NDIgMjU1LjY0MiAzMjguNDMzWiIgZmlsbD0iYmxhY2siLz4KPHBhdGggZD0iTTM0Ni43OCAyOTMuMzkxQzM0Ni43OCAyNTguNTMgMzc1LjAxMSAyMzYuMDM0IDQwMy4yNDEgMjM2LjAzNEM0MTUuNzg4IDIzNi4wMzQgNDMwLjMwNyAyNDAuNTE3IDQzOS45ODUgMjQ4LjU4Mkw0MzUuMzI1IDI1NS40ODJDNDI4Ljc4MyAyNDkuMjk5IDQxNS41MiAyNDQuNDU5IDQwMy4zMzEgMjQ0LjQ1OUMzNzkuMTMzIDI0NC40NTkgMzU1LjIwNCAyNjMuNDU5IDM1NS4yMDQgMjkzLjM5MUMzNTUuMjA0IDMyMy41OTMgMzc5LjQwMyAzNDIuMzIzIDQwMy4yNDEgMzQyLjMyM0M0MTUuNjA4IDM0Mi4zMjMgNDI5LjIzMSAzMzcuMTI2IDQzNi4yMjEgMzMwLjQ5NEw0NDEuMzI5IDMzNy4xMjZDNDMxLjQ3MiAzNDYuMTc4IDQxNi40MTYgMzUwLjc0OSA0MDMuNDIgMzUwLjc0OUMzNzUuMSAzNTAuNzQ5IDM0Ni43OCAzMjguNDMzIDM0Ni43OCAyOTMuMzkxWiIgZmlsbD0iYmxhY2siLz4KPHBhdGggZD0iTTQ2My42MzcgMjM5LjYxOUg0NzIuMDYxVjM0Ny4xNjNINDYzLjYzN1YyMzkuNjE5Wk00NjEuMTI4IDIxMi40NjRDNDYxLjEyOCAyMDguNzAxIDQ2NC4wODUgMjA1Ljc0MyA0NjcuODQ5IDIwNS43NDNDNDcxLjUyNCAyMDUuNzQzIDQ3NC41NzEgMjA4LjcwMSA0NzQuNTcxIDIxMi40NjRDNDc0LjU3MSAyMTYuMjI4IDQ3MS41MjQgMjE5LjE4NSA0NjcuODQ5IDIxOS4xODVDNDY0LjA4NSAyMTkuMTg1IDQ2MS4xMjggMjE2LjIyOCA0NjEuMTI4IDIxMi40NjRaIiBmaWxsPSJibGFjayIvPgo8cGF0aCBkPSJNMjE3Ljg1MyAzMS4zOTE0TDIzNy43MjEgNTEuMjU4TDI1Ny41ODggMzEuMzkxNEwyMzcuNzIxIDExLjUyNDdMMjE3Ljg1MyAzMS4zOTE0Wk0yMzcuNzIxIDYyLjU3MjdMMjA2LjU0IDMxLjM5MTRMMjM3LjcyMSAwLjIxMDAxNkwyNjguOTAxIDMxLjM5MTRMMjM3LjcyMSA2Mi41NzI3Wk0xNTQuMTAxIDU5Ljc1OTRMMTYxLjQzOSA4Ni45NjQ3TDE4OC42NiA3OS42MjJMMTgxLjMyMyA1Mi41OTU0TDE1NC4xMDEgNTkuNzU5NFpNMTU1Ljc5NyA5Ni43NzE0TDE0NC4yOCA1NC4wNzE0TDE4Ni45NjMgNDIuODM5NEwxOTguNDgxIDg1LjI1OEwxNTUuNzk3IDk2Ljc3MTRaTTI4Ni43ODEgNzkuNjIyTDMxNC4wMDMgODYuOTY0N0wzMjEuMzQxIDU5Ljc1OTRMMjk0LjEyIDUyLjU5NTRMMjg2Ljc4MSA3OS42MjJaTTMxOS42NDMgOTYuNzcxNEwyNzYuOTYxIDg1LjI1OEwyODguNDc5IDQyLjgzOTRMMzMxLjE2MiA1NC4wNzE0TDMxOS42NDMgOTYuNzcxNFpNMTU0LjEwMSAxNTYuMTY5TDE4MS4zMjMgMTYzLjMzM0wxODguNjYgMTM2LjMwN0wxNjEuNDM5IDEyOC45NjVMMTU0LjEwMSAxNTYuMTY5Wk0xODYuOTYzIDE3My4wODlMMTQ0LjI4IDE2MS44NTdMMTU1Ljc5NyAxMTkuMTU3TDE5OC40ODEgMTMwLjY3TDE4Ni45NjMgMTczLjA4OVpNMjg2Ljc3NSAxMzYuMzA5TDI5NC4xMiAxNjMuNTM3TDMyMS4zNDggMTU2LjE5M0wzMTQuMDAzIDEyOC45NjVMMjg2Ljc3NSAxMzYuMzA5Wk0yODguNDc5IDE3My4zNDVMMjc2Ljk2NyAxMzAuNjY5TDMxOS42NDMgMTE5LjE1N0wzMzEuMTU1IDE2MS44MzRMMjg4LjQ3OSAxNzMuMzQ1Wk0yMTcuODUzIDE4NC41MzdMMjM3LjcyMSAyMDQuNDA1TDI1Ny41ODggMTg0LjUzN0wyMzcuNzIxIDE2NC42N0wyMTcuODUzIDE4NC41MzdaTTIzNy43MjEgMjE1LjcxOEwyMDYuNTQgMTg0LjUzN0wyMzcuNzIxIDE1My4zNTdMMjY4LjkwMSAxODQuNTM3TDIzNy43MjEgMjE1LjcxOFoiIGZpbGw9ImJsYWNrIi8+Cjwvc3ZnPgo=") -> go.Figure:
    """
    Adds an image to a Plotly figure.

    Args:
        fig (go.Figure): The Plotly Figure object.
        xref (str, optional): The x-coordinate reference point. Defaults to "paper".
        yref (str, optional): The y-coordinate reference point. Defaults to "paper".
        x (float, optional): The x-coordinate of the image position. Defaults to 0.
        y (float, optional): The y-coordinate of the image position. Defaults to 0.
        sizex (float, optional): The size of the image in the x-direction. Defaults to 0.08.
        sizey (float, optional): The size of the image in the y-direction. Defaults to 0.08.
        xanchor (str, optional): The x-coordinate anchor point. Defaults to "right".
        yanchor (str, optional): The y-coordinate anchor point. Defaults to "bottom".
        source (str, optional): The URL source of the image. Defaults to "https://www.example.com/image.jpg".

    Returns:
        fig (go.Figure): The modified Plotly Figure object with the added image.
    """
    fig.add_layout_image(
    dict(
        source=source,
        xref=xref, 
        yref=yref,
        x=x, y=y,
        sizex=sizex, 
        sizey=sizey,
        xanchor=xanchor,
        yanchor=yanchor
        )
    )
    return fig

def add_horizontal_line(fig: go.Figure, 
                         y: float, 
                         line_color: str = "gray", 
                         line_width: float = 1.5, 
                         line_dash: str = "dash", 
                         annotation_text: str = "Longueur moyenne des textes", 
                         annotation_position: str = "top right") -> go.Figure:
    """
    Adds a horizontal line to a Plotly Figure object.

    Args:
        fig (go.Figure): The Plotly Figure object to which the horizontal line will be added.
        y (float): The y-coordinate of the horizontal line.
        line_color (str, optional): The color of the horizontal line. Defaults to "gray".
        line_width (float, optional): The width of the horizontal line. Defaults to 1.5.
        line_dash (str, optional): The dash style of the horizontal line. Defaults to "dash".
        annotation_text (str, optional): The text annotation associated with the horizontal line. Defaults to "Longueur moyenne des textes".
        annotation_position (str, optional): The position of the annotation relative to the horizontal line. Defaults to "top right".

    Returns:
        fig (go.Figure): The Plotly Figure object with the horizontal line added.
    """    
    fig.add_hline(
        y=y, 
        line_width=line_width, 
        line_dash=line_dash, 
        line_color=line_color,
        annotation_text=annotation_text, 
        annotation_position=annotation_position
        )
    return fig

def add_vertical_line(fig: go.Figure, 
                      x: float, 
                      line_color: str = "gray", 
                      line_width: float = 1.5, 
                      line_dash: str = "dash", 
                      annotation_text: str = "Longueur moyenne des textes", 
                      annotation_position: str = "top right") -> go.Figure:
    """
    Adds a vertical line to a Plotly Figure object.

    Args:
        fig (go.Figure): The Plotly Figure object to which the vertical line will be added.
        x (float): The x-coordinate of the vertical line.
        line_color (str, optional): The color of the vertical line. Defaults to "gray".
        line_width (float, optional): The width of the vertical line. Defaults to 1.5.
        line_dash (str, optional): The dash style of the vertical line. Defaults to "dash".
        annotation_text (str, optional): The text annotation associated with the vertical line. Defaults to "Longueur moyenne des textes".
        annotation_position (str, optional): The position of the annotation relative to the vertical line. Defaults to "top right".

    Returns:
        fig (go.Figure): The Plotly Figure object with the vertical line added.
    """
    fig.add_vline(
        x=x, 
        line_width=line_width, 
        line_dash=line_dash, 
        line_color=line_color,
        annotation_text=annotation_text, 
        annotation_position=annotation_position
        )
    return fig

def upload_chart_studio(
    username: str, 
    api_key: str, 
    fig, 
    title: str
) -> tuple:
    """
    Upload a Plotly visualization to Chart Studio.

    Args:
        username (str): The Chart Studio username.
        api_key (str): The Chart Studio API key.
        fig: The Plotly figure object to be uploaded.
        title (str): The title for the uploaded visualization.

    Returns:
        tuple: A tuple containing the URL of the uploaded visualization and the embed code.
    """
    URL = ""
    EMBED = ""

    try:
        # Set Chart Studio credentials
        tls.set_credentials_file(username=username, api_key=api_key)
        
        # Upload the figure to Chart Studio
        URL = py.plot(fig, filename=title, auto_open=True)
        
        # Get the embed code for the uploaded figure
        EMBED = tls.get_embed(URL)
        
        # Print the URL and embed code
        print("* URL DE LA VIZ >> ", URL)
        print("\n*CODE EMBED A COLLER \n", EMBED)
        
    except Exception as e:
        # Print the exception message and a suggestion to reduce the visualization size
        print(e, "try to reduce the dataviz size by printing less data")

    return URL, EMBED

def scale_to_0_10(x: pd.Series) -> pd.Series:
    """
    Scale a pandas Series to the range [0, 10].

    Args:
        x (pd.Series): The input pandas Series to be scaled.

    Returns:
        pd.Series: The scaled pandas Series with values in the range [0, 10].
    """
    return ((x - x.min()) / (x.max() - x.min()) * 10).astype(int)

def normalize_data_size(df: pd.DataFrame, col: str, coef: int = 20, constant: int = 5) -> pd.DataFrame:
    """
    Normalize the sizes of dots based on a specified column in a DataFrame.

    Args:
        df (pd.DataFrame): The input DataFrame.
        col (str): The column name to be normalized.
        coef (int, optional): The coefficient to scale the normalized values. Defaults to 20.
        constant (int, optional): The constant to add to the scaled normalized values. Defaults to 5.

    Returns:
        pd.DataFrame: The DataFrame with an additional column for the normalized sizes.
    """
    df['normalized_' + col] = ((df[col] - df[col].max()) / (df[col] + df[col].max()) + 1) * coef + constant
    return df

def generate_color_palette(lst: list, transparency: float = 1) -> dict:
    """
    Generate a random color palette of RGBA codes.

    Args:
        lst (List[str]): List of color names or identifiers.
        transparency (float, optional): Transparency value for RGBA colors (0 to 1). Defaults to 1.

    Returns:
        dict: Dictionary containing color names or identifiers as keys and corresponding RGBA codes as values.
    """
    color_palette = {
        color: 'rgba({}, {}, {}, {})'.format(
            random.randrange(0, 255),
            random.randrange(0, 255),
            random.randrange(0, 255),
            transparency
        )
        for color in lst
    }
    return color_palette

def generate_color_palette_with_colormap(lst: list, colormap: str = "viridis") -> dict:
    """
    Generate a color palette with hexadecimal codes using a specified colormap.

    Args:
        lst (List[str]): List of color names or identifiers.
        colormap (str, optional): Name of the colormap to use. Defaults to "viridis".

    Returns:
        Dict[str, str]: Dictionary containing color names or identifiers as keys and corresponding hexadecimal codes as values.
    """
    num_colors = len(lst)

    # Generate example data
    data = np.linspace(0, 1, num_colors)

    # Choose the colormap
    cmap = plt.get_cmap(colormap, num_colors)

    # Normalize the data
    norm = plt.Normalize(0, 1)

    # Interpolate colors
    colors = cmap(norm(data))

    # Convert colors to hexadecimal codes
    hex_colors = {item: to_hex(colors[i]) for i, item in enumerate(lst)}

    return hex_colors

def generate_hexadecimal_color_palette(lst: list, add_transparency: bool = False, transparency: float = 0.5) -> dict:
    """
    Generate a random color palette with hexadecimal codes and optional transparency.

    Args:
        lst (List[str]): List of color names or identifiers.
        add_transparency (bool, optional): Whether to add transparency to the colors. Defaults to False.
        transparency (float, optional): Transparency value for the colors (0 to 1). Defaults to 0.5.

    Returns:
        Dict[str, str]: Dictionary containing color names or identifiers as keys and corresponding hexadecimal codes as values.
    """
    if add_transparency:
        alpha_hex = int(transparency * 255)  # Convert transparency to integer (0-255 range)
        color_palette = {
            color: "#{:02x}{:02x}{:02x}{:02x}".format(
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
                alpha_hex
            )
            for color in lst
        }
    else:
        color_palette = {
            color: "#{:02x}{:02x}{:02x}".format(
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255)
            )
            for color in lst
        }
    return color_palette

def generate_random_hexadecimal_color() -> str:
    """
    Generate a random hexadecimal color code.

    Returns:
        str: Hexadecimal color code.
    """
    return "#{:02x}{:02x}{:02x}".format(
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255)
    )

def wrap_text(txt: str, length: int = 50) -> str:
    """
    Wrap text to a specified length.

    Args:
        txt (str): The text to wrap.
        length (int, optional): The maximum length of each line. Defaults to 50.

    Returns:
        str: The wrapped text.
    """
    txt = '<br>'.join(textwrap.wrap(str(txt), width=length))
    return txt

def format_number(number: float, digits=1) -> str:
    """
    Format a number into a human-readable string with K, M, or B suffixes.

    Args:
        number (float): The number to format.

    Returns:
        str: The formatted number as a string with an appropriate suffix.
    """

    if number <= 1:
        return f"{number * 100:.{digits}f}%"
    elif number < 1000:
        return str(number)
    elif number < 1000000:
        return f"{number / 1000:.{digits}f}K"
    elif number < 1000000000:
        return f"{number / 1000000:.{digits}f}M"
    else:
        return f"{number / 1000000000:.{digits}f}B"

def format_input(input_data):
    """
    Format the input data depending on its type. If it's a string, wrap the text.
    If it's a number, format it with appropriate suffixes.

    Args:
        input_data (str or int): The input data to format.

    Returns:
        str: The formatted input data.
    """
    if isinstance(input_data, str):
        return wrap_text(input_data)
    elif isinstance(input_data, (int, float)):
        return format_number(input_data)
    else:
        raise ValueError("Unsupported data type. Please provide a string or a number.")

def get_convex_hull_coord(points: np.array, interpolate_curve: bool = True) -> tuple:
    """
    Calculate the coordinates of the convex hull for a set of points.

    Args:
        points (np.array): Array of points, where each row is [x, y].
        interpolate_curve (bool): Whether to interpolate the convex hull.

    Returns:
        tuple: Tuple containing interpolated x and y coordinates of the convex hull.
    """
    # Calculate the convex hull of the points
    hull = ConvexHull(points)

    # Get the x and y coordinates of the convex hull vertices
    x_hull = np.append(points[hull.vertices, 0], points[hull.vertices, 0][0])
    y_hull = np.append(points[hull.vertices, 1], points[hull.vertices, 1][0])

    if interpolate_curve:
        # Calculate distances between consecutive points on the convex hull
        dist = np.sqrt(
            (x_hull[:-1] - x_hull[1:]) ** 2 + (y_hull[:-1] - y_hull[1:]) ** 2
        )

        # Calculate the cumulative distance along the convex hull
        dist_along = np.concatenate(([0], dist.cumsum()))

        # Use spline interpolation to generate interpolated points
        spline, u = interpolate.splprep([x_hull, y_hull], u=dist_along, s=0, per=1)
        interp_d = np.linspace(dist_along[0], dist_along[-1], 50)
        interp_x, interp_y = interpolate.splev(interp_d, spline)
    else:
        # If interpolation is not needed, use the original convex hull points
        interp_x = x_hull
        interp_y = y_hull

    return interp_x, interp_y


def add_annotations(fig: go.Figure, df: pd.DataFrame, col_x: str, col_y: str, col_txt: str, width: int = 1000, label_size_ratio: int = 100, bordercolor: str = "#C7C7C7", arrowcolor: str = "SlateGray", bgcolor: str = "#FFFFFF", font_color: str = "SlateGray") -> go.Figure:
    """
    Add annotations to a Plotly figure.

    Args:
        fig (go.Figure): Plotly figure object.
        df (pd.DataFrame): DataFrame containing annotation data.
        col_x (str): Name of the column containing X values.
        col_y (str): Name of the column containing Y values.
        col_txt (str): Name of the column containing text for annotations.
        width (int, optional): Width of the figure. Defaults to 1000.
        label_size_ratio (int, optional): Ratio of label size to figure width. Defaults to 100.
        bordercolor (str, optional): Color of annotation borders. Defaults to "#C7C7C7".
        arrowcolor (str, optional): Color of annotation arrows. Defaults to "SlateGray".
        bgcolor (str, optional): Background color of annotations. Defaults to "#FFFFFF".
        font_color (str, optional): Color of annotation text. Defaults to "SlateGray".

    Returns:
        go.Figure: Plotly figure object with annotations added.
    """
    df[col_txt] = df[col_txt].fillna("").astype(str)

    for i, row in df.iterrows():
        fig.add_annotation(
            x=row[col_x],
            y=row[col_y],
            text='<b>'+wrap_text(row[col_txt])+'</b>',
            showarrow=True,
            arrowhead=1,
            font=dict(
                family="Inria Sans",
                size=width / label_size_ratio,
                color=font_color
            ),
            bordercolor=bordercolor,
            borderwidth=width / 1000,
            borderpad=width / 500,
            bgcolor=bgcolor,
            opacity=1,
            arrowcolor=arrowcolor
        )

    return fig

def hex_to_rgb(hex_color: str) -> tuple:
    """
    Convert a hex color string to an RGB tuple.
    
    Args:
        hex_color (str): The hex color string (e.g., '#RRGGBB').
    
    Returns:
        tuple: A tuple containing the RGB values (r, g, b).
    """
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb: tuple) -> str:
    """
    Convert an RGB tuple to a hex color string.
    
    Args:
        rgb (tuple): A tuple containing the RGB values (r, g, b).
    
    Returns:
        str: The hex color string (e.g., '#RRGGBB').
    """
    return '#{:02x}{:02x}{:02x}'.format(*rgb)

def rgb_to_hsl(r: int, g: int, b: int) -> tuple:
    """
    Convert RGB values to HSL values.
    
    Args:
        r (int): The red component (0-255).
        g (int): The green component (0-255).
        b (int): The blue component (0-255).
    
    Returns:
        tuple: A tuple containing the HSL values (h, s, l).
    """
    r /= 255.0
    g /= 255.0
    b /= 255.0
    max_c = max(r, g, b)
    min_c = min(r, g, b)
    l = (max_c + min_c) / 2.0
    if max_c == min_c:
        s = 0.0
        h = 0.0
    else:
        delta = max_c - min_c
        s = delta / (1 - abs(2 * l - 1))
        if max_c == r:
            h = ((g - b) / delta) % 6
        elif max_c == g:
            h = (b - r) / delta + 2
        else:
            h = (r - g) / delta + 4
        h *= 60
        if h < 0:
            h += 360
    return h, s, l

def hsl_to_rgb(h: float, s: float, l: float) -> tuple:
    """
    Convert HSL values to RGB values.
    
    Args:
        h (float): The hue component (0-360).
        s (float): The saturation component (0-1).
        l (float): The lightness component (0-1).
    
    Returns:
        tuple: A tuple containing the RGB values (r, g, b).
    """
    c = (1 - abs(2 * l - 1)) * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = l - c / 2
    if 0 <= h < 60:
        r, g, b = c, x, 0
    elif 60 <= h < 120:
        r, g, b = x, c, 0
    elif 120 <= h < 180:
        r, g, b = 0, c, x
    elif 180 <= h < 240:
        r, g, b = 0, x, c
    elif 240 <= h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    r = (r + m) * 255
    g = (g + m) * 255
    b = (b + m) * 255
    return int(r), int(g), int(b)

def adjust_saturation(hex_color: str, factor: float = 0.5) -> str:
    """
    Adjust the saturation of a hex color by a given factor.

    Args:
        hex_color (str): The hex color string (e.g., '#RRGGBB').
        factor (float): The factor by which to adjust the saturation.
                        Values less than 1 reduce saturation, values greater than 1 increase saturation.

    Returns:
        str: The new hex color string with adjusted saturation.
    """
    rgb = hex_to_rgb(hex_color)
    h, s, l = rgb_to_hsl(*rgb)
    s = max(0, min(1, s * factor))
    new_rgb = hsl_to_rgb(h, s, l)
    return rgb_to_hex(new_rgb)

def adjust_lightness(hex_color: str, factor: float = 1.0) -> str:
    """
    Adjust the lightness of a hex color by a given factor.
    
    Args:
        hex_color (str): The hex color string (e.g., '#RRGGBB').
        factor (float): The factor by which to adjust the lightness (default is 1.0).
    
    Returns:
        str: The new hex color string with adjusted lightness.
    """
    rgb = hex_to_rgb(hex_color)
    h, s, l = rgb_to_hsl(*rgb)
    l = max(0, min(1, l * factor))
    new_rgb = hsl_to_rgb(h, s, l)
    return rgb_to_hex(new_rgb)
# def create_scatter_plot(df: pd.DataFrame, col_x: str, col_y: str, col_category: str, color_palette: dict, col_color: str, col_size: str, col_text: str, col_legend: list = [], title: str = "Scatter Plot", x_axis_label: str = "X-axis", y_axis_label: str = "Y-axis", width: int = 1000, height: int = 1000, xaxis_range: list =None, yaxis_range: list =None, size_value: int = 4, opacity: float = 0.8, maxdisplayed: int = 0, mode: str = "markers", textposition: str = "bottom center", plot_bgcolor: str = None, paper_bgcolor: str = None, yaxis_showgrid: bool = False, xaxis_showgrid: bool = False, color: str = "indianred", line_width: float = 0.5, line_color: str = "white", colorscale: str = 'Viridis', showscale: bool = True, template: str = "plotly", font_size:int =16) -> go.Figure:
#     """
#     Create a scatter plot.

#     Args:
#         df (pd.DataFrame): DataFrame containing all data.
#         col_x (str): Name of the column containing X values.
#         col_y (str): Name of the column containing Y values.
#         col_category (str): Name of the column for colorization.
#         color_palette (dict): A dictionary mapping category with color value.
#         col_color (str): Name of the column for color. Only used for continuous scale.
#         col_size (str): Name of the column for dot sizes.
#         col_text (str): Name of the column containing text for legend on hover.
#         col_legend (List[str], optional): List of column names for legend. Defaults to [].
#         title (str, optional): Graph title. Defaults to "Scatter Plot".
#         x_axis_label (str, optional): Label for X-axis. Defaults to "X-axis".
#         y_axis_label (str, optional): Label for Y-axis. Defaults to "Y-axis".
#         width (int, optional): Size of the graph. Defaults to 1000.
#         height (int, optional): Size of the graph. Defaults to 1000.
#         xaxis_range (list, optional): Range values for X-axis. Defaults to None.
#         yaxis_range (list, optional): Range values for Y-axis. Defaults to None.
#         size_value (int, optional): Minimum size (or constant) for dots. Defaults to 4.
#         opacity (float, optional): Dots transparency. Defaults to 0.8.
#         maxdisplayed (int, optional): Maximum number of dots to display. 0 = infinite. Defaults to 0.
#         mode (str, optional): Mode for the scatter plot. Defaults to "markers".
#         textposition (str, optional): Text position for hover. Defaults to "bottom center".
#         plot_bgcolor (str, optional): Background color for plot. Defaults to None.
#         paper_bgcolor (str, optional): Background color for the area around the plot. Defaults to None.
#         yaxis_showgrid (bool, optional): Whether to show grid on Y-axis. Defaults to False.
#         xaxis_showgrid (bool, optional): Whether to show grid on X-axis. Defaults to False.
#         color (str, optional): Color code for dots if col_category is None. Defaults to "indianred".
#         line_width (float, optional): Width of dots contours. Defaults to 0.5.
#         line_color (str, optional): Color of dots contours. Defaults to "white".
#         colorscale (str, optional): Color scale for continuous color mapping. Defaults to 'Viridis'.
#         showscale (bool, optional): Whether to show color scale. Defaults to True.
#         template (str, optional): Plotly template. Defaults to "plotly".

#     Returns:
#         go.Figure: Plotly scatter plot figure.
#     """

#     if line_color is None :
#         line_color=color

#     fig = go.Figure()

#     #col_category is used to colorize dots
#     if col_category is not None:
#         for i, category in enumerate(df[col_category].unique()):
#             color = color_palette.get(category, 'rgb(0, 0, 0)')  # Default to black if category not found
            
#             #hovertemplate generation 
#             hovertemplate='<b>'+col_x+'</b>:'+df[df[col_category]==category][col_x].astype(str)+'<br><b>'+col_y+'</b>:'+df[df[col_category]==category][col_y].astype(str)+'<br><b>'+col_category+'</b>:'+str(category)
#             if col_size is None:
#                 size=size_value
#             else:
#                 size = df[df[col_category] == category][col_size]
#                 hovertemplate += '<br><b>'+col_size+'</b>:'+size.astype(str)

#             if len(col_legend)>0:
#                 for c in col_legend:
#                     hovertemplate +='<br><b>'+str(c)+'</b>:'+ df[df[col_category]==category][c].astype(str).apply(wrap_text)

#             fig.add_trace(
#                 go.Scatter(
#                     x=df[df[col_category]==category][col_x], 
#                     y=df[df[col_category]==category][col_y], 
#                     mode=mode, 
#                     text = df[df[col_category]==category][col_text],
#                     textposition=textposition,
#                     marker=dict(color=color,                 #dots color
#                                 size=size,                   #dots size
#                                 opacity=opacity,             #dots opacity
#                                 line_color=line_color,       #line color around dot
#                                 line_width=line_width,       #line width around dot
#                                 sizemode='area',
#                                 sizemin = size_value,        #minimum size of dot
#                                 maxdisplayed=maxdisplayed,   #max number of dots to display (0 = infinite)
#                                 symbol = "circle"            #type of dot
#                                 ), 
#                     name=category,                           # trace name
#                     hovertemplate=hovertemplate+"<extra></extra>"
#                     )
#                 )
#     # if there is no category for color, we create a simpler plot
#     else:
#         hovertemplate='<b>'+col_x+'</b>:'+df[col_x].astype(str)+'<br><b>'+col_y+'</b>:'+df[col_y].astype(str)
#         if col_size is None:
#             size=size_value
#         else:
#             size = df[col_size]
#             hovertemplate += '<br><b>'+col_size+'</b>:'+size.astype(str)
#         if col_color is not None :
#             hovertemplate +='<br><b>'+col_color+'</b>:'+df[col_color].astype(str)
#             color = df[col_color]
#         else :
#             if color is None:
#                 color = generate_random_hexadecimal_color()
#         if len(col_legend)>0:
#             for c in col_legend:
#                 hovertemplate +='<br><b>'+str(c)+'</b>:'+ df[c].astype(str).apply(wrap_text)

#         fig = go.Figure( go.Scatter(
#                     x=df[col_x], 
#                     y=df[col_y], 
#                     mode=mode, 
#                     text = df[col_text],
#                     textposition=textposition,
#                     marker=dict(color=color,                #dots color
#                                 size=size,                  #dots size
#                                 opacity=opacity,            #dots opacity
#                                 line_color=line_color,      #line color around dot
#                                 line_width=line_width,      #line width arount dot
#                                 sizemode='area',            # Scale marker sizes
#                                 sizemin = size_value,       #minimum size of dot
#                                 maxdisplayed=maxdisplayed,  #max number of dots to display (0 = infinite)
#                                 symbol = "circle",           #type of dot
#                                 colorscale=colorscale,
#                                 showscale=showscale
#                                 ), 
#                     name="",
#                     hovertemplate=hovertemplate+"<extra></extra>"
#                     ))

#     #we calculate X and Y axis ranges. 
#     if yaxis_range is None :
#         yaxis_range=[df[col_y].min()- 0.1,df[col_y].max() +  0.1]
#     if yaxis_range == "auto":
#         yaxis_range=None
    
#     if xaxis_range is None : 
#         xaxis_range = [df[col_x].min()- 0.1,df[col_x].max()+ 0.1]
#     if xaxis_range =="auto":
#         xaxis_range=None

#     # Update layout
#     fig.update_layout(
#         title=title,                  #graph title
#         xaxis_title=x_axis_label,     #xaxis title
#         yaxis_title=y_axis_label,     #yaxis title
#         width=width,                  #plot size
#         height=height,                #plot size
#         xaxis_showgrid=xaxis_showgrid,         #grid
#         yaxis_showgrid=yaxis_showgrid,         #grid
#         yaxis_range = yaxis_range,    #yaxis range
#         xaxis_range = xaxis_range,    #xaxis range
#         template=template,
#         plot_bgcolor=plot_bgcolor,    #background color (plot)
#         paper_bgcolor=paper_bgcolor,   #background color (around plot)
#         font_family="Inria Sans",           # font
#         font_size=font_size

#     )
#     return fig



# def scatter3D(df: pd.DataFrame, col_x: str, col_y: str, col_z: str, col_category: str, color_palette: dict, col_size: str, col_text: str, title: str = "3D Scatter Plot", x_axis_label: str = "X-axis", y_axis_label: str = "Y-axis", z_axis_label: str = "Z-axis", width: int = 1000, height: int = 1000, xaxis_range: list = None, yaxis_range: list = None, zaxis_range: list = None, size_value: int = 4, opacity: float = 0.8, plot_bgcolor: str = None, paper_bgcolor: str = None, color: str = "indianred", line_width: float = 0.5, line_color: str = "white", template: str = "plotly", font_size:int =16) -> go.Figure:
#     """
#     Create a 3D scatter plot.

#     Args:
#         df (pd.DataFrame): DataFrame containing all data.
#         col_x (str): Name of the column containing X values.
#         col_y (str): Name of the column containing Y values.
#         col_z (str): Name of the column containing Z values.
#         col_category (str): Name of the column for colorization.
#         color_palette (dict): A dictionary mapping categories with color values.
#         col_size (str): Name of the column for dot sizes.
#         col_text (str): Name of the column containing text for legend on hover.
#         title (str, optional): Graph title. Defaults to "3D Scatter Plot".
#         x_axis_label (str, optional): Label for X-axis. Defaults to "X-axis".
#         y_axis_label (str, optional): Label for Y-axis. Defaults to "Y-axis".
#         z_axis_label (str, optional): Label for Z-axis. Defaults to "Z-axis".
#         width (int, optional): Width of the graph. Defaults to 1000.
#         height (int, optional): Height of the graph. Defaults to 1000.
#         xaxis_range (list, optional): Range values for the X-axis. Defaults to None.
#         yaxis_range (list, optional): Range values for the Y-axis. Defaults to None.
#         zaxis_range (list, optional): Range values for the Z-axis. Defaults to None.
#         size_value (int, optional): Minimum size (or constant) for dots. Defaults to 4.
#         opacity (float, optional): Dots transparency. Defaults to 0.8.
#         plot_bgcolor (str, optional): Background color for the plot. Defaults to None.
#         paper_bgcolor (str, optional): Background color for the area around the plot. Defaults to None.
#         color (str, optional): Color code for dots if col_category is None. Defaults to "indianred".
#         line_width (float, optional): Width of dots contours. Defaults to 0.5.
#         line_color (str, optional): Color of dots contours. Defaults to "white".
#         template (str, optional): Plotly template. Defaults to "plotly".

#     Returns:
#         go.Figure: Plotly figure object.
#     """
#     fig=go.Figure()
#     if col_category is not None:
#         for i, category in enumerate(df[col_category].unique()):
#             color = color_palette.get(category, 'rgb(0, 0, 0)')  # Default to black if category not found

#             #hovertemplate generation 
#             hovertemplate='<b>X</b>:'+df[df[col_category]==category][col_x].astype(str)+'<br><b>Y</b>:'+df[df[col_category]==category][col_y].astype(str)+'<br><b>Z</b>:'+df[df[col_category]==category][col_z].astype(str)+'<br><b>'+col_category+'</b>:'+str(category)
#             if col_size is None:
#                 size=size_value
#             else:
#                 size = df[df[col_category] == category][col_size]
#                 hovertemplate += '<br><b>'+col_size+'</b>:'+size.astype(str)

#             if col_text is not None:
#                 hovertemplate +='<br><b>'+col_text+'</b>:'+ df[df[col_category]==category][col_text].apply(wrap_text)

#             fig.add_trace(
#                 go.Scatter3d(
#                     x=df[df[col_category]==category][col_x], 
#                     y=df[df[col_category]==category][col_y], 
#                     z=df[df[col_category]==category][col_z], 
#                     mode='markers', 
#                     marker=dict(color=color,                 #dots color
#                                 size=size,                   #dots size
#                                 opacity=opacity,             #dots opacity
#                                 line_color=line_color,          #line color around dot
#                                 line_width=line_width,              #line width around dot
#                                 sizemin = size_value,        #minimum size of dot
#                                 symbol = "circle"            #type of dot
#                                 ), 
#                     name=category,                           # trace name
#                     hovertemplate=hovertemplate+"<extra></extra>"
#                     )
#                 )
#     else:
#         #hovertemplate creation
#         hovertemplate='<b>X</b>:'+df[col_x].astype(str)+'<br><b>Y</b>:'+df[col_y].astype(str)+'<br><b>Z</b>:'+df[col_z].astype(str)
#         if col_size is None:
#             size=size_value
#         else:
#             size = df[col_size]
#             hovertemplate += '<br><b>'+col_size+'</b>:'+size.astype(str)
#         if col_text is not None:
#             hovertemplate +='<br><b>'+col_text+'</b>:'+ df[col_text].apply(wrap_text)

#         fig = go.Figure( go.Scatter3d(
#                     x=df[col_x], 
#                     y=df[col_y],
#                     z=df[col_z], 
#                     mode='markers', 
#                     marker=dict(color=color,                #dots color
#                                 size=size,                  #dots size
#                                 opacity=opacity,            #dots opacity
#                                 line_color=line_color,         #line color around dot
#                                 line_width=line_width,             #line width arount dot
#                                 sizemin = size_value,       #minimum size of dot
#                                 symbol = "circle"           #type of dot
#                                 ), 
#                     name="",
#                     hovertemplate=hovertemplate+"<extra></extra>"
#                     ))


#     #we calculate X and Y axis ranges. 
#     if yaxis_range is None :
#         yaxis_range=[df[col_y].min()-0.1,df[col_y].max()+0.1]
#     if xaxis_range is None : 
#         xaxis_range = [df[col_x].min()-0.1,df[col_x].max()+0.1]
#     if zaxis_range is None : 
#         zaxis_range = [df[col_z].min()-0.1,df[col_z].max()+0.1]
#     fig.update_layout(
        
#         font_family="Inria Sans",           # font
#         font_size = font_size,
#         title=title,                  #graph title
#         xaxis_title=x_axis_label,     #xaxis title
#         yaxis_title=y_axis_label,     #yaxis title
#         zaxis_title=z_axis_label,     #zaxis title
#         width=width,                  #plot size
#         height=height,                #plot size
#         xaxis_showline=False,         #intermediate lines
#         xaxis_showgrid=False,         #grid
#         xaxis_zeroline=False,         #zeroline
#         yaxis_showline=False,         #intermediate lines
#         yaxis_showgrid=False,         #grid
#         yaxis_zeroline=False,         #zeroline
#         zaxis_showline=False,         #intermediate lines
#         zaxis_showgrid=False,         #grid
#         zaxis_zeroline=False,         #zeroline
#         scene_yaxis_range = yaxis_range,    #yaxis range
#         scene_xaxis_range = xaxis_range,    #xaxis range
#         scene_zaxis_range = zaxis_range,    #zaxis range
#         scene_camera = dict(               #camera orientation at start
#             up=dict(x=1, y=0, z=2),        
#             center=dict(x=0, y=0, z=0),
#             eye=dict(x=2, y=1.25, z=0.5)
#         ),
#         template=template,
#         plot_bgcolor=plot_bgcolor,    #background color (plot)
#         paper_bgcolor=paper_bgcolor,   #background color (around plot)
#         margin=dict(
#                     t=width / 15,
#                     b=width / 25,
#                     r=width / 25,
#                     l=width / 25,
#                 ),
#         legend=dict(   
#             orientation="h",
#             yanchor="bottom",
#             y=-0.12,
#             xanchor="right",
#             x=1,
#             itemsizing= 'constant'
#         )
#     )

#     return fig
    

# def fig_bar_trend(df: pd.DataFrame, col_x: str, bar_measure: str, trend_measure: str, x_name: str = "X", bar_name: str = "metric1", trend_name: str = "metric2", marker_color: str = '#d399ff', line_color: str = '#bd66ff', title_text: str = "Couverture & Résonance", width: int = 1500, height: int = 700, xaxis_tickangle: int = 0, opacity: float = 0.8, plot_bgcolor: str = None, paper_bgcolor: str = None, template: str = "plotly", font_size:int =16) -> go.Figure:
#     """
#     Display a graph that combines bar and trend chart to compare 2 metrics.

#     Args:
#         df (pd.DataFrame): DataFrame containing all data.
#         col_x (str): Name of the column containing X values.
#         bar_measure (str): Data represented as bar diagram.
#         trend_measure (str): Data represented as trend line.
#         x_name (str, optional): Label for X-axis. Defaults to "X".
#         bar_name (str, optional): Label for the bar measure. Defaults to "metric1".
#         trend_name (str, optional): Label for the trend measure. Defaults to "metric2".
#         marker_color (str, optional): Color code for bars. Defaults to 'lightpink'.
#         line_color (str, optional): Color code for trend line. Defaults to 'indianred'.
#         title_text (str, optional): Graph title. Defaults to "Couverture & Résonance".
#         width (int, optional): Width of the graph. Defaults to 1500.
#         height (int, optional): Height of the graph. Defaults to 700.
#         xaxis_tickangle (int, optional): Angle for x ticks. Defaults to 0.
#         opacity (float, optional): Opacity of bars. Defaults to 0.8.
#         plot_bgcolor (str, optional): Background color for the plot. Defaults to None.
#         paper_bgcolor (str, optional): Background color for the area around the plot. Defaults to None.
#         template (str, optional): Plotly template. Defaults to "plotly".

#     Returns:
#         go.Figure: Plotly figure object.
#     """

#     # nk = np.empty(shape=(len(x), 3, 1), dtype="object")
#     # nk[:, 0] = np.array(x.apply(lambda txt: '<br>'.join(textwrap.wrap(str(txt), width=50)))).reshape(-1, 1)
#     # nk[:, 1] = np.array(bar_measure).reshape(-1, 1)
#     # nk[:, 2] = np.array(trend_measure).reshape(-1, 1)

#     fig = make_subplots(specs=[[{"secondary_y": True}]])

#     fig.add_trace(
#         go.Scatter(
#             x=df[col_x].apply(wrap_text), 
#             y=df[trend_measure], 
#             name=trend_name,
#             mode='lines', 
#             line_color=line_color, 
#             line_width=4,
#             textfont=dict(size=8),
#             # customdata=nk,
#             hovertemplate=("<br>"+x_name+" :"+df[col_x].astype(str)+"<br>"+bar_name+" - "+df[bar_measure].astype(str)+"<br>"+trend_name+" : "+df[trend_measure].astype(str)+"<extra></extra>"),
#         ),
#         secondary_y=True,
#     )
#     # Add traces
#     fig.add_trace(
#         go.Bar(
#             x=df[col_x].apply(wrap_text), 
#             y = df[bar_measure], 
#             name=bar_name, 
#             marker_color=marker_color, 
#             opacity=opacity,
#             # customdata=nk,
#             hovertemplate=("<br>"+x_name+" :"+df[col_x].astype(str)+"<br>"+bar_name+" - "+df[bar_measure].astype(str)+"<br>"+trend_name+" : "+df[trend_measure].astype(str)+"<extra></extra>"),
#         ),
#         secondary_y=False,

#     )
#     first_axis_range=[-0.5,df[bar_measure].max()*1.01]
#     secondary_axis_range=[-0.5,df[trend_measure].max()*1.01]

#     # Add figure title
#     fig.update_layout(
        
#         title_text=title_text, 
#         showlegend=True,
#         width = width,
#         height= height,
#         xaxis_tickangle=xaxis_tickangle,
#         xaxis_showline=False,
#         xaxis_showgrid=False,
#         yaxis_showline=False,
#         yaxis_showgrid=False,
#         font_family="Inria Sans",
#         font_size = font_size,
#         template=template,
#         plot_bgcolor=plot_bgcolor,    #background color (plot)
#         paper_bgcolor=paper_bgcolor,   #background color (around plot)
#         margin=dict(
#                     t=width / 15,
#                     b=width / 20,
#                     r=width / 20,
#                     l=width / 20,
#                 ),
#     )

#     # # Set x-axis title
#     fig.update_xaxes(title_text=x_name)

#     # Set y-axes titles
#     fig.update_yaxes(title_text=bar_name, range = first_axis_range, secondary_y=False)
#     fig.update_yaxes(title_text=trend_name, range = secondary_axis_range, secondary_y=True)  
    
#     return fig

def network_graph(T: nx.Graph, 
                  col_size: str = "scaled_size", 
                  col_color: str = "modularity_color",  
                  title_text: str = "Analyse de similitudes", 
                  sample_nodes: float = 0.15, 
                  show_edges: bool = True, 
                  show_halo: bool = False, 
                  textposition: str = None, 
                  line_color: str = "#B7B7B7", 
                  line_dash: str = "dot", 
                  edge_mode: str = "lines+markers", 
                  node_mode: str = "markers+text", 
                  opacity: float = 0.2, 
                  width: int = 1600, 
                  height: int = 1200, 
                  plot_bgcolor: str = None, 
                  paper_bgcolor: str = None, 
                  template: str = "plotly") -> go.Figure:
    """
    Creates a network graph visualization using Plotly.

    Args:
        T (nx.Graph): The NetworkX graph object.
        col_size (str, optional): The column name for node size. Defaults to "scaled_size".
        col_color (str, optional): The column name for node color. Defaults to "modularity_color".
        title_text (str, optional): The title for the graph. Defaults to "Analyse de similitudes".
        sample_nodes (float, optional): The proportion of nodes to sample for displaying labels. Defaults to 0.15.
        show_edges (bool, optional): Whether to display edges. Defaults to True.
        show_halo (bool, optional): Whether to display halo around nodes. Defaults to False.
        textposition (str, optional): The position of node labels. Defaults to None.
        line_color (str, optional): The color of edges. Defaults to "#B7B7B7".
        line_dash (str, optional): The dash style of edges. Defaults to "dot".
        edge_mode (str, optional): The mode for displaying edges. Defaults to "lines+markers".
        node_mode (str, optional): The mode for displaying nodes. Defaults to "markers+text".
        opacity (float, optional): The opacity of nodes. Defaults to 0.2.
        width (int, optional): The width of the plot. Defaults to 1600.
        height (int, optional): The height of the plot. Defaults to 1200.
        plot_bgcolor (str, optional): The background color of the plot area. Defaults to None.
        paper_bgcolor (str, optional): The background color of the paper area. Defaults to None.
        template (str, optional): The template of the plot. Defaults to "plotly".

    Returns:
        fig (go.Figure): The Plotly Figure object representing the network graph visualization.
    """    
    # on construit un dataframe des noeuds à partir des données du graphe pour plus de simplicité
    df_nodes=pd.DataFrame()
    for node in T.nodes(data=True):
        df_nodes_tmp=pd.json_normalize(node[1])
        df_nodes_tmp['node']=node[0]
        df_nodes=pd.concat([df_nodes, df_nodes_tmp])
    df_nodes[['x','y']]=df_nodes['pos'].apply(pd.Series)
    df_nodes = df_nodes.sort_values(by=col_size, ascending=False).reset_index(drop=True)

    # on conserve les labels pour seulement un échantillon de noeuds
    df_sample = sample_most_engaging_posts(df_nodes, "modularity", col_size, sample_size= sample_nodes, min_size=3)

    for index, row in df_nodes.iterrows():
        if row['node'] in df_sample['node'].values:
            df_nodes.at[index, 'node_label'] = row['node']
        else:
            df_nodes.at[index, 'node_label'] = ''
    
    fig = go.Figure()
    # on crée nos liens
    if show_edges:
        for edge in T.edges(data=True):
            x0, y0 = T.nodes[edge[0]]['pos']
            x1, y1 = T.nodes[edge[1]]['pos']

            fig.add_trace(
                go.Scatter(
                    x = tuple([x0, x1, None]),
                    y = tuple([y0, y1, None]),
                    line_width = edge[2]['scaled_weight'],
                    line_color = line_color,
                    mode=edge_mode,
                    line_dash=line_dash,
                    name="",
                    hoverinfo='skip',
                )
            )

    # on affiche éventuellement les halo
    if show_halo:
        for i, row in df_nodes.groupby("modularity"):
            try:
                x_hull, y_hull = get_convex_hull_coord(np.array(row[['x','y']]))
                hull_color = row[col_color].iloc[0]
                # Create a Scatter plot with the convex hull coordinates
                fig.add_trace( 
                    go.Scatter(
                        x=x_hull,
                        y=y_hull,
                        mode="lines",
                        fill="toself",
                        fillcolor=hull_color,
                        opacity=0.1,
                        name="Convex Hull",
                        line=dict(color="grey", dash="dot"),
                        hoverinfo="none",
                    )
                )
            except:
                pass

    # on affiche nos noeuds
    for i, row in df_nodes.iterrows():
        fig.add_trace(
            go.Scatter(
                x = [row['x']],
                y = [row['y']],
                mode=node_mode,
                marker_opacity=opacity,
                marker_size=row[col_size],
                marker_color= row[col_color],
                marker_sizemode='area',
                marker_sizemin = 8,
                textposition=textposition,
                text = row['node_label'],
                textfont_size=row[col_size],
                textfont_color=row[col_color],
                hovertemplate='<b>'+str(row['node'])+'</b><br>Modularity :'+str(row["modularity"])+'</b><br>Frequency :'+str(row["size"])+'</b><br>Eigenvector Centrality : '+str(round(row["eigenvector_centrality"],3))+'</b><br>Degree Centrality : '+str(round(row["degree_centrality"],3))+'</b><br>Betweenness Centrality : '+str(round(row["betweenness_centrality"],3))+"<extra></extra>"
            )
        )

    fig.update_layout(
            width=width,
            height=height,
            showlegend=False,
            hovermode='closest',
            title=title_text,
            titlefont_size=18,
            font_family="Inria Sans",
            # font_size = 12,
            # uniformtext_minsize=8,
            template=template,
            plot_bgcolor=plot_bgcolor,
            paper_bgcolor = paper_bgcolor,
            
            xaxis=dict(
                showgrid=False, 
                showline=False,                           #intermediate lines
                zeroline=False,
                showticklabels=False, 
                mirror=False
                ),
            yaxis=dict(
                showgrid=False, 
                showline=False,                           #intermediate lines
                zeroline=False,
                showticklabels=False, 
                mirror=False
                ))
    
    return fig

def richesse_lexicale(df: pd.DataFrame, 
                      title: str = "Richesse lexicale", 
                      width: int = 1200, 
                      height: int = 1000, 
                      template: str = "plotly",
                      font_size: int = 16) -> go.Figure:
    """
    Creates a lexical richness visualization using Plotly.

    Args:
        df (pd.DataFrame): The DataFrame containing word frequency data.
        title (str, optional): The title for the plot. Defaults to "Richesse lexicale".
        width (int, optional): The width of the plot. Defaults to 1200.
        height (int, optional): The height of the plot. Defaults to 1000.
        template (str, optional): The template of the plot. Defaults to "plotly".

    Returns:
        fig_richesse (go.Figure): The Plotly Figure object representing the lexical richness visualization.
    """
    df = create_frequency_table(df, "freq")
    fig_richesse = go.Figure()
    fig_richesse.add_trace(
            go.Scatter(
                x=df['rank'],
                y=df['freq'], 
                # marker_color=generate_random_hexadecimal_color(),
                mode='markers', 
                name="",
                hovertemplate = 'rank : '+df["rank"].astype(str)+'<br>'+'<b>word : '+df["word"].astype(str)+'</b><br>'+'count : '+df["freq"].astype(str)+'<br>')
            ) 
    fig_richesse.update_layout(title=title, 
                            xaxis_title="Rank", 
                            font_family="Inria Sans",
                            font_size = font_size,
                            width=width, 
                            height=height,
                            template=template)    
    fig_richesse.update_xaxes(tickformat=".0f", title_text="Rank", type="log")
    fig_richesse.update_yaxes(tickformat=".0f", title_text="Freq", type="log")
    return fig_richesse

def richesse_lexicale_per_topic(df: pd.DataFrame, 
                                col_topic: str, 
                                title: str = "Richesse lexicale par topic", 
                                width: int = 1200, 
                                height: int = 1000, 
                                template: str = "plotly",
                                font_size: int = 16) -> go.Figure:
    """
    Creates a lexical richness visualization per topic using Plotly.

    Args:
        df (pd.DataFrame): The DataFrame containing word frequency data.
        col_topic (str): The name of the column representing topics.
        title (str, optional): The title for the plot. Defaults to "Richesse lexicale par topic".
        width (int, optional): The width of the plot. Defaults to 1200.
        height (int, optional): The height of the plot. Defaults to 1000.
        template (str, optional): The template of the plot. Defaults to "plotly".

    Returns:
        fig_richesse (go.Figure): The Plotly Figure object representing the lexical richness visualization per topic.
    """
    fig_richesse = go.Figure()
    for topic in list(df[col_topic].unique()):
        df_tmp = create_frequency_table(df[df[col_topic]==topic], "freq")
        fig_richesse.add_trace(
                go.Scatter(
                    x=df_tmp['rank'],
                    y=df_tmp['freq'], 
                    # marker_color=generate_random_hexadecimal_color(),
                    mode='markers', 
                    name=topic,
                    hovertemplate = col_topic+ ' : '+ str(topic)+'<br> rank : '+df_tmp["rank"].astype(str)+'<br>'+'<b>word : '+df_tmp["word"].astype(str)+'</b><br>'+'count : '+df_tmp["freq"].astype(str)+'<br>')
                ) 
        fig_richesse.update_layout(title=title, 
                                xaxis_title="Rank", 
                                font_family="Inria Sans",
                                font_size = font_size,
                                width=width, 
                                height=height,
                                template=template)    
        fig_richesse.update_xaxes(tickformat=".0f", title_text="Rank", type="log")
        fig_richesse.update_yaxes(tickformat=".0f", title_text="Freq", type="log")
    return fig_richesse



def density_map(df_posts: pd.DataFrame,
                df_dots: pd.DataFrame,
                df_topics: pd.DataFrame,
                col_topic: str,
                col_engagement: str,
                col_text: str,
                col_text_dots: str,
                show_text: bool = True,
                show_topics: bool = True,
                show_halo: bool = False,
                show_histogram: bool = True,
                colorscale: str = "Portland",
                marker_color: str = "#ff7f0e",
                arrow_color: str = "#ff7f0e",
                width: int = 1000,
                height: int = 1000,
                label_size_ratio: int = 100,
                n_words: int = 3,
                title_text: str = "Clustering",
                max_dots_displayed: int = 0,
                max_topics_displayed: int = 20,
                opacity: float = 0.3,
                plot_bgcolor: str = None,
                paper_bgcolor: str = None,
                template: str = "plotly",
                font_size:int = 16) -> go.Figure:
    """
    Display a 2D histogram with contours and scattered dots.

    Args:
        df_posts (pd.DataFrame): DataFrame containing all data points to plot (corresponding to contours).
        df_dots (pd.DataFrame): DataFrame containing a sample of points to plot as dots.
        df_topics (pd.DataFrame): DataFrame containing topics representations.
        col_topic (str): Column name corresponding to category.
        col_engagement (str): Column name corresponding to a metric.
        col_text (str): Column name corresponding to a text separated by |.
        col_text_dots (str): Column name corresponding to the text for dots.
        colorscale (str, optional): Possible values are ``https://plotly.com/python/builtin-colorscales/``. Defaults to "Portland".
        marker_color (str, optional): Dots color value. Defaults to "#ff7f0e".
        arrow_color (str, optional): Arrow pointing to topic centroid color value. Defaults to "#ff7f0e".
        width (int, optional): Width of the plot. Defaults to 1000.
        height (int, optional): Height of the plot. Defaults to 1000.
        show_text (bool, optional): Show dots. Defaults to True.
        show_topics (bool, optional): Show topics labels. Defaults to True.
        show_halo (bool, optional): Show circles around topics. Defaults to False.
        show_histogram (bool, optional): Show 2D histogram with contours. Defaults to True.
        label_size_ratio (int, optional): Influence the size of the topics labels. Higher value means smaller topics labels. Defaults to 100.
        n_words (int, optional): Number of words to display. Defaults to 3.
        title_text (str, optional): Graph title. Defaults to "Clustering".
        max_dots_displayed (int, optional): Number of dots to display. Defaults to 0.
        max_topics_displayed (int, optional): Number of topics to display. Defaults to 20.
        opacity (float, optional): Opacity of dots. Defaults to 0.3.
        plot_bgcolor (str, optional): Background color for the plot. Defaults to None.
        paper_bgcolor (str, optional): Background color for the area around the plot. Defaults to None.
        template (str, optional): Plotly template. Defaults to "plotly".

    Returns:
        go.Figure: Plotly figure object.
    """

    # df_topics = df_distrib_sample.copy()
    df_topics= df_topics.dropna(subset=col_text)
    df_topics['text_bunka']= df_topics[col_text].apply(lambda x : "|".join(x.split('|')[:n_words]))
    

    if (max_topics_displayed>0) and (max_topics_displayed < len(df_topics[col_topic].unique())):
        df_topics= df_topics.sample(max_topics_displayed)

    #on  crée l'histogramme principal
    if show_histogram:
        fig_density = go.Figure(
                go.Histogram2dContour(
                    x=df_posts['x'],
                    y=df_posts['y'],
                    colorscale=colorscale,
                    showscale=False,
                    hoverinfo="none"
                )
            )
    else : 
        fig_density = go.Figure()

    #paramètre des contours
    fig_density.update_traces(
        contours_coloring="fill", contours_showlabels=False
    )

    #paramètres cosmetiques
    fig_density.update_layout(
                font_family="Inria Sans",           # font
                font_size = font_size,
                width=width,
                height=height,
                # margin=dict(
                #     t=width / 15,
                #     b=width / 25,
                #     r=width / 25,
                #     l=width / 25,
                # ),
                title=dict(text=title_text, font=dict(size=width / 40)),
                xaxis=dict(showline=False, zeroline=False, showgrid=False, showticklabels=False),
                yaxis=dict(showline=False, zeroline=False, showgrid=False, showticklabels=False),
            )

    # création de la légende de chaque points
    nk = np.empty(shape=(len(df_dots), 3, 1), dtype="object")
    nk[:, 0] = np.array(df_dots[col_topic]).reshape(-1, 1)
    nk[:, 1] = np.array(df_dots[col_text_dots].apply(lambda txt: '<br>'.join(textwrap.wrap(txt, width=50)))).reshape(-1, 1)
    nk[:, 2] = np.array(df_dots[col_engagement]).reshape(-1, 1)

    # ajout des points
    if show_text:
        fig_density.add_trace(
            go.Scatter(
                x=df_dots['x'],
                y=df_dots['y'],
                mode="markers",
                marker=dict(opacity=opacity, 
                            color=marker_color, 
                            maxdisplayed=max_dots_displayed
                            ),
                customdata=nk,
                hovertemplate=("<br>%{customdata[1]}<br>Engagements: %{customdata[2]}"+"<extra></extra>"),
                name="",
                
            )
        )

    if show_topics:
        # Afficher les topics
        for i, row in df_topics.iterrows():
            fig_density.add_annotation(
                x=row['topic_x'],
                y=row['topic_y'],
                # text="|".join(row['top_keywords'].split('|')[:n_words]),
                text=str(row['text_bunka']),
                showarrow=True,
                arrowhead=1,
                font=dict(
                    family="Inria Sans",
                    size=width / label_size_ratio,
                    color="blue",
                ),
                bordercolor="#c7c7c7",
                borderwidth=width / 1000,
                borderpad=width / 500,
                bgcolor="white",
                opacity=1,
                arrowcolor=arrow_color,
            )
    if show_halo:
        for i, row in df_posts.groupby(col_topic):
            x_hull, y_hull = get_convex_hull_coord(np.array(row[['x','y']]))
                
            # Create a Scatter plot with the convex hull coordinates
            trace = go.Scatter(
                x=x_hull,
                y=y_hull,
                mode="lines",
                name="Convex Hull",
                line=dict(color="grey", dash="dot"),
                hoverinfo="none",
            )
            fig_density.add_trace(trace)

    fig_density.update_layout(showlegend=False, 
                              width=width, 
                              height=height, 
                              template=template,
                              plot_bgcolor=plot_bgcolor,    #background color (plot)
                              paper_bgcolor=paper_bgcolor,   #background color (around plot)
                            )


    return fig_density



def topic_heatmap(df: pd.DataFrame,
                  col_x: str = "topic_x",
                  col_y: str = "topic_y",
                  col_topic: str = "soft_topic",
                  color_continuous_scale: str = 'GnBu',
                  title: str = "Similarity between topics", 
                  font_size:int = 16) -> go.Figure:
    """
    Display a heatmap representing the similarity between topics.

    Args:
        df (pd.DataFrame): DataFrame containing the topic data.
        col_x (str, optional): Column name for x-axis coordinates. Defaults to "topic_x".
        col_y (str, optional): Column name for y-axis coordinates. Defaults to "topic_y".
        col_topic (str, optional): Column name for the topic labels. Defaults to "soft_topic".
        color_continuous_scale (str, optional): Plotly color scale. Defaults to 'GnBu'.
        title (str, optional): Title of the heatmap. Defaults to "Similarity between topics".

    Returns:
        go.Figure: Plotly figure object representing the heatmap.
    """

    distance_matrix = cosine_similarity(np.array(df[[col_x,col_y]]))

    fig = px.imshow(distance_matrix,
                        labels=dict(color="Similarity Score"),
                        x=df[col_topic].astype(int).sort_values().astype(str),
                        y=df[col_topic].astype(int).sort_values().astype(str),
                        color_continuous_scale=color_continuous_scale
                        )

    fig.update_layout(
        font_family="Inria Sans",           # font
        font_size = font_size,
        title={
            'text': title,
            'y': .95,
            'x': 0.55,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(
                size=22,
                color="Black")
        },
        width=1000,
        height=1000,
        hoverlabel=dict(
            bgcolor="white",
            font_family="Inria Sans",           # font
            font_size = font_size,
        ),
    )
    fig.update_layout(showlegend=True)
    fig.update_layout(legend_title_text='Trend')
    return fig

def generate_wordcloud(df: pd.DataFrame,
                       col_word: str,
                       col_metric: str,
                       width: int = 3000,
                       height: int = 1500,
                       dpi: int = 300,
                       background_color: str = 'white',
                       font_path: str = "font/InriaSans-Bold.ttf",
                       colormap: str = "Viridis",
                       show: bool = False) -> WordCloud:
    """
    Generate a word cloud from a DataFrame.

    Args:
        df (pd.DataFrame): DataFrame containing word frequency data.
        col_word (str): Column name containing words.
        col_metric (str): Column name containing frequency metrics for each word.
        width (int, optional): Width of the word cloud image. Defaults to 3000.
        height (int, optional): Height of the word cloud image. Defaults to 1500.
        dpi (int, optional): Dots per inch for image resolution. Defaults to 300.
        background_color (str, optional): Background color of the word cloud image. Defaults to 'white'.
        font_path (str, optional): Path to the font file to be used in the word cloud. Defaults to "font/SEGUIEMJ.TTF".
        colormap (str, optional): Colormap for the word cloud image. Defaults to "Viridis".
        show (bool, optional): Whether to display the word cloud image. Defaults to False.

    Returns:
        WordCloud: WordCloud object representing the generated word cloud.
    """
    
    top_n_words={row[col_word]:row[col_metric] for i,row in df.iterrows()}
    
    # Generate a wordcloud of the top n words
    wordcloud = WordCloud(width=width, height=height, background_color=background_color, font_path = font_path, colormap = colormap, prefer_horizontal=1).generate_from_frequencies(top_n_words)
    if show : 
        plt.figure(figsize=(width/dpi, height/dpi), dpi=dpi)
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.show()
    return wordcloud

def create_radar(df: pd.DataFrame,
                 col_topic: str,
                 col_metrics: list,
                 title: str = "Radar",
                 opacity: float = 0.6,
                 width: int = 1000,
                 height: int = 1000,
                 template: str = "ggplot2",
                 plot_bgcolor: str = None,
                 paper_bgcolor: str = None,
                 font_size:int = 16) -> go.Figure:
    """
    Create a radar chart.

    Args:
        df (pd.DataFrame): DataFrame containing data for radar chart.
        col_topic (str): Column name containing topics.
        col_metrics (List[str]): List of column names containing metric values.
        title (str, optional): Title of the radar chart. Defaults to "Radar".
        opacity (float, optional): Opacity of radar area. Defaults to 0.6.
        width (int, optional): Width of the radar chart. Defaults to 1000.
        height (int, optional): Height of the radar chart. Defaults to 1000.
        template (str, optional): Plotly template to use. Defaults to "ggplot2".
        plot_bgcolor (Optional[str], optional): Background color of the plot. Defaults to None.
        paper_bgcolor (Optional[str], optional): Background color of the paper. Defaults to None.

    Returns:
        go.Figure: Plotly Figure object representing the radar chart.
    """

    df = df[[col_topic] + col_metrics]
    col_metrics.append(col_metrics[0])

    fig = go.Figure()
    for topic in list(df[col_topic].unique()) :

        data = df[df[col_topic]==topic].drop(columns=[col_topic]).values.tolist()[0]
        data.append(data[0])
        fig.add_trace(
            go.Scatterpolar(
                r=data,
                theta=col_metrics,
                fill="toself",
                fillcolor=None,
                name=topic,
                opacity=opacity            
                )
            )

    fig.update_layout(
        polar=dict(
                    angularaxis_showgrid=False,   # remove the axis
                    radialaxis=dict(
                    gridwidth=0,
                    gridcolor=None,
                    tickmode='array',  # Set tick mode to 'array'
                    tickvals=[0, 2, 4, 6, 8, 10],  # Specify tick values
                    showticklabels=True,  # Show tick labels
                    visible=True,
                    range=[0, 10],
                ),
                gridshape='linear',
                # bgcolor="white",
                ),
        showlegend=True,
        font_family="Inria Sans",
        font_size = 16,
        font_color="SlateGrey",
        title=title,             
        width=width,                  #plot size
        height=height,                #plot size
        plot_bgcolor=plot_bgcolor,    #background color (plot)
        paper_bgcolor=paper_bgcolor,   #background color (around plot)
        template=template,
        margin=dict(l=100, r=100, t=100, b=100)
    )
    return fig

def bar_subplots_per_cat(df: pd.DataFrame,
                         col_x: str,
                         col_y: str,
                         col_cat: str,
                         col_stack: str,
                         color_palette: dict = None,
                         n_top_words: int = 20,
                         **kwargs
                         ) -> go.Figure:
    """
    Create subplots of stacked bar charts.

    Args:
        df (pd.DataFrame): DataFrame containing data for bar charts.
        col_x (str): Name of the column containing x-axis values.
        col_y (str): Name of the column containing y-axis values.
        col_cat (str): Name of the column containing categories.
        col_stack (str): Name of the column containing stacking values.
        color_palette (Optional[Dict[str, str]], optional): Dictionary mapping categories to colors. Defaults to None.
        n_top_words (int, optional): Number of top words to display in each bar chart. Defaults to 20.
        **kwargs: Additional keyword arguments to update default plotting parameters.

    Returns:
        go.Figure: Plotly Figure object representing the subplots of stacked bar charts.
    """

    params = general_kwargs()
    params.update(kwargs)

    marker_color = params['marker_color']
    textposition = params["textposition"]
    vertical_spacing = params['vertical_spacing']
    horizontal_spacing = params["horizontal_spacing"]
    col_hover = params['col_hover']
    n_cols = params['n_cols']
    categories = df[col_cat].unique()

    # user define a number of columns, we compute the number of rows requires
    n_rows = math.ceil(len(categories) / n_cols)

    # fine tune parameter according to the text position provided
    if textposition == 'inside':
        horizontal_spacing = (horizontal_spacing / n_cols) / 2
    else:
        horizontal_spacing = (horizontal_spacing / n_cols)

    # create subplots
    fig = make_subplots(
        rows=n_rows,  # number of rows
        cols=n_cols,  # number of columns
        subplot_titles=list(categories),  # title for each subplot
        vertical_spacing=vertical_spacing / n_rows,  # space between subplots
        horizontal_spacing=horizontal_spacing,  # space between subplots
        shared_xaxes=params["shared_xaxes"],
        shared_yaxes=params["shared_yaxes"]
    )

    # create stacked bar traces for each subplot
    row_id = 0
    col_id = 0
    for i, category in enumerate(categories):
        # define row and column position
        col_id += 1
        if i % n_cols == 0:
            row_id += 1
        if col_id > n_cols:
            col_id = 1

        # select data
        current_df = df[df[col_cat] == category].sort_values(by=col_x, ascending=True)
        unique_stacks = current_df[col_stack].unique()

        if textposition == 'inside':
            text = current_df[col_y].head(n_top_words)
        else:
            textposition = "auto"
            text = None

        for stack in unique_stacks:
            # define bar color or create a random color
            if color_palette:
                marker_color = color_palette.get(stack, generate_random_hexadecimal_color())
            else:
                marker_color = generate_random_hexadecimal_color()
                
            stack_df = current_df[current_df[col_stack] == stack]
            hovertemplate = '<b>'+col_cat+" : "+ stack_df[col_cat].astype(str)+ '</b><br>' + col_stack+" : "+ stack_df[col_stack].astype(str)
            
            for col in col_hover:
                hovertemplate += '<br><b>' + col + ': ' + current_df[current_df[col_cat] == category][col].astype(str) + '</b>'


            fig.add_trace(
                go.Bar(
                    x=stack_df[col_x].tail(n_top_words),
                    y=stack_df[col_y].tail(n_top_words),
                    opacity=params["marker_opacity"],
                    orientation=params["orientation"],  # horizontal bars
                    name=stack,  # trace name for legend
                    text=text,  # text to display
                    textposition=textposition,  # text position
                    textangle=params["xaxis_tickangle"],  # text angle
                    marker_color=marker_color,  # bar color
                    hovertemplate=hovertemplate + "<extra></extra>"  # hover info
                ),
                row=row_id,
                col=col_id
            )

    for row_id in range(1, n_rows+1):
        for col_id in range(1, n_cols+1):
            fig.update_yaxes(title=params["yaxis_title"], row=row_id, col=1)
            fig.update_xaxes(title=params["xaxis_title"], row=row_id, col=col_id)

    fig.update_layout(
        margin=dict(l=75, r=75, t=75, b=50),
        title_text=params["title_text"],
        width=n_cols * params["width"],  # plot size
        height=n_rows * n_top_words * params["height"],  # plot size
        showlegend=params["showlegend"],
        font_family=params["font_family"],
        font_size=params["font_size"],
        template=params["template"],
        plot_bgcolor=params["plot_bgcolor"],  # background color (plot)
        paper_bgcolor=params["paper_bgcolor"],  # background color (around plot)
        uniformtext_minsize=params["uniformtext_minsize"],
        barmode=params['barmode']
    )

    fig.update_yaxes(
        # title=params["yaxis_title"],
        title_font_size=params["yaxis_title_font_size"],
        tickangle=params["yaxis_tickangle"],
        tickfont_size=params["yaxis_tickfont_size"],
        range=params["yaxis_range"],
        showgrid=params["yaxis_showgrid"],
        showline=params["yaxis_showline"],
        zeroline=params["yaxis_zeroline"],
        gridwidth=params["yaxis_gridwidth"],
        gridcolor=params["yaxis_gridcolor"],
        linewidth=params["yaxis_linewidth"],
        linecolor=params["yaxis_linecolor"],
        mirror=params["yaxis_mirror"],
        layer="below traces",
    )

    fig.update_xaxes(
        # title=params["xaxis_title"],
        title_font_size=params["xaxis_title_font_size"],
        tickangle=params["xaxis_tickangle"],
        tickfont_size=params["xaxis_tickfont_size"],
        range=params["xaxis_range"],
        showgrid=params["xaxis_showgrid"],
        showline=params["xaxis_showline"],
        zeroline=params["xaxis_zeroline"],
        gridwidth=params["xaxis_gridwidth"],
        gridcolor=params["xaxis_gridcolor"],
        linewidth=params["xaxis_linewidth"],
        linecolor=params["xaxis_linecolor"],
        mirror=params["xaxis_mirror"],
        layer="below traces"
    )
    return fig

# def bar_subplots(df: pd.DataFrame,
#                  col_x: str,
#                  col_y: str,
#                  col_cat: str,
#                  color_palette: dict = None,
#                  n_cols: int = 4,
#                  n_top_words: int = 20,
#                  horizontal_spacing: float = 0.2,
#                  vertical_spacing: float = 0.08,
#                  textposition: str = None,
#                  color: str = None,
#                  title: str = "Top words per topic",
#                  template: str = "plotly",
#                  bargap: float = 0.4,
#                  width: int = 500,
#                  height: int = 35,
#                  plot_bgcolor: str = None,
#                  paper_bgcolor: str = None,
#                  showlegend: bool = True,
#                  font_size:int=16) -> go.Figure:
#     """
#     Create subplots of horizontal bar charts.

#     Args:
#         df (pd.DataFrame): DataFrame containing data for bar charts.
#         col_x (str): Name of the column containing x-axis values.
#         col_y (str): Name of the column containing y-axis values.
#         col_cat (str): Name of the column containing categories.
#         color_palette (Optional[Dict[str, str]], optional): Dictionary mapping categories to colors. Defaults to None.
#         n_cols (int, optional): Number of columns in the subplot grid. Defaults to 4.
#         n_top_words (int, optional): Number of top words to display in each bar chart. Defaults to 20.
#         horizontal_spacing (float, optional): Spacing between subplots horizontally. Defaults to 0.2.
#         vertical_spacing (float, optional): Spacing between subplots vertically. Defaults to 0.08.
#         textposition (Optional[str], optional): Position of the text relative to the bars ('inside', 'outside', or None). Defaults to None.
#         color (Optional[str], optional): Color of the bars. Defaults to None.
#         title (str, optional): Title of the subplot. Defaults to "Top words per topic".
#         template (str, optional): Plotly template to use. Defaults to "plotly".
#         bargap (float, optional): Space between bars in the same cluster. Defaults to 0.4.
#         width (int, optional): Width of each subplot. Defaults to 500.
#         height (int, optional): Height of each bar in the subplot. Defaults to 35.
#         plot_bgcolor (Optional[str], optional): Background color of the plot. Defaults to None.
#         paper_bgcolor (Optional[str], optional): Background color of the paper. Defaults to None.
#         showlegend (bool, optional): Whether to display the legend. Defaults to True.

#     Returns:
#         go.Figure: Plotly Figure object representing the subplots of horizontal bar charts.
#     """
#     categories = df[col_cat].unique()

#     # user define a number of columns, we compute the number of rows requires
#     n_rows =  math.ceil(len(categories) / n_cols)

#     # fine tune parameter according to the text position provided
#     if textposition == 'inside':
#         horizontal_spacing = (horizontal_spacing / n_cols)/2
#     else:
#         horizontal_spacing = (horizontal_spacing / n_cols)
        
#     # create subplots
#     fig = make_subplots(
#         rows = n_rows,                           # number of rows
#         cols = n_cols,                           # number of columns
#         subplot_titles = list(categories),       # title for each subplot
#         vertical_spacing = vertical_spacing / n_rows,     # space between subplots
#         horizontal_spacing = horizontal_spacing  # space between subplots
#         )

#     # create bar traces for each subplot
#     row_id = 0
#     col_id = 0
#     for i, category in enumerate(categories):
        
#         # define bar color or create a random color
#         if color_palette:
#             color = color_palette.get(category, generate_random_hexadecimal_color())
#         else : 
#             if color is None:
#                 color = generate_random_hexadecimal_color()

#         # define row and column position
#         col_id +=1 
#         if i % n_cols == 0:
#             row_id += 1
#         if col_id > n_cols:
#             col_id = 1

#         # select data
#         current_df = df[df[col_cat]==category].sort_values(by=col_x, ascending = True)
#         hovertemplate='<b>'+current_df[current_df[col_cat]==category][col_y].astype(str)+"</b><br>"+current_df[current_df[col_cat]==category][col_x].astype(str)

#         if textposition == 'inside':
#             showticklabels = False
#             text=current_df[col_y].head(n_top_words)
#         else:
#             showticklabels = True
#             textposition="auto"
#             text=None

#         fig.add_trace(
#             go.Bar(
#                 x=current_df[col_x].tail(n_top_words), 
#                 y=current_df[col_y].tail(n_top_words),
#                 orientation='h',                                # horizontal bars
#                 name=category,                                  # trace name for legend
#                 text=text,                                      # text to display
#                 textposition=textposition,                      # text position
#                 textangle=0,                                    # text angle
#                 marker_color = color,                           # bar color
#                 hovertemplate=hovertemplate+"<extra></extra>"   # hover info
#                 ),
#             row=row_id, 
#             col=col_id
#             )

#     fig.update_layout(
#         height = n_rows * n_top_words * height,    # height depending on the number of rows and words to display
#         width = n_cols * width,                    # width depending on the number of cols
#         bargap = bargap,                           # space between bars
#         uniformtext_minsize=7,                     # Adjust the minimum size of text to avoid overlap
#         margin=dict(l=75, r=75, t=75, b=50),       # margins around the plot
#         showlegend=showlegend,                     # legend display
#         font_family="Inria Sans",           # font
#         font_size=font_size,
#         template=template,                         # template, possible values : plotly, plotly_white, plotly_dark, ggplot2, seaborn, simple_white, none
#         plot_bgcolor=plot_bgcolor,                 # background color (plot)
#         paper_bgcolor=paper_bgcolor,               # background color (around plot)
#         title_text=title                           # viz title
#         )

#     fig.update_yaxes(
#         showticklabels = showticklabels,          # show text near the bars
#         showline=False,                           #intermediate lines
#         showgrid=False,                           #grid
#         zeroline=False,
#         )
#     fig.update_xaxes(
#         showline=False,         #intermediate lines
#         showgrid=False,         #grid
#         zeroline=False,
#         )
#     return fig

# def pie_subplots(df: pd.DataFrame,
#                  col_x: str,
#                  col_y: str,
#                  col_cat: str,
#                  col_color: str,
#                  n_cols: int = 4,
#                  horizontal_spacing: float = 0.2,
#                  vertical_spacing: float = 0.08,
#                  title: str = "Top words per topic",
#                  template: str = "plotly",
#                  width: int = 500,
#                  height: int = 150,
#                  plot_bgcolor: str = None,
#                  paper_bgcolor: str = None,
#                  showlegend: bool = True,
#                  font_size=16) -> go.Figure:
#     """
#     Create subplots of pie charts.

#     Args:
#         df (pd.DataFrame): DataFrame containing data for pie charts.
#         col_x (str): Name of the column containing labels.
#         col_y (str): Name of the column containing values.
#         col_cat (str): Name of the column containing categories.
#         col_color (str): Name of the column containing colors.
#         n_cols (int, optional): Number of columns in the subplot grid. Defaults to 4.
#         horizontal_spacing (float, optional): Spacing between subplots horizontally. Defaults to 0.2.
#         vertical_spacing (float, optional): Spacing between subplots vertically. Defaults to 0.08.
#         title (str, optional): Title of the subplot. Defaults to "Top words per topic".
#         template (str, optional): Plotly template to use. Defaults to "plotly".
#         width (int, optional): Width of each subplot. Defaults to 500.
#         height (int, optional): Height of each subplot. Defaults to 150.
#         plot_bgcolor (Optional[str], optional): Background color of the plot. Defaults to None.
#         paper_bgcolor (Optional[str], optional): Background color of the paper. Defaults to None.
#         showlegend (bool, optional): Whether to display the legend. Defaults to True.

#     Returns:
#         go.Figure: Plotly Figure object representing the subplots of pie charts.
#     """    
#     categories = df[col_cat].unique()

#     # user define a number of columns, we compute the number of rows requires
#     n_rows =  math.ceil(len(categories) / n_cols)
        
#     specs = [[{'type':'domain'}] * n_cols] * n_rows
#     # create subplots
#     fig = make_subplots(
#         rows=n_rows,
#         cols=n_cols,
#         subplot_titles=list(categories),
#         horizontal_spacing=horizontal_spacing / n_cols,
#         vertical_spacing=vertical_spacing / n_rows,
#         specs=specs
#     )

#     # create pie chart subplots
#     for i, category in enumerate(categories):
#         col_id = i % n_cols + 1
#         row_id = i // n_cols + 1 

#         current_df = df[df[col_cat] == category]
#         hovertemplate = '<b>' + current_df[current_df[col_cat] == category][col_y].astype(str) + "</b><br>" + current_df[current_df[col_cat] == category][col_x].astype(str)

#         fig.add_trace(
#             go.Pie(
#             labels=current_df[col_x],
#             values=current_df[col_y],
#             name=category,
#             hole=.4,
#             hovertemplate=hovertemplate+"<extra></extra>",
#             marker=dict(colors=list(current_df[col_color])),
#             sort=False 
#             ),
#         row=row_id,
#         col=col_id,
#         )

#     # Update layout and axes
#     fig.update_layout(
#         height=n_rows * height,
#         width=n_cols * width,
#         uniformtext_minsize=7,
#         margin=dict(l=75, r=75, t=75, b=50),
#         showlegend=showlegend,
#         font_family="Inria Sans",
#         font_size=font_size,
#         template=template,
#         plot_bgcolor=plot_bgcolor,
#         paper_bgcolor=paper_bgcolor,
#         title_text=title
#     )
#     fig.update_yaxes(
#         showline=False,
#         showgrid=False,
#         zeroline=False
#     )
#     fig.update_xaxes(
#         showline=False,
#         showgrid=False,
#         zeroline=False
#     )

#     return fig


# def horizontal_stacked_bars(df: pd.DataFrame,
#                              col_x: str,
#                              col_y: str,
#                              col_percentage: str,
#                              col_cat: str,
#                              col_color: str,
#                              title_text: str = "Sentiment per topic",
#                              width: int = 1200,
#                              height: int = 1200,
#                              xaxis_tickangle: int = 0,
#                              horizontal_spacing: float = 0,
#                              vertical_spacing: float = 0.08,
#                              plot_bgcolor: str = None,
#                              paper_bgcolor: str = None,
#                              template: str = "plotly",
#                              font_size: int = 16) -> go.Figure:
#     """
#     Create horizontal stacked bar plots.

#     Args:
#         df (pd.DataFrame): DataFrame containing data for the bar plots.
#         col_x (str): Name of the column containing x-axis values.
#         col_y (str): Name of the column containing y-axis values.
#         col_percentage (str): Name of the column containing percentage values.
#         col_cat (str): Name of the column containing categories.
#         col_color (str): Name of the column containing colors.
#         title_text (str, optional): Title of the plot. Defaults to "Sentiment per topic".
#         width (int, optional): Width of the plot. Defaults to 1200.
#         height (int, optional): Height of the plot. Defaults to 1200.
#         xaxis_tickangle (int, optional): Angle for x-axis ticks. Defaults to 0.
#         horizontal_spacing (float, optional): Spacing between subplots horizontally. Defaults to 0.
#         vertical_spacing (float, optional): Spacing between subplots vertically. Defaults to 0.08.
#         plot_bgcolor (Optional[str], optional): Background color of the plot. Defaults to None.
#         paper_bgcolor (Optional[str], optional): Background color of the paper. Defaults to None.
#         template (str, optional): Plotly template to use. Defaults to "plotly".

#     Returns:
#         go.Figure: Plotly Figure object representing the horizontal stacked bar plots.
#     """
#     categories = df[col_cat].unique()

#     n_cols=2
#     fig = make_subplots(
#         rows = 1,                           # number of rows
#         cols = 2,                           # number of columns
#         # subplot_titles = list(categories),       # title for each subplot
#         vertical_spacing = vertical_spacing,     # space between subplots
#         horizontal_spacing = horizontal_spacing / n_cols # space between subplots
#         )
    
#     for cat in categories:
#         current_df = df[df[col_cat] == cat]
#         hovertemplate="Catégorie "+current_df[col_y].astype(str)+"<br><b>"+str(cat)+"</b><br>"+current_df[col_x].astype(str)+" "+str(col_x)+"<br>"+current_df[col_percentage].map("{:.1%}".format).astype(str)

#         fig.add_trace(
#             go.Bar(
                
#                 x=current_df[col_x], 
#                 y=current_df[col_y],
#                 orientation='h',
#                 # text = current_df[col_x],
#                 # textposition="inside",
#                 name=cat, 
#                 marker=dict(color=current_df[col_color]),
#                 hovertemplate=hovertemplate+'<extra></extra>',
#                 textfont_size=14
#                 ),
#             row=1,
#             col=1,
#         )

#         fig.add_trace(
#             go.Bar(
                
#                 x=current_df[col_percentage], 
#                 y=current_df[col_y],
#                 orientation='h',
#                 text = current_df[col_percentage].map("{:.1%}".format),
#                 textposition="inside",
#                 textangle=0,
#                 name="",
#                 marker=dict(color=current_df[col_color]),
#                 hovertemplate=hovertemplate+'<extra></extra>',
#                  showlegend = False
#                 ),
#             row=1,
#             col=2,
#         )

#     fig.update_layout(
#             barmode='stack',
#             title_text=title_text, 
#             showlegend=True,
#             width = width,
#             height= height,
#             xaxis_tickangle=xaxis_tickangle,
#             xaxis_showline=False,
#             xaxis_showgrid=False,
#             yaxis_showline=False,
#             yaxis_showgrid=False,
#             uniformtext_minsize=8,
#             uniformtext_mode='hide',
#             font_family="Inria Sans",
#             font_size=font_size,
#             template=template,
#             plot_bgcolor=plot_bgcolor,    #background color (plot)
#             paper_bgcolor=paper_bgcolor,   #background color (around plot)

#         )
#     fig.update_xaxes(title_text=col_x)
#     fig.update_yaxes(title_text=col_y, row=1,col=1)
#     fig.update_xaxes(title_text=col_x, range=[0,1], tickformat=".0%", row=1,col=2)
#     fig.update_yaxes(showticklabels = False, row=1,col=2)
    
#     return fig

# def bar_trend_per_day(df: pd.DataFrame, 
#                       col_date: str, 
#                       col_metric1: str, 
#                       col_metric2: str, 
#                       xaxis_title: str = "Date", 
#                       y1_axis_title: str = "Verbatims", 
#                       y2_axis_title: str = "Engagements", 
#                       title_text: str = "Trend - couverture & résonance", 
#                       width: int = 1500, 
#                       height: int = 700, 
#                       marker_color: str = "indianred", 
#                       line_color: str = "#273746", 
#                       plot_bgcolor: str = None, 
#                       paper_bgcolor: str = None, 
#                       template: str = "plotly",
#                       font_size: int = 16) -> go.Figure:
#     """
#     Creates a Plotly stacked bar chart with a secondary line plot for two metrics over time.

#     Parameters:
#     - df (pd.DataFrame): The DataFrame containing the data.
#     - col_date (str): The name of the column containing dates.
#     - col_metric1 (str): The name of the column containing the first metric values.
#     - col_metric2 (str): The name of the column containing the second metric values.
#     - xaxis_title (str, optional): The title for the x-axis. Defaults to "Date".
#     - y1_axis_title (str, optional): The title for the primary y-axis. Defaults to "Verbatims".
#     - y2_axis_title (str, optional): The title for the secondary y-axis. Defaults to "Engagements".
#     - title_text (str, optional): The title text for the chart. Defaults to "Trend - couverture & résonance".
#     - width (int, optional): The width of the chart. Defaults to 1500.
#     - height (int, optional): The height of the chart. Defaults to 700.
#     - marker_color (str, optional): The color of the bars. Defaults to "indianred".
#     - line_color (str, optional): The color of the line plot. Defaults to "#273746".
#     - plot_bgcolor (str, optional): The background color of the plot area. Defaults to None.
#     - paper_bgcolor (str, optional): The background color of the paper area. Defaults to None.
#     - template (str, optional): The template of the chart. Defaults to "plotly".

#     Returns:
#     - fig (go.Figure): The Plotly Figure object representing the stacked bar chart with line plot.
#     """
#     # Plotly Stacked Bar Chart
#     fig = make_subplots(specs=[[{"secondary_y": True}]])
#     hovertemplate='<b>Date :</b>'+ df[col_date].astype(str) + '<br><b>'+y1_axis_title+'</b>:'+ df[col_metric1].astype(str)+ '<br><b>'+y2_axis_title+'</b>:'+ df[col_metric2].astype(int).astype(str)

#     fig.add_trace(
#             go.Bar(
#                 name=y1_axis_title, 
#                 x=df[col_date], 
#                 y=df[col_metric1], 
#                 marker_color=marker_color, 
#                 opacity=0.8,
#                 hovertemplate=hovertemplate+"<extra></extra>"
#                 ),
#             secondary_y=False,
#         )       
        
#     fig.add_trace(
#             go.Scatter(
#                 x=df[col_date], 
#                 y=df[col_metric2], 
#                 name=y2_axis_title,
#                 mode='lines', 
#                 line_color=line_color, 
#                 line_width=2,
#                 hovertemplate=hovertemplate+"<extra></extra>"            
#                 ),
#             secondary_y=True,
#         )

#     first_axis_range=[-0.5,df[col_metric1].max()*1.01]
#     secondary_axis_range=[-0.5,df[col_metric2].max()*1.01]
#     # Change the layout if necessary
#     fig.update_layout(
#         barmode='stack',
#         xaxis_title=xaxis_title, 
#         width = width,
#         height = height,
#         title_text=title_text, 
#         showlegend=True,
#         xaxis_tickangle=0,
#         xaxis_showline=False,
#         xaxis_showgrid=False,
#         yaxis_showline=False,
#         yaxis_showgrid=False,
#         uniformtext_minsize=8,
#         uniformtext_mode='hide',
#         font_family="Inria Sans",
#         font_size=font_size,
#         template=template,
#         plot_bgcolor=plot_bgcolor,    #background color (plot)
#         paper_bgcolor=paper_bgcolor,   #background color (around plot)
#         )

                    
#     fig.update_yaxes(title_text=y1_axis_title, range=first_axis_range, secondary_y=False)
#     fig.update_yaxes(title_text=y2_axis_title, range = secondary_axis_range, secondary_y=True) 
#     fig.update_yaxes(
#         showline=False,
#         showgrid=False,
#         zeroline=False
#     )
#     fig.update_xaxes(
#         showline=False,
#         showgrid=False,
#         zeroline=False
#     ) 

#     return fig

# def bar_trend_per_day_per_cat(df: pd.DataFrame, 
#                               col_date: str, 
#                               col_cat: str, 
#                               col_metric1: str, 
#                               col_metric2: str, 
#                               col_color: str, 
#                               xaxis_title: str = "Date", 
#                               y1_axis_title: str = "Verbatims", 
#                               y2_axis_title: str = "Engagements", 
#                               title_text: str = "Trend - couverture & résonance", 
#                               vertical_spacing: float = 0.1, 
#                               width: int = 1500, 
#                               height: int = 700, 
#                               plot_bgcolor: str = None, 
#                               paper_bgcolor: str = None, 
#                               template: str = "plotly",
#                               font_size: int = 16) -> go.Figure:
#     """
#     Creates a Plotly stacked bar chart with multiple categories, each represented as a separate subplot.

#     Args:
#         df (pd.DataFrame): The DataFrame containing the data.
#         col_date (str): The name of the column containing dates.
#         col_cat (str): The name of the column containing categories.
#         col_metric1 (str): The name of the column containing the first metric values.
#         col_metric2 (str): The name of the column containing the second metric values.
#         col_color (str): The name of the column containing the color codes for each category.
#         xaxis_title (str, optional): The title for the x-axis. Defaults to "Date".
#         y1_axis_title (str, optional): The title for the primary y-axis. Defaults to "Verbatims".
#         y2_axis_title (str, optional): The title for the secondary y-axis. Defaults to "Engagements".
#         title_text (str, optional): The title text for the chart. Defaults to "Trend - couverture & résonance".
#         vertical_spacing (float, optional): The space between subplots. Defaults to 0.1.
#         width (int, optional): The width of the chart. Defaults to 1500.
#         height (int, optional): The height of the chart. Defaults to 700.
#         plot_bgcolor (str, optional): The background color of the plot area. Defaults to None.
#         paper_bgcolor (str, optional): The background color of the paper area. Defaults to None.
#         template (str, optional): The template of the chart. Defaults to "plotly".

#     Returns:
#         fig (go.Figure): The Plotly Figure object representing the stacked bar chart with subplots for each category.
#     """
#     fig = make_subplots(
#         rows = 2,                           # number of rows
#         cols = 1,                           # number of columns
#         vertical_spacing = vertical_spacing,     # space between subplots
#     )

#     categories = df[col_cat].unique()
#     for cat in categories:
#         current_df = df[df[col_cat] == cat]
    
#         hovertemplate='<b>Categorie : </b>'+str(cat)+'<br><b>Date : </b>'+ current_df[col_date].astype(str) + '<br><b>'+y1_axis_title+'</b> : '+ current_df[col_metric1].astype(str)+' ('+current_df["per_"+col_metric1].map("{:.1%}".format).astype(str)+')' +'<br><b>'+y2_axis_title+'</b> : '+ current_df[col_metric2].astype(int).astype(str)+' ('+current_df["per_"+col_metric2].map("{:.1%}".format).astype(str)+')'

#         fig.add_trace(
#             go.Bar(
#                 x=current_df[col_date], 
#                 y=current_df[col_metric1],
#                 orientation='v',
#                 name=cat, 
#                 marker=dict(color=current_df[col_color]),
#                 hovertemplate=hovertemplate+'<extra></extra>',
#                 textfont_size=14,
#                 legendgroup=cat
#                 ),
#             row=1,
#             col=1,
#         )

#         fig.add_trace(
#             go.Bar(
                
#                 x=current_df[col_date], 
#                 y=current_df[col_metric2],
#                 orientation='v',
#                 name="",
#                 marker=dict(color=current_df[col_color]),
#                 hovertemplate=hovertemplate+'<extra></extra>',
#                 showlegend = False,
#                 legendgroup=cat
#                 ),
#             row=2,
#             col=1,
#         )

#     fig.update_layout(
#             barmode='stack',
#             title_text=title_text, 
#             showlegend=True,
#             width = width,
#             height= height,
#             xaxis_tickangle=0,
#             xaxis_showline=False,
#             xaxis_showgrid=False,
#             yaxis_showline=False,
#             yaxis_showgrid=False,
#             uniformtext_minsize=8,
#             uniformtext_mode='hide',
#             font_family="Inria Sans",
#             font_size=font_size,
#             template=template,
#             plot_bgcolor=plot_bgcolor,    #background color (plot)
#             paper_bgcolor=paper_bgcolor,   #background color (around plot)
#             legend_tracegroupgap=0

#         )
#     fig.update_xaxes(showticklabels = False, row=1,col=1)
#     fig.update_xaxes(title_text=xaxis_title, row=2,col=1)
#     fig.update_yaxes(title_text=y1_axis_title, row=1,col=1)
#     fig.update_yaxes(title_text=y2_axis_title, row=2,col=1)
#     fig.update_yaxes(
#         showline=False,
#         showgrid=False,
#         zeroline=False
#     )
#     fig.update_xaxes(
#         showline=False,
#         showgrid=False,
#         zeroline=False
#     )

#     return fig

# def pie(df: pd.DataFrame, 
#         col_x: str, 
#         col_y: str, 
#         col_color: str, 
#         title: str = "Sentiment", 
#         template: str = "plotly",  
#         width: int = 1000, 
#         height: int = 1000, 
#         plot_bgcolor: str = None, 
#         paper_bgcolor: str = None, 
#         showlegend: bool = True,
#         font_size: int = 16) -> go.Figure:
#     """
#     Creates a Plotly pie chart.

#     Args:
#         df (pd.DataFrame): The DataFrame containing the data.
#         col_x (str): The name of the column containing the labels for the pie chart slices.
#         col_y (str): The name of the column containing the values for the pie chart slices.
#         col_color (str): The name of the column containing the colors for the pie chart slices.
#         title (str, optional): The title for the pie chart. Defaults to "Sentiment".
#         template (str, optional): The template of the chart. Defaults to "plotly".
#         width (int, optional): The width of the chart. Defaults to 1000.
#         height (int, optional): The height of the chart. Defaults to 1000.
#         plot_bgcolor (str, optional): The background color of the plot area. Defaults to None.
#         paper_bgcolor (str, optional): The background color of the paper area. Defaults to None.
#         showlegend (bool, optional): Whether to show the legend. Defaults to True.

#     Returns:
#         fig (go.Figure): The Plotly Figure object representing the pie chart.
#     """    
#     fig = go.Figure()
#     fig.add_trace(go.Pie(
#         labels=df[col_x],
#         values=df[col_y],
#         name="",
#         hole=.4,
#         hovertemplate='<b>'+ df[col_x].astype(str) +"</b><br>"+ str(col_y) + " : "+df[col_y].astype(str) + "<extra></extra>",
#         marker=dict(colors=list(df[col_color])),
#         textfont_size = 18,
#         sort=False 
#         ),
#     )

#     # Update layout and axes
#     fig.update_layout(
#         height=height,
#         width=width,
#         uniformtext_minsize=7,
#         margin=dict(l=75, r=75, t=75, b=50),
#         showlegend=showlegend,
#         font_family="Inria Sans",
#         font_size=font_size,
#         template=template,
#         plot_bgcolor=plot_bgcolor,
#         paper_bgcolor=paper_bgcolor,
#         title_text=title
#     )
#     fig.update_yaxes(
#         showline=False,
#         showgrid=False,
#         zeroline=False
#     )
#     fig.update_xaxes(
#         showline=False,
#         showgrid=False,
#         zeroline=False
#     )
#     return fig

# def bar(df: pd.DataFrame, 
#         x: str, 
#         y: str, 
#         color: str = "indianred", 
#         xaxis_title: str = "x", 
#         yaxis_title: str = "y", 
#         width: int = 1200, 
#         height: int = 700, 
#         title_text: str = "", 
#         plot_bgcolor: str = None, 
#         paper_bgcolor: str = None, 
#         template: str = "plotly", 
#         showlegend: bool = True,
#         font_size: int = 16,
#         xaxis_tickangle:int=0) -> go.Figure:
#     """
#     Creates a Plotly vertical bar chart.

#     Args:
#         df (pd.DataFrame): The DataFrame containing the data.
#         x (str): The name of the column containing the x-axis values.
#         y (str): The name of the column containing the y-axis values.
#         color (str, optional): The color of the bars. Defaults to "indianred".
#         xaxis_title (str, optional): The title for the x-axis. Defaults to "x".
#         yaxis_title (str, optional): The title for the y-axis. Defaults to "y".
#         width (int, optional): The width of the chart. Defaults to 1200.
#         height (int, optional): The height of the chart. Defaults to 700.
#         title_text (str, optional): The title text for the chart. Defaults to "".
#         plot_bgcolor (str, optional): The background color of the plot area. Defaults to None.
#         paper_bgcolor (str, optional): The background color of the paper area. Defaults to None.
#         template (str, optional): The template of the chart. Defaults to "plotly".
#         showlegend (bool, optional): Whether to show the legend. Defaults to True.
#         xaxis_tickangle (int, optional) : label angle on x axis

#     Returns:
#         fig (go.Figure): The Plotly Figure object representing the vertical bar chart.
#     """
#     fig = go.Figure()
#     fig.add_trace(
#         go.Bar(
#                 x=df[x], 
#                 y=df[y],
#                 orientation='v',
#                 name=yaxis_title, 
#                 marker=dict(color=color),
#                 hovertemplate = str(x) +" : "+df[x].astype(str)+"<br>"+str(y)+" : "+df[y].astype(str)+'<extra></extra>'
#         )

#     )
#     fig.update_traces(marker_color=color)
#     fig.update_layout(
#         title=title_text, 
#         xaxis_title=xaxis_title, 
#         yaxis_title=yaxis_title,
#         title_text=title_text, 
#         showlegend=showlegend,
#         width = width,
#         height= height,
#         xaxis_tickangle=xaxis_tickangle,
#         xaxis_showline=False,
#         xaxis_showgrid=False,
#         yaxis_showline=False,
#         yaxis_showgrid=False,
#         uniformtext_minsize=8,
#         uniformtext_mode='hide',
#         font_family="Inria Sans",
#         font_size = font_size,
#         template=template,
#         plot_bgcolor=plot_bgcolor,    #background color (plot)
#         paper_bgcolor=paper_bgcolor,   #background color (around plot)
#         )
#     return fig






# def subplots_bar_per_day_per_cat(df: pd.DataFrame, 
#                                  col_date: str, 
#                                  col_cat: str, 
#                                  metrics: list, 
#                                  col_color: str, 
#                                  y_axis_titles: list, 
#                                  xaxis_title: str = "Date", 
#                                  title_text: str = "Trend - couverture & résonance", 
#                                  vertical_spacing: float = 0.1, 
#                                  width: int = 1500, 
#                                  height: int = 700, 
#                                  plot_bgcolor: str = None, 
#                                  paper_bgcolor: str = None, 
#                                  template: str = "plotly",
#                                  font_size: int = 16) -> go.Figure:
#     """
#     Creates subplots of stacked bar charts per day and category using Plotly.

#     Args:
#         df (pd.DataFrame): The DataFrame containing the data.
#         col_date (str): The name of the column representing dates.
#         col_cat (str): The name of the column representing categories.
#         metrics (List[str]): A list of column names representing metrics to be plotted.
#         col_color (str): The name of the column representing colors for bars.
#         y_axis_titles (List[str]): A list of titles for the y-axes of subplots.
#         xaxis_title (str, optional): The title for the x-axis. Defaults to "Date".
#         title_text (str, optional): The title for the entire plot. Defaults to "Trend - couverture & résonance".
#         vertical_spacing (float, optional): The space between subplots. Defaults to 0.1.
#         width (int, optional): The width of the entire plot. Defaults to 1500.
#         height (int, optional): The height of each subplot. Defaults to 700.
#         plot_bgcolor (str, optional): The background color for the plot area. Defaults to None.
#         paper_bgcolor (str, optional): The background color for the paper area. Defaults to None.
#         template (str, optional): The template of the plot. Defaults to "plotly".

#     Returns:
#         fig (go.Figure): The Plotly Figure object representing the subplots of stacked bar charts.
#     """
#     fig = make_subplots(
#         rows = len(metrics),                           # number of rows
#         cols = 1,                           # number of columns
#         vertical_spacing = vertical_spacing,     # space between subplots
#     )

#     categories = df[col_cat].unique()
#     for cat in categories:
#         current_df = df[df[col_cat] == cat]
    
#         hovertemplate='<b>Categorie : </b>'+str(cat)+'<br><b>Date : </b>'+ current_df[col_date].astype(str)

#         for i, metric in enumerate(metrics):
#             hovertemplate +=  '<br><b>'+ metric + " : "+current_df[metric].astype(str) 
#             if i==0:
#                 showlegend = True
#             else:
#                 showlegend = False

#             fig.add_trace(
#                 go.Bar(
#                     x=current_df[col_date], 
#                     y=current_df[metric],
#                     orientation='v',
#                     name=cat, 
#                     marker=dict(color=current_df[col_color]),
#                     hovertemplate=hovertemplate+'<extra></extra>',
#                     textfont_size=14,
#                     showlegend = showlegend,
#                     legendgroup=cat
#                     ),
#                 row = i+1,
#                 col=1,
#             )

#     fig.update_layout(
#             barmode='stack',
#             title_text=title_text, 
#             showlegend=True,
#             width = width,
#             height= height * len(metrics),
#             xaxis_tickangle=0,
#             xaxis_showline=False,
#             xaxis_showgrid=False,
#             yaxis_showline=False,
#             yaxis_showgrid=False,
#             uniformtext_minsize=8,
#             uniformtext_mode='hide',
#             font_family="Inria Sans",
#             font_size=font_size,
#             template=template,
#             plot_bgcolor=plot_bgcolor,    #background color (plot)
#             paper_bgcolor=paper_bgcolor,   #background color (around plot)
#             legend_tracegroupgap=0

#         )

#     for i, title in enumerate(y_axis_titles):
#         fig.update_xaxes(title_text=xaxis_title, row=i+1,col=1)

#         fig.update_yaxes(title_text=title, row=i+1,col=1)

#     fig.update_yaxes(
#         showline=False,
#         showgrid=False,
#         zeroline=False
#     )
#     fig.update_xaxes(
#         showline=False,
#         showgrid=False,
#         zeroline=False
#     )

#     return fig


# def boxplot(df : pd.DataFrame, col_y : str = "degrees" , title : str ="Distribution of Node Degrees", yaxis_title : str = 'Degrees', width : int =1000, height: int =1000, plot_bgcolor: str = None, paper_bgcolor: str = None, template: str = "plotly", font_size : int = 16) -> go.Figure:
#     """
#     Generates a box plot using Plotly Express with customization options.

#     Args:
#         df (pd.DataFrame): The DataFrame containing the data to plot.
#         col_y (str, optional): The column name in the DataFrame to plot on the y-axis. Default is "degrees".
#         title (str, optional): The title of the plot. Default is "Distribution of Node Degrees".
#         yaxis_title (str, optional): The label for the y-axis. Default is 'Degrees'.
#         width (int, optional): The width of the plot in pixels. Default is 1000.
#         height (int, optional): The height of the plot in pixels. Default is 1000.
#         plot_bgcolor (str, optional): The background color of the plot area. Default is None.
#         paper_bgcolor (str, optional): The background color of the paper (overall plot background). Default is None.
#         template (str, optional): The template for the plot. Default is "plotly".
#         font_size (int, optional): The font size for the plot text. Default is 16.

#     Returns:
#         fig (go.Figure): The Plotly Figure object for the box plot.
#     """
#     # Box plot using Plotly Express
#     fig = px.box(df, y = col_y, title=title)

#     # Customize the plot (optional)
#     fig.update_layout(
#         yaxis_title = yaxis_title,
#         xaxis_title='',
#         showlegend=False,
#         width=width,
#         height=height,
#         font_family="Inria Sans",
#         font_size=font_size,
#         template=template,
#         plot_bgcolor=plot_bgcolor,    #background color (plot)
#         paper_bgcolor=paper_bgcolor
#     )
#     return fig
