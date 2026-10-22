"""Unit tests for mini_mac_address.core.

Run with:  PYTHONPATH=src python -m unittest discover -s tests
"""

import unittest

from mini_mac_address import MACAddress, MACParseError, format_mac, parse_mac


class TestParseHappyPath(unittest.TestCase):
    def test_colon_notation(self):
        mac = parse_mac("aa:bb:cc:dd:ee:ff")
        self.assertEqual(mac.raw, "AABBCCDDEEFF")
        self.assertEqual(mac.octets, ("AA", "BB", "CC", "DD", "EE", "FF"))

    def test_hyphen_notation(self):
        mac = parse_mac("11-22-33-44-55-66")
        self.assertEqual(mac.raw, "112233445566")

    def test_dot_notation_cisco_dotted(self):
        mac = parse_mac("aabb.ccdd.eeff")
        self.assertEqual(mac.octets, ("AA", "BB", "CC", "DD", "EE", "FF"))
        self.assertEqual(mac.raw, "AABBCCDDEEFF")

    def test_raw_hex_notation(self):
        mac = parse_mac("aabbccddeeff")
        self.assertEqual(mac.raw, "AABBCCDDEEFF")

    def test_uppercase_input_preserved_as_upper(self):
        mac = parse_mac("AA:BB:CC:DD:EE:FF")
        self.assertEqual(mac.octets[0], "AA")

    def test_strips_surrounding_whitespace(self):
        mac = parse_mac("  aa:bb:cc:dd:ee:ff  \n")
        self.assertEqual(mac.raw, "AABBCCDDEEFF")


class TestParseErrors(unittest.TestCase):
    def test_empty_string(self):
        with self.assertRaises(MACParseError):
            parse_mac("")

    def test_whitespace_only(self):
        with self.assertRaises(MACParseError):
            parse_mac("   \t  ")

    def test_non_string_input(self):
        with self.assertRaises(MACParseError):
            parse_mac(None)  # type: ignore[arg-type]

    def test_too_short(self):
        with self.assertRaises(MACParseError):
            parse_mac("aa:bb:cc")

    def test_too_long(self):
        with self.assertRaises(MACParseError):
            parse_mac("aa:bb:cc:dd:ee:ff:11")

    def test_invalid_hex_characters(self):
        with self.assertRaises(MACParseError):
            parse_mac("gg:bb:cc:dd:ee:ff")

    def test_mixed_separators_rejected(self):
        with self.assertRaises(MACParseError):
            parse_mac("aa:bb-cc:dd:ee:ff")

    def test_wrong_grouping_for_dot(self):
        # Dotted notation must be groups of four hex digits, not pairs.
        with self.assertRaises(MACParseError):
            parse_mac("aa.bb.cc.dd.ee.ff")

    def test_eui64_length_rejected(self):
        # 16 hex digits is EUI-64, explicitly out of scope.
        with self.assertRaises(MACParseError):
            parse_mac("aa:bb:cc:dd:ee:ff:aa:bb")


class TestFormat(unittest.TestCase):
    def test_format_default_colon(self):
        self.assertEqual(format_mac("aabbccddeeff"), "AA:BB:CC:DD:EE:FF")

    def test_format_colon(self):
        self.assertEqual(format_mac("aabb.ccdd.eeff", ":"), "AA:BB:CC:DD:EE:FF")

    def test_format_hyphen(self):
        self.assertEqual(format_mac("aa:bb:cc:dd:ee:ff", "-"), "AA-BB-CC-DD-EE-FF")

    def test_format_dot(self):
        self.assertEqual(format_mac("aa:bb:cc:dd:ee:ff", "."), "AABB.CCDD.EEFF")

    def test_format_raw(self):
        self.assertEqual(format_mac("aa:bb:cc:dd:ee:ff", ""), "AABBCCDDEEFF")

    def test_format_unsupported_separator(self):
        with self.assertRaises(ValueError):
            format_mac("aa:bb:cc:dd:ee:ff", "/")


class TestRoundTrip(unittest.TestCase):
    def test_round_trip_all_notations(self):
        original = "aa:bb:cc:dd:ee:ff"
        mac = parse_mac(original)
        for sep in (":", "-", ".", ""):
            formatted = mac.format(sep)
            reparsed = parse_mac(formatted)
            self.assertEqual(reparsed.raw, mac.raw)

    def test_macaddress_is_immutable(self):
        mac = parse_mac("aa:bb:cc:dd:ee:ff")
        with self.assertRaises(Exception):
            # frozen dataclass raises FrozenInstanceError (subclass of AttributeError).
            mac.octets = ("11", "22", "33", "44", "55", "66")  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
