"""mini_mac_address — parse, validate, and reformat MAC addresses.

Public API re-exported from :mod:`mini_mac_address.core`.
"""

from .core import (
    MACAddress,
    MACParseError,
    format_mac,
    parse_mac,
)

__all__ = [
    "MACAddress",
    "MACParseError",
    "format_mac",
    "parse_mac",
]

__version__ = "1.0.0"
