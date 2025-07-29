import unittest
from creolenltk import NumberConverter


class TestNumberConverter(unittest.TestCase):

    def setUp(self):
        self.converter = NumberConverter()

    def test_cardinal_units(self):
        self.assertEqual(self.converter.number_to_word(0), "zewo")
        self.assertEqual(self.converter.number_to_word(1), "en")
        self.assertEqual(self.converter.number_to_word(9), "nèf")

    def test_cardinal_tens(self):
        self.assertEqual(self.converter.number_to_word(10), "dis")
        self.assertEqual(self.converter.number_to_word(22), "vennde")
        self.assertEqual(self.converter.number_to_word(35), "tannsenk")
        self.assertEqual(self.converter.number_to_word(93), "katreventrèz")

    def test_cardinal_hundreds_thousands(self):
        self.assertEqual(self.converter.number_to_word(100), "san")
        self.assertEqual(self.converter.number_to_word(101), "san en")
        self.assertEqual(self.converter.number_to_word(215), "de san kenz")
        self.assertEqual(self.converter.number_to_word(
            1234), "mil de san trannkat")
        self.assertEqual(self.converter.number_to_word(
            2025), "de mil vennsenk")

    def test_cardinal_million_billion(self):
        self.assertEqual(self.converter.number_to_word(1_000_000), "en milyon")
        self.assertEqual(self.converter.number_to_word(
            2_500_000), "de milyon senk san mil")
        self.assertEqual(self.converter.number_to_word(
            1_000_000_000), "en milya")
        self.assertEqual(self.converter.number_to_word(
            1_000_000_001), "en milya en")

    def test_ordinal_units(self):
        self.assertEqual(self.converter.number_to_ordinal(1), "premye")
        self.assertEqual(self.converter.number_to_ordinal(2), "dezyèm")
        self.assertEqual(self.converter.number_to_ordinal(9), "nevyèm")

    def test_ordinal_tens(self):
        self.assertEqual(self.converter.number_to_ordinal(12), "douzyèm")
        self.assertEqual(self.converter.number_to_ordinal(30), "trantyèm")
        self.assertEqual(self.converter.number_to_ordinal(45), "karannsenkyèm")
        self.assertEqual(self.converter.number_to_ordinal(91), "katevenonzyèm")

    def test_ordinal_large(self):
        self.assertEqual(self.converter.number_to_ordinal(100), "santyèm")
        self.assertEqual(self.converter.number_to_ordinal(1000), "milyèm")
        self.assertEqual(self.converter.number_to_ordinal(
            1_000_000), "milyonyèm")
        self.assertEqual(self.converter.number_to_ordinal(
            1_000_000_000), "milyadyèm")

    def test_replace_cardinals_in_text(self):
        text = "Mwen genyen 3 chat ak 21 ti chen."
        expected = "Mwen genyen twa chat ak venteyen ti chen."
        self.assertEqual(
            self.converter.replace_cardinals_in_text(text), expected)

    def test_replace_ordinals_in_text(self):
        text = "Li te fini 3yèm nan kous la, men li te 21yèm nan klasman an."
        expected = "Li te fini twazyèm nan kous la, men li te venteyinyèm nan klasman an."
        self.assertEqual(
            self.converter.replace_ordinals_in_text(text), expected)


if __name__ == '__main__':
    unittest.main()
