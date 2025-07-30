from .utils.FilesManager import FileManager
from .logic.Converter import Converter
from ._bridgex import Bridgex

__author__:str = "Tutos Rive"
__version__:str = "0.0.2-dev"
__license__:str = "MIT"
__description__:str = "Graphical interface for converting files to Markdown, built in Python and based on PySide6 and Markitdown."
__all__:list[str] = ['FileManager', 'Converter', 'Bridgex', '__author__', '__version__', '__license__', '__description__']