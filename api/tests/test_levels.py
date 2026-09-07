"""Tests for api/_levels.py (Fase 2.1)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import _levels  # noqa: E402


class Levels(unittest.TestCase):
    def test_tiers(self):
        self.assertEqual(_levels.calcular_nivel(0), "🚪 Invitado")
        self.assertEqual(_levels.calcular_nivel(2), "🚪 Invitado")
        self.assertEqual(_levels.calcular_nivel(3), "🌱 Neófito")
        self.assertEqual(_levels.calcular_nivel(9), "🌱 Neófito")
        self.assertEqual(_levels.calcular_nivel(10), "🍷 Entusiasta")
        self.assertEqual(_levels.calcular_nivel(24), "🍷 Entusiasta")
        self.assertEqual(_levels.calcular_nivel(25), "🍷 Entusiasta")

    def test_enofilo_only_at_25_with_flag(self):
        self.assertEqual(_levels.calcular_nivel(25, es_enofilo=True), "🔐 Enófilo")
        self.assertEqual(_levels.calcular_nivel(24, es_enofilo=True), "🍷 Entusiasta")
        self.assertEqual(_levels.calcular_nivel(25, es_enofilo=False), "🍷 Entusiasta")


if __name__ == "__main__":
    unittest.main()
