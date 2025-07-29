import unittest
from creolenltk import PosTagger


class TestPosTagger(unittest.TestCase):
    def setUp(self):
        self.tagger = PosTagger()

    def test_basic_sentence(self):
        text = "Mwen renmen Ayiti anpil."
        result = self.tagger.tag(text)
        self.assertTrue(isinstance(result, list))
        self.assertEqual(len(result), 5)
        self.assertEqual(result[0][0], "Mwen")  
        self.assertTrue(isinstance(result[0][1], str))

    def test_question(self):
        text = "Poukisa panse yo chanje?"
        result = self.tagger.tag(text)
        self.assertEqual(result[-1][0], "?")  
        self.assertTrue(
            all(isinstance(tag, str) and tag for word, tag in result))

    def test_longer_sentence(self):
        text = "Li sitou enpòtan pou kretyen selibatè ki vle marye yo veye."
        result = self.tagger.tag(text)
        self.assertTrue(len(result) >= 10)
        self.assertTrue(any(word == "Li" for word, tag in result))

    def test_no_empty_tags(self):
        text = "Mwen renmen pale Kreyòl."
        result = self.tagger.tag(text)
        self.assertTrue(all(tag for word, tag in result))


if __name__ == "__main__":
    unittest.main()
