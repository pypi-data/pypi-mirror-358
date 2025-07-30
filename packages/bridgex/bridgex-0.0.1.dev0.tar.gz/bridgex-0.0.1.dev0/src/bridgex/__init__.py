from .utils.FilesManager import FileManager
from .logic.Converter import Converter
from ._bridgex import Bridgex

__author__:str = "Tutos Rive"
__version__:str = "0.0.1-dev"
__license__:str = "MIT"
__description__:str = "Bridgex is a PySide6 application for file management and conversion, featuring a lite markdown editor and viewer."
__all__:list[str] = ['FileManager', 'Converter', 'Bridgex', '__author__', '__version__', '__license__', '__description__']