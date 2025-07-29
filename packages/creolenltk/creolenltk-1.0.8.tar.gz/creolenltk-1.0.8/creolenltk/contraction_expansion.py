import re
from .pos.pos_tagger import PosTagger


class ContractionToExpansion:
    """
    Expands contractions in Haitian Creole, resolving ambiguous forms using POS and context.
    """

    CONTRACTIONS_MAPPING = {
        "fèw": "fè ou", "fèl": "fè li", "poum": "pou mwen", "pouw": "pou ou", "fèm": "fè mwen",
        "lap": "li ap", "wap": "ou ap", "yap": "yo ap", "tap": "te ap", "kap": "ki ap", "nap": "nou ap",
        "potko": "te poko", "fin": "fini", "sot": "soti", "ka": "kapab",
        "al": "ale", "k": "ki",
        "nooon": "non", "wii": "wi", "konn": "konnen", "paka": "pa kapab", "diw": "di ou",
        "yok": "yo ki",
        "m": "mwen", "mw": "mwen", "n": "nou", "l": "li", "t": "te", "w": "ou", "y": "yo",
    }
    AMBIGUOUS_SHORTS = {"fèm", "lap", "wap", "yap", "tap", "kap", "nap"}

    def __init__(self, tagger=None):
        self.tagger = tagger or PosTagger()

    @staticmethod
    def reduce_repeated_letters(text):
        """Reduces three or more repeated letters to a single letter."""
        return re.sub(r'(.)\1{2,}', r'\1', text)

    def expand_contractions(self, text, lowercase=True):
        """
        Expands contractions in input text using context.
        Args:
            text (str): Input sentence.
            lowercase (bool): Whether to lowercase input.
        Returns:
            str: Expanded sentence.
        """
        if not isinstance(text, str):
            return text

        if lowercase:
            text = text.lower()
        text = self.reduce_repeated_letters(text)
        text = text.replace("'", " ")

        doc = self.tagger.nlp(text)
        tokens_out = []

        for i, token in enumerate(doc):
            word = token.text
            if word in self.AMBIGUOUS_SHORTS:
                # Expand if next word is a verb, otherwise leave as is
                next_is_verb = (
                    i + 1 < len(doc)) and (doc[i + 1].tag_ == "VERB")
                if next_is_verb:
                    tokens_out.append(
                        self.CONTRACTIONS_MAPPING.get(word, word))
                else:
                    tokens_out.append(word)
            else:
                tokens_out.append(self.CONTRACTIONS_MAPPING.get(word, word))

        expanded_text = ' '.join(tokens_out)

        expanded_text = re.sub(r'\s+([,;.!?])', r'\1', expanded_text)
        return expanded_text
