from importlib import metadata

from langchain_digitalocean.chat_models import ChatDigitalOcean
from langchain_digitalocean.document_loaders import LangchainDigitaloceanLoader
from langchain_digitalocean.embeddings import LangchainDigitaloceanEmbeddings
from langchain_digitalocean.retrievers import LangchainDigitaloceanRetriever
from langchain_digitalocean.toolkits import LangchainDigitaloceanToolkit
from langchain_digitalocean.tools import LangchainDigitaloceanTool
from langchain_digitalocean.vectorstores import LangchainDigitaloceanVectorStore

try:
    __version__ = metadata.version(__package__)
except metadata.PackageNotFoundError:
    # Case where package metadata is not available.
    __version__ = ""
del metadata  # optional, avoids polluting the results of dir(__package__)

__all__ = [
    "ChatDigitalocean",
    "LangchainDigitaloceanVectorStore",
    "LangchainDigitaloceanEmbeddings",
    "LangchainDigitaloceanLoader",
    "LangchainDigitaloceanRetriever",
    "LangchainDigitaloceanToolkit",
    "LangchainDigitaloceanTool",
    "__version__",
]
