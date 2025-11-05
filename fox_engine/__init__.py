# fox_engine/__init__.py
from .core import FoxMode, TugasFox, MetrikFox
from .manager import ManajerFox
from .api import tfox, wfox, fox, dapatkan_manajer_fox
from .monitor_sumber_daya import MonitorSumberDaya
from .batas_adaptif import BatasAdaptif

__version__ = "1.0.0-fase2"
__all__ = [
    'FoxMode',
    'TugasFox',
    'MetrikFox',
    'ManajerFox',
    'tfox',
    'wfox',
    'fox',
    'dapatkan_manajer_fox',
    'MonitorSumberDaya',
    'BatasAdaptif',
]
