import csv
import itertools
import os
import sys
from itertools import combinations
from collections import Counter
from multiprocessing import Pool
from os import path
from statistics import median

import casestyle
import syllapy
import wordninja
from Levenshtein import distance as levenshtein_distance
from nltk.tokenize import RegexpTokenizer
from rich.console import Console

from db.models import Function, Repo
from db.utils import (commit, get_functions_for_repo, get_repos,
                      init_local_session, update_function_metrics)

from ..utils import unique_pairs
from .cc import get_conciseness_and_consistency
from .context_coverage import get_context_coverage
from .external_similarity import get_external_similarity
from .utils import is_dict_word, load_abbreviations, split_compound

csv.field_size_limit(sys.maxsize)
console = Console()


def get_median_length(names):
    return median([len(name) for name in names])


def get_syllable_count(identifier):
    softwords = casestyle.casepreprocess(identifier)
    syllables = sum([syllapy.count(word) for word in softwords])
    return syllables


def get_soft_words(identifier):
    return casestyle.casepreprocess(identifier.strip("_"))


def get_num_abbreviations(abbreviations, softwords):
    count = 0

    for word in softwords:
        if (not is_dict_word(word) or len(word) == 1) and word in abbreviations:
            count += 1

    return count


def get_num_dictionary_words(words):
    count = 0

    for word in words:
        if len(word) > 1 and is_dict_word(word):
            count += 1

    return count


def get_median_levenshtein_distance(word_pairs):
    distances = []

    for pair in word_pairs:
        word1, word2 = pair
        distances.append(levenshtein_distance(word1, word2))

    if len(distances) > 0:
        return median(distances)
    else:
        return None


def calculate_context_coverage():
    session = init_local_session()
    count = 0

    for repo in Repo.all(session, selected=True):
        console.print(f"Calculating context coverage for {repo.name}", style="red")
        all_names = set()
        all_function_bodies = []
        functions = Function.filter_by(session, repo_id=repo.id)

        functions = [
            function
            for function in functions
            if (function.name and "test" not in function.name)
        ]

        count = sum(
            1 for function in functions if function.context_coverage is not None
        )
        console.print(
            f"Found {len(functions)} functions and {count} functions with context coverage",
            style="red",
        )

        if count >= 2000 or count >= len(functions):
            continue

        functions = functions[:2000]

        for function in functions:
            names = function.names.split(" ")
            all_function_bodies.append(names)
            all_names.update(names[:20])

        all_names = list(all_names)

        if len(all_names) == 0 or len(all_function_bodies) == 0:
            continue

        values = get_context_coverage(all_function_bodies, all_names)

        for function in functions:
            console.print(
                f"Calculating context coverage for {function.name}", style="yellow"
            )
            names = function.names.split(" ")[:20]
            scores = []

            for name, value in values.items():
                if name in names:
                    scores.append(value)

            if len(scores) > 0:
                function.context_coverage = float(median(scores))
                session.commit()


def get_duplicate_percentage(names):
    word_counts = Counter(names)
    duplicate_count = sum(1 for count in word_counts.values() if count > 1)
    total_words = len(word_counts.keys())

    if total_words == 0:
        return 0.0

    return duplicate_count / total_words


def calculate_basic_metrics_for_repo(repo_id):
    session = init_local_session()
    abbreviations = load_abbreviations("build/abbreviations.csv")
    count = 0

    for function in Function.filter_by(session, repo_id=repo_id):
        names = function.names.split(" ")
        metrics = get_basic_metrics(names, abbreviations)
        count += 1

        for key, value in metrics.items():
            setattr(function, key, value)

        session.commit()


def calculate_basic_metrics():
    session = init_local_session()
    for repo in Repo.all(session, selected=True):
        calculate_basic_metrics_for_repo(repo.id)


def get_basic_metrics(names, abbreviations):
    metrics = {}

    metrics["median_id_length"] = get_median_length(names)

    syllable_counts = [get_syllable_count(name) for name in names]
    metrics["median_id_syllable_count"] = median(syllable_counts)

    soft_word_counts = [len(get_soft_words(name)) for name in names]
    metrics["median_id_soft_word_count"] = median(soft_word_counts)

    metrics["id_duplicate_percentage"] = get_duplicate_percentage(names)

    single_letter_names = [name for name in names if len(name) == 1]
    metrics["num_single_letter_ids"] = len(single_letter_names)

    console.print(f"Calculating abbreviations")
    soft_words = [word for name in names for word in get_soft_words(name)]
    if len(soft_words) > 0:
        metrics["id_percent_abbreviations"] = get_num_abbreviations(
            abbreviations, soft_words
        ) / len(soft_words)

    console.print(f"Calculating dictionary words")
    if len(soft_words) > 0:
        metrics["id_percent_dictionary_words"] = get_num_dictionary_words(
            soft_words
        ) / len(soft_words)
    else:
        metrics["id_percent_dictionary_words"] = 0

    console.print(f"Calculating conciseness and consistency violations")
    names = [get_soft_words(name) for name in set(names)]
    consistency_violations, conciseness_violations = get_conciseness_and_consistency(
        names
    )
    metrics["num_consistency_violations"] = consistency_violations
    metrics["num_conciseness_violations"] = conciseness_violations

    console.print(f"Calculating levenshtein distance: #{len(names)}")
    pairs = list(combinations(names, 2))
    if len(pairs) > 0:
        metrics["median_id_lv_dist"] = get_median_levenshtein_distance(pairs)
    else:
        metrics["median_id_lv_dist"] = None

    return metrics
