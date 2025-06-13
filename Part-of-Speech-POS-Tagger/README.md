# 🧠 Part-of-Speech (POS) Tagger

This project is a simple Python script that takes a paragraph as input and classifies the words into different parts of speech (POS) such as nouns, verbs, adjectives, etc., using the Natural Language Toolkit (NLTK).

## 📌 Features

- Tokenizes a paragraph into individual words
- Tags each word with its corresponding part of speech
- Categorizes words into:
  - Nouns
  - Verbs
  - Adjectives
  - Adverbs
  - Pronouns
  - Prepositions
  - Conjunctions
  - Interjections
  - Others

## 🚀 Getting Started

### Prerequisites

- Python 3.x
- [NLTK](https://www.nltk.org/) library

You can install the required library using pip:

```bash
pip install nltk
```

### Run the Script

```bash
python Part-Of-Speech.py
```

You'll be prompted to enter a paragraph. The script will then display the words grouped by their part-of-speech categories.

## 📂 Example

**Input:**

```
Enter your paragraph: The quick brown fox jumps over the lazy dog and shouts, "Wow!"
```

**Output:**
```
nouns: ['fox', 'dog']
verbs: ['jumps']
adjectives: ['quick', 'brown', 'lazy']
adverbs: []
pronouns: []
prepositions: ['over']
conjunctions: ['and']
interjections: ['Wow']
others: ['The', 'the', 'shouts', ', ', '"', '!']
```

## 📚 Built With

- [Python](https://www.python.org/)
- [NLTK](https://www.nltk.org/)
