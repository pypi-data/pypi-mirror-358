import re


class ContractionToExpansion:
    """
    A class for expanding contractions in Creole Haitian text.
    """

    CONTRACTIONS_MAPPING = {
        "m": "mwen",
        "mw": "mwen",
        "n": "nou",
        "ka": "kapab",
        "l": "li",
        "potko": "te poko",
        "t": "te",
        "w": "ou",
        "fin": "fini",
        "sot": "soti",
        "k": "ki",
        "al": "ale",
        "y": "yo",
        "fèl": "fè li",
        "fèw": "fè ou",
        "nooo": "non",
        "wii": "wi",
        "konn": "konnen",
        "paka": "pa kapab",
        "diw": "di ou",
        "poum": "pou mwen",
        "pouw": "pou ou",
        "yok": "yo ki",
        "fèm": "fè mwen",
        "lap": "li ap",
        "wap": "ou ap",
        "yap": "yo ap",
        # "tap": "te ap",
        # "kap": "ki ap",
        # "nap": "nou ap",
    }

    @staticmethod
    def reduce_repeated_letters(text):
        return re.sub(r'(.)\1{2,}', r'\1', text)

    @staticmethod
    def expand_contractions(text, lowercase=True):
        """
        Expands contractions in the input text.

        Returns:
        str: Text with contractions expanded.
        """
        if not isinstance(text, str):
            return text

        if lowercase:
            text = text.lower()

        text = ContractionToExpansion.reduce_repeated_letters(text)
        text = text.replace("'", " ")

        for key, value in ContractionToExpansion.CONTRACTIONS_MAPPING.items():
            pattern = re.compile(r'\b' + re.escape(key) + r'\b', re.IGNORECASE)
            text = pattern.sub(value, text)

        return re.sub(r'\s+', ' ', text).strip()
