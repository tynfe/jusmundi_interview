import unittest

from src.transform.transform import number_to_french_text


class TestNumberToFrenchText(unittest.TestCase):

    def test_units(self):
        self.assertEqual(number_to_french_text(0), "zéro")
        self.assertEqual(number_to_french_text(1), "un")
        self.assertEqual(number_to_french_text(9), "neuf")

    def test_teens(self):
        self.assertEqual(number_to_french_text(10), "dix")
        self.assertEqual(number_to_french_text(13), "treize")
        self.assertEqual(number_to_french_text(16), "seize")

    def test_tens(self):
        self.assertEqual(number_to_french_text(20), "vingt")
        self.assertEqual(number_to_french_text(21), "vingt-et-un")
        self.assertEqual(number_to_french_text(25), "vingt-cinq")
        self.assertEqual(number_to_french_text(30), "trente")
        self.assertEqual(number_to_french_text(37), "trente-sept")

    def test_soixante(self):
        self.assertEqual(number_to_french_text(70), "septante")
        self.assertEqual(number_to_french_text(71), "soixante-et-onze")
        self.assertEqual(number_to_french_text(79), "soixante-dix-neuf")

    def test_quatre_vingt(self):
        self.assertEqual(number_to_french_text(80), "huitante")
        self.assertEqual(number_to_french_text(90), "nonante")
        self.assertEqual(number_to_french_text(85), "quatre-vingt-cinq")
        self.assertEqual(number_to_french_text(91), "quatre-vingt-onze")
        self.assertEqual(number_to_french_text(99), "quatre-vingt-dix-neuf")

    def test_hundreds(self):
        self.assertEqual(number_to_french_text(100), "cent")
        self.assertEqual(number_to_french_text(101), "cent-un")
        self.assertEqual(number_to_french_text(200), "deux-cents")
        self.assertEqual(number_to_french_text(253), "deux-cent-cinquante-trois")
        self.assertEqual(number_to_french_text(999), "neuf-cent-quatre-vingt-dix-neuf")

    def test_thousands(self):
        self.assertEqual(number_to_french_text(1000), "mille")
        self.assertEqual(number_to_french_text(2000), "deux-mille")
        self.assertEqual(number_to_french_text(2023), "deux-mille-vingt-trois")
        self.assertEqual(
            number_to_french_text(9999), "neuf-mille-neuf-cent-quatre-vingt-dix-neuf"
        )
