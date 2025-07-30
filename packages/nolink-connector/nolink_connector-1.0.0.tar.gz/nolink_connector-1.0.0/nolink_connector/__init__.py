"""
NoLink Connector - Auto-detecting Socket.IO Terminal Bridge
"""

__version__ = "1.0.0"
__author__ = "Sumedh Patil"
__email__ = "sumedhpatil99@gmail.com"
__description__ = "Auto-detecting Socket.IO Terminal Bridge for web platforms"

from .main import main
from .detector import APIKeyDetector
from .server import SocketIOTerminalServer
from .security import SecurityManager

__all__ = [
    'main',
    'APIKeyDetector', 
    'SocketIOTerminalServer',
    'SecurityManager'
]
