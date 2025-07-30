"""
JellyProxy - Jellyfin MPV IPC Proxy & Filter

A Python-based proxy system that intercepts and filters IPC communication
between jellyfin-mpv-shim (JMS) and mpv, while also managing mpv's lifecycle.
"""

__version__ = "0.1.0"
__author__ = "JellyProxy Contributors"
__description__ = "Jellyfin MPV IPC Proxy & Filter"
__license__ = "GPL-3.0-or-later"

from .proxy import JellyProxy
from .config import ProxyConfig

__all__ = ['JellyProxy', 'ProxyConfig']
