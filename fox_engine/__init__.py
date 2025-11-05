# fox_engine/__init__.py
from .core import FoxMode, TugasFox, MetrikFox
from .manager import ManajerFox
from .api import tfox, wfox, sfox, mfox, fox, dapatkan_manajer_fox

__version__ = "1.0.0-fase1"
__all__ = [
    'FoxMode',
    'TugasFox',
    'MetrikFox',
    'ManajerFox',
    'tfox',
    'wfox',
    'sfox',
    'mfox',
    'fox',
    'dapatkan_manajer_fox'
]
