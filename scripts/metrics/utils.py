import csv
import re

import enchant
import nltk
import spacy
from nltk.corpus import words
from nltk.stem import WordNetLemmatizer

d = enchant.Dict("en_US")

lemmatizer = WordNetLemmatizer()
word_list = set(words.words())


def is_dict_word(word):
    lemma_nltk = lemmatizer.lemmatize(word.lower())

    if lemma_nltk in word_list:
        return True

    return d.check(lemma_nltk)


def load_abbreviations(file_path: str) -> dict:
    abbreviations = {}

    with open(file_path, newline="") as csvfile:
        reader = csv.reader(csvfile)

        for row in reader:
            value, key = row
            if key in abbreviations:
                abbreviations[key].add(value)
            else:
                abbreviations[key] = set([value])

    return abbreviations


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
