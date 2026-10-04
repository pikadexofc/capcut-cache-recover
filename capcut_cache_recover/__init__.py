"""Export Capcut Pro Video Free - High-performance recovery engine to decrypt, unlock, and export unplayable CapCut & JianYing draft cache videos."""

__version__ = "1.0.1"
__tool_name__ = "Export Capcut Pro Video Free"
__author__ = "Shanto (pikadexofc)"
__license__ = "MIT"

from .cryptor import recover_file, recover_bytes, CryptorParams
from .scanner import find_encrypted_videos
