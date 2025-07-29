import re
from .number_dict import ten_cardinal, ten_ordinal


class NumberConverter:
    """
    Converts numbers to Haitian Creole words (cardinal and ordinal),
    with full accuracy based on linguistic rules and lookup dictionaries.
    """

    # Base constants
    ZERO = "zewo"
    HUNDRED = "san"
    THOUSAND = "mil"
    MILLION = "milyon"
    BILLION = "milya"

    HUNDRED_ORD = "santyèm"
    THOUSAND_ORD = "milyèm"
    MILLION_ORD = "milyonyèm"
    BILLION_ORD = "milyadyèm"

    unit_cardinal = {
        1: 'en', 2: 'de', 3: 'twa', 4: 'kat', 5: 'senk',
        6: 'sis', 7: 'sèt', 8: 'uit', 9: 'nèf'
    }

    unit_ordinal = {
        1: 'premye', 2: 'dezyèm', 3: 'twazyèm', 4: 'katriyèm', 5: 'senkyèm',
        6: 'sizyèm', 7: 'sètyèm', 8: 'uityèm', 9: 'nevyèm'
    }

    def __init__(self):
        self.ten_cardinal = ten_cardinal
        self.ten_ordinal = ten_ordinal

    def number_to_word(self, n: int) -> str:
        if n < 0:
            return "mwens " + self.number_to_word(-n)
        if n == 0:
            return self.ZERO
        if n <= 9:
            return self.unit_cardinal[n]
        if 10 <= n <= 99:
            return self.ten_cardinal.get(n, str(n))
        if 100 <= n < 200:
            rest = n - 100
            return self.HUNDRED if rest == 0 else f"{self.HUNDRED} {self.number_to_word(rest)}"
        if n < 1000:
            hundreds = n // 100
            rest = n % 100
            hundreds_word = f"{self.unit_cardinal[hundreds]} {self.HUNDRED}"
            return hundreds_word + (f" {self.number_to_word(rest)}" if rest else "")
        if n < 1_000_000:
            return self._chunk_to_words(n, 1000, self.THOUSAND)
        if n < 1_000_000_000:
            return self._chunk_to_words(n, 1_000_000, self.MILLION)
        return self._chunk_to_words(n, 1_000_000_000, self.BILLION)

    def number_to_ordinal(self, n: int) -> str:
        """Ordinal numbers like 22 → venndezyèm"""
        if n <= 9:
            return self.unit_ordinal[n]
        if 10 <= n <= 99:
            return self.ten_ordinal.get(n, self.number_to_word(n) + "yèm")
        if 100 <= n < 1000:
            if n == 100:
                return self.HUNDRED_ORD
            return self.number_to_word(n) + "yèm"
        if n < 1_000_000:
            if n % 1000 == 0:
                return self.THOUSAND_ORD
            return self.number_to_word(n) + "yèm"
        if n < 1_000_000_000:
            if n % 1_000_000 == 0:
                return self.MILLION_ORD
            return self.number_to_word(n) + "yèm"
        return self.BILLION_ORD if n % 1_000_000_000 == 0 else self.number_to_word(n) + "yèm"

    def _chunk_to_words(self, n: int, divisor: int, word: str) -> str:
        major = n // divisor
        rest = n % divisor

        # Use only "mil" (not "en mil") when major == 1 and it's a thousand
        if major == 1 and word == self.THOUSAND:
            result = word
        elif major == 1:
            result = f"{self.unit_cardinal[1]} {word}"
        else:
            result = f"{self.number_to_word(major)} {word}"

        if rest:
            result += f" {self.number_to_word(rest)}"

        return result

    def replace_cardinals_in_text(self, text: str) -> str:
        return re.sub(r'\b\d+\b', lambda m: self.number_to_word(int(m.group())), text)

    def replace_ordinals_in_text(self, text: str) -> str:
        return re.sub(r'\b(\d+)yèm\b', lambda m: self.number_to_ordinal(int(m.group(1))), text)
