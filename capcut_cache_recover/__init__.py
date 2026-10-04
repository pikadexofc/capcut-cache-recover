"""CapCut Cache Recover - High-performance engine to recover and decrypt unplayable CapCut & JianYing draft cache videos."""

__version__ = "1.0.0"
__author__ = "Shanto (pikadexofc)"
__license__ = "MIT"

from .cryptor import recover_file, recover_bytes, CryptorParams
from .scanner import find_encrypted_videos
