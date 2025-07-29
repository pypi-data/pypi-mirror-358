# CreoleNLTK: Creole Natural Language Toolkit

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue)](https://www.python.org/downloads/)
[![Build Status](https://travis-ci.org/jcblanc2/CreoleNLTK.svg?branch=main)](https://travis-ci.org/jcblanc2/CreoleNLTK)

CreoleNLTK is a Python library designed for preprocessing Creole text. The library includes various functions and tools to prepare text data for natural language processing (NLP) tasks. It provides functionality for cleaning, tokenization, lowercasing, stopword removal, contraction to expansion, and spelling checking.

## Features

- **Spelling Check:** Identify and correct spelling errors.
- **Contraction to Expansion:** Expand contractions in the text.
- **Stopword Removal:** Remove common words that do not contribute much to the meaning.
- **Tokenization:** Break the text into words or tokens.
- **Text Cleaning:** Remove unwanted characters and clean the text.

## Installation

You can install CreoleNLTK using pip:

```bash
pip install creolenltk
```

## Usage

### Spelling Checker

```python
from creolenltk.spelling_checker import SpellingChecker

# Initialize the spelling checker
spell_checker = SpellingChecker()

# Correct spelling errors in a word
corrected_word = spell_checker.correction('òtgraf')

print(f"Original Word: òtgraf, Corrected Word: {corrected_word}") # òtograf
```

### Number to Words (Cardinal and Ordinal)

```python
from creolenltk.num2word import CreoleNumberConverter

# Initialize the number converter
num_converter = CreoleNumberConverter()

# Convert numbers to cardinal words
print(num_converter.number_to_word(2024))  # de mil venntkat

# Convert numbers to ordinal words
print(num_converter.number_to_ordinal(21))  # venteyinyèm

# Replace numbers in text with cardinal form
text = "Mwen genyen 3 chat ak 21 ti chen."
converted = num_converter.replace_cardinals_in_text(text)
print(converted)  # Mwen genyen twa chat ak venteyen ti chen.
```

### Part-of-Speech Tagging

```python
from creolenltk.pos_tagger import PosTagger

# Initialize the POS tagger (uses the trained Creole model)
tagger = PosTagger()

sentence = "Mwen renmen Ayiti anpil."
tags = tagger.tag(sentence)
print(tags)  # [('Mwen', 'PRON'), ('renmen', 'VERB'), ('Ayiti', 'PROPN'), ('anpil', 'ADV'), ('.', 'PUNCT')]

sentence2 = "Poukisa panse yo chanje?"
tags2 = tagger.tag(sentence2)
print(tags2)  # [('Poukisa', 'ADV'), ('panse', 'VERB'), ('yo', 'PRON'), ('chanje', 'VERB'), ('?', 'PUNCT')]
```

### Contraction to Expansion

```python
from creolenltk.contraction_expansion import ContractionToExpansion

# Initialize the contraction expander
contraction_expander = ContractionToExpansion()

# Expand contractions in a sentence
original_sentence = "L'ap manje. m'ap rete lakay mw."
expanded_sentence = contraction_expander.expand_contractions(original_sentence)

print(f"Original Sentence: {original_sentence}\nExpanded Sentence: {expanded_sentence}") # li ap manje. mwen ap rete lakay mwen.
```

### Stopword Removal

```python
from creolenltk.stopword import Stopword

# Initialize the stopword handler
stopword_handler = Stopword()

# Remove stopwords from a sentence
sentence_with_stopwords = "Sa se yon fraz tès ak kèk stopwords nan Kreyòl Ayisyen."
sentence_without_stopwords = stopword_handler.remove_stopwords(sentence_with_stopwords)

print(f"Sentence with Stopwords: {sentence_with_stopwords}\nWithout Stopwords: {sentence_without_stopwords}") # fraz tès stopwords Kreyòl Ayisyen.
```

### Tokenizer

```python
from creolenltk.tokenizer import Tokenizer

# Initialize the tokenizer
tokenizer = Tokenizer()

# Tokenize a sentence
sentence = "Sa se yon fraz senp"
tokens = tokenizer.word_tokenize(sentence, expand_contractions=True, lowercase=True)

print(f"Sentence: {sentence}\nTokens: {tokens}") # ["sa", "se", "yon", "fraz", "senp"]
```

For more detailed usage and examples, refer to the [documentation](https://pypi.org/project/creolenltk/).

## License

MIT licensed. See the bundled [LICENSE](LICENSE) file for more details.
