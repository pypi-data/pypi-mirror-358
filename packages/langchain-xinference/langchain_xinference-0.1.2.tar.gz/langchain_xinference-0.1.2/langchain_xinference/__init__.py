from importlib import metadata

from langchain_xinference.chat_models import ChatXinference
from langchain_xinference.embeddings import XinferenceEmbeddings
from langchain_xinference.llms import Xinference
from langchain_xinference.reranks import XinferenceRerank

try:
    __version__ = metadata.version(__package__)
except metadata.PackageNotFoundError:
    # Case where package metadata is not available.
    __version__ = ""
del metadata  # optional, avoids polluting the results of dir(__package__)

__all__ = [
    "ChatXinference",
    "Xinference",
    "XinferenceEmbeddings",
    "XinferenceRerank",
    "__version__",
]
