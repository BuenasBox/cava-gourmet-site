"""Deterministic tests for api/_member_token.py (Fase 0B.4).

Run:  python -m unittest discover -s api/tests
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import _member_token as mt  # noqa: E402

SECRET = "test-hmac-secret-0B4"
NOW = 1_800_000_000  # fixed reference epoch (well before any real sunset)


def _flip_last(s):
    return s[:-1] + ("0" if s[-1] != "0" else "1")


class MemberTokenV1(unittest.TestCase):
    def setUp(self):
        mt.HMAC_SECRET, mt._SALT = SECRET, ""
        mt._V2_ENABLED, mt._V1_SUNSET = False, ""

    def test_valid_roundtrip(self):
        t = mt.generar_token("a@b.co")
        self.assertFalse(t.startswith("v2."))
        self.assertTrue(mt.validar_token("a@b.co", t, now=NOW))

    def test_wrong_email(self):
        t = mt.generar_token("a@b.co")
        self.assertFalse(mt.validar_token("z@b.co", t, now=NOW))

    def test_tampered(self):
        t = mt.generar_token("a@b.co")
        self.assertFalse(mt.validar_token("a@b.co", _flip_last(t), now=NOW))

    def test_empty_token(self):
        self.assertFalse(mt.validar_token("a@b.co", "", now=NOW))

    def test_no_secret(self):
        mt.HMAC_SECRET = ""
        self.assertEqual(mt.generar_token("a@b.co"), "")
        self.assertFalse(mt.validar_token("a@b.co", "deadbeef", now=NOW))

    def test_sunset_rejects_v1_after_date(self):
        v1 = mt._v1_sig("a@b.co")
        mt._V1_SUNSET = "2020-01-01"
        self.assertFalse(mt.validar_token("a@b.co", v1, now=NOW))
        mt._V1_SUNSET = "2099-01-01"
        self.assertTrue(mt.validar_token("a@b.co", v1, now=NOW))


class MemberTokenV2(unittest.TestCase):
    def setUp(self):
        mt.HMAC_SECRET, mt._SALT = SECRET, "salt-A"
        mt._V2_ENABLED, mt._V1_SUNSET = True, ""

    def test_valid(self):
        t = mt.generar_token_v2("a@b.co", ttl_days=120, now=NOW)
        self.assertTrue(t.startswith("v2."))
        self.assertTrue(mt.validar_token("a@b.co", t, now=NOW))

    def test_issued_by_generar_token_when_enabled(self):
        self.assertTrue(mt.generar_token("a@b.co").startswith("v2."))

    def test_expired(self):
        t = mt.generar_token_v2("a@b.co", ttl_days=1, now=NOW)
        self.assertFalse(mt.validar_token("a@b.co", t, now=NOW + 2 * 86400))

    def test_tampered_sig(self):
        p = mt.generar_token_v2("a@b.co", now=NOW).split(".")
        self.assertFalse(mt.validar_token("a@b.co", f"{p[0]}.{p[1]}.{_flip_last(p[2])}", now=NOW))

    def test_tampered_exp_extends_but_sig_fails(self):
        p = mt.generar_token_v2("a@b.co", ttl_days=1, now=NOW).split(".")
        forged = f"{p[0]}.{int(p[1]) + 10_000_000}.{p[2]}"
        self.assertFalse(mt.validar_token("a@b.co", forged, now=NOW))

    def test_wrong_email(self):
        t = mt.generar_token_v2("a@b.co", now=NOW)
        self.assertFalse(mt.validar_token("z@b.co", t, now=NOW))

    def test_malformed(self):
        for bad in ("v2.", "v2.abc.def", "v2.123", "v2.1.2.3"):
            self.assertFalse(mt.validar_token("a@b.co", bad, now=NOW))

    def test_salt_rotation_revokes_all_v2(self):
        t = mt.generar_token_v2("a@b.co", now=NOW)
        self.assertTrue(mt.validar_token("a@b.co", t, now=NOW))
        mt._SALT = "salt-B"
        self.assertFalse(mt.validar_token("a@b.co", t, now=NOW))


class MemberTokenGracePeriod(unittest.TestCase):
    """The rollout invariant: turning V2 issuance on must not break V1 links."""

    def setUp(self):
        mt.HMAC_SECRET, mt._SALT, mt._V1_SUNSET = SECRET, "salt-A", ""

    def test_v1_link_survives_v2_activation(self):
        mt._V2_ENABLED = False
        v1 = mt.generar_token("a@b.co")            # link handed out before the flip
        mt._V2_ENABLED = True                       # operator sets MEMBER_TOKEN_V2=1
        self.assertTrue(mt.generar_token("a@b.co").startswith("v2."))  # new links: V2
        self.assertTrue(mt.validar_token("a@b.co", v1, now=NOW))       # old link: still ok

    def test_v1_link_dies_after_sunset(self):
        mt._V2_ENABLED = True
        v1 = mt._v1_sig("a@b.co")
        mt._V1_SUNSET = "2020-06-01"
        self.assertFalse(mt.validar_token("a@b.co", v1, now=NOW))


if __name__ == "__main__":
    unittest.main()
