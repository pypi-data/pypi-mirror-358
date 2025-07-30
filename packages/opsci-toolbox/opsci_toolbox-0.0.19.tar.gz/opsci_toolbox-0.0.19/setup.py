from setuptools import setup, find_packages

# with open('requirements.txt') as f:
#     requirements = f.read().splitlines()

setup(
    name='opsci_toolbox',
    version='0.0.19',
    description="a complete toolbox",
    author='Erwan Le Nagard',
    author_email='erwan@opsci.ai',
    licence="MIT",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0,<3",
        # "translatehtml==1.5.2",
        # "packaging==23.1",
        "beautifulsoup4==4.9.3",
        "chardet>=4.0.0",
        "chart_studio==1.1.0",
        "eldar==0.0.8",
        "emoji==2.10.1",
        "fa2_modified==0.3.10",
        "google_api_python_client==2.122.0",
        "gspread==6.1.2",
        "hdbscan==0.8.33",
        "jusText==3.0.0",
        "langchain==0.1.20",
        "matplotlib>=3.9.0",
        "mysql-connector-python>=9.0.0",
        "networkx==3.2.1",
        "nltk==3.8.1",
        "numpy>=1.21.5,<1.25.0",
        "opencv_python_headless==4.9.0.80",
        "openpyxl==3.1.3",
        "pandas>=1.5.3",
        "Pillow>=9.0.1",
        "plotly==5.19.0",
        "protobuf==4.23.4",
        "pyarrow>=14.0.2",
        "python_louvain==0.16",
        "scikit_learn==1.4.1.post1",
        'scipy>=1.8.0,<2.0.0',
        "sentence_transformers==2.5.1",
        "setuptools==59.6.0",
        "spacy==3.7.4",
        "spacy_language_detection==0.2.1",
        "spacymoji==3.1.0",
        "supervision==0.21.0",
        "textacy==0.13.0",
        "torch>=2.4.0",
        "tqdm>=4.66.2",
        "trafilatura==1.7.0",
        "transformers==4.38.2",
        "umap_learn==0.5.5",
        "urlextract==1.9.0",
        "wordcloud==1.9.3",
        "Unidecode==1.3.8",
        "kaleido==0.2.1",
        "gliner==0.2.8"
        # "libretranslate==1.6.0",
    ],  # Add any dependencies your library needs
    dependency_links=[
        'https://download.pytorch.org/whl/cu124'
    ],
    include_package_data=True,
    package_data={'': ['lexicons/*.csv']},  # Include all Python files in the lib directory
)