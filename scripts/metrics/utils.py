import enchant
import re
import nltk
import spacy
import csv
from nltk.corpus import words
from nltk.stem import WordNetLemmatizer

# TODO
nltk.download("wordnet")
nltk.download("omw-1.4")

# Initialize PyEnchant spell checker
d = enchant.Dict("en_US")

# NLTK WordNet Lemmatizer
lemmatizer = WordNetLemmatizer()
word_list = set(words.words())

# SpaCy
nlp = spacy.load("en_core_web_sm")

# To handle cases where you might get false positives from lemmatization, such as
# with non-standard words or misspellings like "examplessss," you can incorporate
# a spell checker to first verify whether the word is close to any valid
# dictionary word before attempting to lemmatize and check it. This approach can
# help filter out obvious misspellings or non-words.

# One effective way to implement this is by using the PyEnchant library for spell
# checking in combination with either NLTK or SpaCy for lemmatization. Here’s how
# you could integrate spell checking into the process:

# This approach first uses PyEnchant to check if the input word is a recognized
# English word or close to one. If the word passes this initial spell check, it
# is then processed with lemmatization (using either NLTK or SpaCy) to find its
# root form and check against a list of known dictionary words.


def is_dict_word(word):
    # Check if the word is close to any valid dictionary word
    if d.check(word) or any(d.suggest(word)):
        # Try lemmatizing and checking the word with NLTK
        lemma_nltk = lemmatizer.lemmatize(word.lower())
        if lemma_nltk in word_list:
            return True

        # Try lemmatizing and checking the word with SpaCy
        doc = nlp(word.lower())
        lemma_spacy = [token.lemma_ for token in doc][0]  # Get lemma of the first token
        if lemma_spacy in word_list:
            return True

    # If neither check passes, the word is not valid
    return False


def load_abbreviations(file_path: str) -> set:
    first_column_values = set()

    with open(file_path, mode="r", newline="") as csvfile:
        reader = csv.reader(csvfile)

        # Optionally skip the header if your CSV file has one
        # next(reader, None)  # Uncomment this line if there's a header

        for row in reader:
            if row:  # Ensure the row is not empty
                first_column_values.add(row[0])

    return first_column_values


def split_compound(word):
    original = word

    # Check if the word is in all uppercase (considering acronyms or similar cases)
    if word.isupper():
        word = re.sub(r"[_\-]+", " ", word)  # Only split snake_case and kebab-case
    else:
        # Split snake_case and kebab-case
        word = re.sub(r"[_\-]+", " ", word)
        # Split camelCase and PascalCase, considering all uppercase scenario
        word = re.sub(r"(?<!^)(?=[A-Z])", " ", word)

    # Normalize spaces and split, convert to lowercase for consistency
    compounds = re.sub(r"\s+", " ", word).strip().lower().split(" ")
    # console.print(f'\'{original}\' -> {compounds}', style='red')

    return tuple(compounds)
