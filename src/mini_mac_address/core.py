"""Core parsing, validation, and formatting logic for MAC addresses.

Notation decisions
------------------
This library deliberately supports a single, common length: 48-bit (6-octet)
MAC addresses in EUI-48 form. 64-bit EUI-64 identifiers use a different format
and mixing them here would produce a parser with confusing success conditions
("is this 16 hex digits or 12?"). If you need EUI-64 support, choose a
different library — that decision is stated plainly rather than half-implemented.

Supported input separators: ``:`` (colon), ``-`` (hyphen), ``.`` (Cisco
dotted), or no separator at all (raw hex). Mixed separators in a single string
("aa:bb-cc") are rejected; real-world inputs almost never mix them, and
accepting them would hide transcription errors rather than fix them.

The case of hex letters is preserved on input so that ``format_mac`` round-trips
losslessly, but formatting always produces uppercase output because that is the
ubiquitous display convention for MAC addresses in network tooling.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Tuple

__all__ = [
    "MACAddress",
    "MACParseError",
    "format_mac",
    "parse_mac",
]


# Pre-compiled at module load so repeated parsing does not pay re-compilation cost.
# Each pattern enforces a single separator throughout the entire string — mixing
# is rejected rather than silently normalised.
_COLON_RE = re.compile(r"^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$")
_HYPHEN_RE = re.compile(r"^([0-9A-Fa-f]{2}-){5}[0-9A-Fa-f]{2}$")
# Cisco dotted notation groups as xxxx.xxxx.xxxx (three groups of four hex digits).
_DOT_RE = re.compile(r"^([0-9A-Fa-f]{4}\.){2}[0-9A-Fa-f]{4}$")
_RAW_RE = re.compile(r"^[0-9A-Fa-f]{12}$")


class MACParseError(ValueError):
    """Raised when input cannot be interpreted as a 48-bit MAC address.

    Subclassing :class:`ValueError` keeps backwards-compatibility with code
    that already catches ``ValueError`` from hand-rolled parsing.
    """


@dataclass(frozen=True)
class MACAddress:
    """An immutable, normalised representation of a 48-bit MAC address.

    Attributes
    ----------
    octets:
        Six uppercase hex digit-pairs as a tuple, e.g.
        ``('AA', 'BB', 'CC', 'DD', 'EE', 'FF')``.
    raw:
        The 12-character uppercase raw hex string, useful as a dict key.
    """

    octets: Tuple[str, str, str, str, str, str]

    @property
    def raw(self) -> str:
        """Uppercase 12-character hex string with no separators."""
        return "".join(self.octets)

    def format(self, sep: str = ":") -> str:
        """Return the address rendered with ``sep`` between octet pairs.

        Parameters
        ----------
        sep:
            One of ``":"``, ``"-"``, ``"."``, or ``""`` (empty string).

        Notes
        -----
        The dot separator uses Cisco's grouping of four hex digits
        (``aabb.ccdd.eeff``) rather than per-octet grouping, because that is
        the only convention actually seen in the wild for the dot style.
        """
        if sep == ":":
            return ":".join(self.octets)
        if sep == "-":
            return "-".join(self.octets)
        if sep == ".":
            raw = self.raw
            return f"{raw[0:4]}.{raw[4:8]}.{raw[8:12]}"
        if sep == "":
            return self.raw
        raise ValueError(f"unsupported separator: {sep!r}")


def parse_mac(value: str) -> MACAddress:
    """Parse a MAC address string into a :class:`MACAddress`.

    Parameters
    ----------
    value:
        Input in colon, hyphen, dot, or raw-hex notation.

    Raises
    ------
    MACParseError:
        If the input is not a string, is empty, or does not match one of the
        supported notations.
    """
    if not isinstance(value, str):
        raise MACParseError(f"expected str, got {type(value).__name__}")
    s = value.strip()
    if not s:
        raise MACParseError("input is empty")

    if _COLON_RE.match(s) or _HYPHEN_RE.match(s):
        parts = re.split(r"[:\-]", s)
    elif _DOT_RE.match(s):
        # Cisco dotted joins three 4-digit groups into six 2-digit octets.
        parts = [s[0:2], s[2:4], s[5:7], s[7:9], s[10:12], s[12:14]]
    elif _RAW_RE.match(s):
        parts = [s[i : i + 2] for i in range(0, 12, 2)]
    else:
        raise MACParseError(f"not a recognised MAC notation: {value!r}")

    octets = tuple(p.upper() for p in parts)
    return MACAddress(octets=octets)  # type: ignore[arg-type]


def format_mac(value: str, sep: str = ":") -> str:
    """Parse ``value`` and immediately re-format it with ``sep``.

    Convenience wrapper around :func:`parse_mac` and :meth:`MACAddress.format`.
    Raises :class:`MACParseError` on bad input.
    """
    return parse_mac(value).format(sep)
