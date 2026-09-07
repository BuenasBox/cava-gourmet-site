"""Deterministic tests for scan.evaluate_scan_guard (Fase 0B.3, pure logic).

Run:  python -m unittest discover -s api/tests
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import scan  # noqa: E402

NOW = 1_000_000.0
CFG = {
    "cooldown_min": 30, "rate_window_min": 10, "rate_max_token": 30,
    "rate_max_ip": 60, "lockout_min": 15, "max_fails_token": 5, "max_fails_ip": 15,
}


def rows(*specs):
    """specs: (reason, minutes_ago) -> ledger rows."""
    return [{"reason": r, "ts": NOW - m * 60} for r, m in specs]


class ScanGuardToken(unittest.TestCase):
    def test_clean_allows(self):
        self.assertEqual(scan.evaluate_scan_guard(NOW, [], [], CFG), (True, "ok"))

    def test_success_cooldown_blocks(self):
        self.assertEqual(scan.evaluate_scan_guard(NOW, rows(("ok", 5)), [], CFG),
                         (False, "cooldown"))

    def test_cooldown_expires(self):
        self.assertEqual(scan.evaluate_scan_guard(NOW, rows(("ok", 45)), [], CFG),
                         (True, "ok"))

    def test_pin_lockout_at_threshold(self):
        self.assertEqual(scan.evaluate_scan_guard(NOW, rows(*[("bad_pin", 1)] * 5), [], CFG),
                         (False, "locked_token"))

    def test_pin_lockout_below_threshold(self):
        self.assertEqual(scan.evaluate_scan_guard(NOW, rows(*[("bad_pin", 1)] * 4), [], CFG),
                         (True, "ok"))

    def test_rate_checked_before_lockout(self):
        # 30 attempts in the 10-min window trips rate_token first
        self.assertEqual(scan.evaluate_scan_guard(NOW, rows(*[("bad_pin", 1)] * 30), [], CFG),
                         (False, "rate_token"))

    def test_stale_rows_ignored(self):
        self.assertEqual(scan.evaluate_scan_guard(NOW, rows(*[("bad_pin", 40)] * 20), [], CFG),
                         (True, "ok"))


class ScanGuardIP(unittest.TestCase):
    def test_none_ip_skips_ip_checks(self):
        self.assertEqual(scan.evaluate_scan_guard(NOW, [], None, CFG), (True, "ok"))

    def test_cross_token_rate(self):
        self.assertEqual(scan.evaluate_scan_guard(NOW, [], rows(*[("bad_pin", 1)] * 60), CFG),
                         (False, "rate_ip"))

    def test_cross_token_pin_lockout(self):
        # 15 bad PINs from one IP within the lockout window, under the ip rate cap
        self.assertEqual(scan.evaluate_scan_guard(NOW, [], rows(*[("bad_pin", 12)] * 15), CFG),
                         (False, "locked_ip"))

    def test_ip_lockout_below_threshold(self):
        self.assertEqual(scan.evaluate_scan_guard(NOW, [], rows(*[("bad_pin", 12)] * 14), CFG),
                         (True, "ok"))

    def test_token_limit_takes_precedence_over_ip(self):
        # token cooldown is evaluated before any IP check
        self.assertEqual(
            scan.evaluate_scan_guard(NOW, rows(("ok", 2)), rows(*[("bad_pin", 1)] * 100), CFG),
            (False, "cooldown"),
        )


class ScanGuardParseTs(unittest.TestCase):
    def test_parse_utc_offset(self):
        self.assertAlmostEqual(scan._parse_ts("2026-09-07T17:53:12.685+00:00"),
                               scan._parse_ts("2026-09-07T17:53:12.685Z"), places=3)

    def test_parse_naive_assumed_utc(self):
        a = scan._parse_ts("2026-09-07T17:53:12")
        b = scan._parse_ts("2026-09-07T17:53:12+00:00")
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
