# mini_mac_address

Parse, validate, and reformat 48-bit MAC addresses between colon, hyphen, dot (Cisco dotted), and raw hex notations.

```python
from mini_mac_address import MACAddress, MACParseError, format_mac, parse_mac

mac: MACAddress = parse_mac("aa:bb:cc:dd:ee:ff")
print(mac.raw)            # AABBCCDDEEFF
print(mac.format(":"))    # AA:BB:CC:DD:EE:FF
print(mac.format("-"))    # AA-BB-CC-DD-EE-FF
print(mac.format("."))    # AABB.CCDD.EEFF
print(mac.format(""))     # AABBCCDDEEFF

# One-shot convenience:
print(format_mac("aabbccddeeff", ":"))   # AA:BB:CC:DD:EE:FF

try:
    parse_mac("not a mac")
except MACParseError as exc:
    print(exc)
```

## Why this exists

Network configuration data arrives in whatever notation the source tool happened to use — `ifconfig` prints colons, Cisco gear prints dots, vendor databases often store raw hex. A single small parser that normalises all four styles into one canonical object lets the rest of your code compare and store MACs without sprinkling regexes everywhere.

The trade-off: this library handles **EUI-48 only**. 64-bit EUI-64 addresses (16 hex digits) are rejected, not silently truncated. Supporting both lengths in one parser produces ambiguous success conditions (is `aabbccddeeff0011` one EUI-64 or a typoed pair of EUI-48s?), so the scope is kept narrow and predictable.

## Edge you will hit

Dot notation follows Cisco's convention: three groups of **four** hex digits (`aabb.ccdd.eeff`), not six pairs. If your input uses dots between every octet (`aa.bb.cc.dd.ee.ff`), it will be rejected. That style does not appear in real network tooling, so accepting it would hide typos rather than fix them.

Mixed separators within a single string (`aa:bb-cc:dd:ee:ff`) are also rejected for the same reason — a MAC with mixed separators is almost always a copy-paste error, not a valid address in distress.

All formatted output is uppercase, matching the display convention used by virtually every network tool. If you need round-trip case preservation, work with the parsed `MACAddress` object rather than re-parsing formatted strings.
