import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag

def classify_words(paragraph):
    # Tokenize the paragraph into words
    words = word_tokenize(paragraph)
    
    # Tag each word with its part of speech
    tagged_words = pos_tag(words)
    
    # Initialize dictionaries to store words of different categories
    categories = {
        'nouns': [],
        'verbs': [],
        'adjectives': [],
        'adverbs': [],
        'pronouns': [],
        'prepositions': [],
        'conjunctions': [],
        'interjections': [],
        'others': []
    }
    
    # Classify words into different categories based on their POS tags
    for word, pos in tagged_words:
        if pos.startswith('NN'):  # Noun
            categories['nouns'].append(word)
        elif pos.startswith('VB'):  # Verb
            categories['verbs'].append(word)
        elif pos.startswith('JJ'):  # Adjective
            categories['adjectives'].append(word)
        elif pos.startswith('RB'):  # Adverb
            categories['adverbs'].append(word)
        elif pos.startswith('PR'):  # Pronoun
            categories['pronouns'].append(word)
        elif pos.startswith('IN'):  # Preposition
            categories['prepositions'].append(word)
        elif pos.startswith('CC'):  # Conjunction
            categories['conjunctions'].append(word)
        elif pos.startswith('UH'):  # Interjection
            categories['interjections'].append(word)
        else:
            categories['others'].append(word)
    
    return categories

# Get user input for the paragraph
paragraph = input("Enter your paragraph: ")

# Classify words in the paragraph
word_categories = classify_words(paragraph)

# Print words in each category
for category, words in word_categories.items():
    print(category + ':', words)