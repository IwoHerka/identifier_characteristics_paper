import itertools
import csv
import os
import wordninja
from multiprocessing import Pool
import sys
from itertools import combinations
import syllapy
import casestyle
from nltk.tokenize import RegexpTokenizer
from os import path
from statistics import median
from Levenshtein import distance as levenshtein_distance
from rich.console import Console
from db.utils import get_functions_for_repo, update_function_metrics, commit, get_repos, init_local_session
from db.models import Repo, Function
from ..utils import unique_pairs
from .utils import load_abbreviations, split_compound, is_dict_word
from .cc import get_conciseness_and_consistency
from .context_coverage import get_context_coverage
from .external_similarity import get_external_similarity

csv.field_size_limit(sys.maxsize)
console = Console()

POOL_SIZE = 1


def get_median_length(names):
    return median([len(name) for name in names])


def get_syllable_count(identifier):
    softwords = casestyle.casepreprocess(identifier)
    syllables = sum([syllapy.count(word) for word in softwords])
    return syllables


# Function to tokenize based on uppercase letters
def tokenize_identifier(identifier):
    tokenizer = RegexpTokenizer("[A-Z][^A-Z]*")
    tokens = tokenizer.tokenize(identifier)
    return tokens


def get_soft_words(identifier):
    return casestyle.casepreprocess(identifier.strip("_"))


def get_casing_style(identifier):
    camelcase = casestyle.camelcase(identifier)
    pascalcase = casestyle.pascalcase(identifier)
    snakecase = casestyle.snakecase(identifier)
    kebabcase = casestyle.kebabcase(identifier)
    macrocase = casestyle.macrocase(identifier)

    if camelcase == snakecase == kebabcase:
        return "nocase"
    elif camelcase == identifier:
        return "camelcase"
    elif pascalcase == identifier:
        return "pascalcase"
    elif identifier == pascalcase:
        return "pascalcase"
    elif identifier == snakecase:
        return "snakecase"
    elif identifier == kebabcase:
        return "kebabcase"
    elif identifier == macrocase:
        return "macrocase"
    else:
        return "unknown"


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

    for repo in Repo.all(session):
        if repo.ntype is None or repo.ntype == "":
            continue

        if repo.lang in ["javascript", "haskell"]:
            continue

        if repo.ntype not in ['frontend', 'backend', 'infr', 'edu', 'db', 'cli', 'lang', 'ml', 'game', 'test', 'comp',
            'build', 'code', 'log', 'seman', 'struct', 'ui']:
            continue

        console.print(f"Calculating context coverage for {repo.name}", style="red")
        all_names = set()
        all_function_bodies = []
        functions = Function.filter_by(session, repo_id=repo.id)

        functions = [function for function in functions if (function.name and 'test' not in function.name)]

        count = sum(1 for function in functions if function.context_coverage is not None)
        console.print(f"Found {len(functions)} functions and {count} functions with context coverage", style="red")

        if count >= 1000 or count >= len(functions):
            continue

        functions = functions[:1000]

        for function in functions:
            names = function.names.split(" ")
            all_function_bodies.append(names)
            all_names.update(names[:10])

        all_names = list(all_names)

        if len(all_names) == 0 or len(all_function_bodies) == 0:
            continue
        
        values = get_context_coverage(all_function_bodies, all_names)

        for function in functions:
            console.print(f"Calculating context coverage for {function.name}", style="yellow")
            names = function.names.split(" ")[:10]
            scores = []

            for name, value in values.items():
                if name in names:
                    scores.append(value)

            if len(scores) > 0:
                function.context_coverage = float(median(scores))
                session.commit()


def get_duplicate_percentage(names):
    from collections import Counter

    # Count occurrences of each word
    word_counts = Counter(names)

    # Count how many words have more than one occurrence
    duplicate_count = sum(1 for count in word_counts.values() if count > 1)

    # Calculate the percentage of duplicate words
    total_words = len(word_counts.keys())
    if total_words == 0:
        return 0.0

    return duplicate_count / total_words


def calculate_common_grammar(langs):
    lang_to_grammars = {}
    
    for lang in langs:
        session = init_local_session()

        grammars = Function.get_grammars_for_lang(lang, session, limit=25000)
        from collections import Counter

        # Flatten the list of grammars and count occurrences
        grammar_list = [grammar for sublist in grammars for grammar in sublist]
        grammar_counts = Counter(grammar_list)

        # Get the 10 most common grammars
        most_common_grammars = grammar_counts.most_common(10)

        console.print(f"Most common grammars for {lang}:", style="yellow")

        for grammar, count in most_common_grammars:
            console.print(f"{grammar}: {count}", style="yellow")

        lang_to_grammars[lang] = most_common_grammars

    return lang_to_grammars


def calculate_basic_metrics_for_repo(repo_id):
    session = init_local_session()
    abbreviations = load_abbreviations("build/abbreviations.csv")
    count = 0

    for function in Function.filter_by(session, repo_id=repo_id):
        # try:
        # TODO: Refactor
        if function.median_id_length is not None:
            continue

        try:
            console.print(f"({count}) {function.name}", style="yellow")
        except:
            pass

        names = function.names.split(" ")
        metrics = get_basic_metrics(names, abbreviations)
        count += 1

        for key, value in metrics.items():
            setattr(function, key, value)

        session.commit()
        # except Exception as e:
        #     console.print(f"Error: {e}")
        # finally:
        #     session.close()


def calculate_basic_metrics():
    session = init_local_session()
    repo_ids = [repo.id for repo in Repo.all(session, lang='javascript')]

    for repo_id in repo_ids:
        calculate_basic_metrics_for_repo(repo_id)

    # with Pool(POOL_SIZE) as p:
    #     # Use the pool to map the function to the repo_ids with a specified chunk size
    #     p.map(calculate_basic_metrics_for_repo, repo_ids, chunksize=10)


def get_basic_metrics(names, abbreviations):
    metrics = {}

    # 1. Median identifier length (multigram, non-unique)
    metrics["median_id_length"] = get_median_length(names)

    # 2. Median syllable count (multigram, non-unique)
    syllable_counts = [get_syllable_count(name) for name in names]
    metrics["median_id_syllable_count"] = median(syllable_counts)

    # 3. Median soft word count (soft-words, non-unique)
    soft_word_counts = [len(get_soft_words(name)) for name in names]
    metrics["median_id_soft_word_count"] = median(soft_word_counts)

    # 4. Ratio of unique to duplicate identifiers (multigram, non-unique)
    metrics["id_duplicate_percentage"] = get_duplicate_percentage(names)

    # 5. Number of single letter identifiers (multigram, non-unique)
    single_letter_names = [name for name in names if len(name) == 1]
    metrics["num_single_letter_ids"] = len(single_letter_names)

    # 6. Most common casing style (multigram, non-unique)
    casing_styles = [get_casing_style(name) for name in names]
    metrics["id_most_common_casing_style"] = max(set(casing_styles), key=casing_styles.count)

    # 7. Percent of abbreviations (soft-words, non-unique)
    console.print(f"Calculating abbreviations")
    soft_words = [word for name in names for word in get_soft_words(name)]
    if len(soft_words) > 0:
        metrics["id_percent_abbreviations"] = get_num_abbreviations(abbreviations, soft_words) / len(soft_words)

    # 8. Percent of dictionary words (soft-words, non-unique)
    console.print(f"Calculating dictionary words")
    if len(soft_words) > 0:
        metrics["id_percent_dictionary_words"] = get_num_dictionary_words(soft_words) / len(soft_words)
    else:
        metrics["id_percent_dictionary_words"] = 0

    # 9. Levenshtein distance (multigram, non-unique)
    console.print(f"Calculating levenshtein distance")
    pairs = list(combinations(names, 2))
    if len(pairs) > 0:
        metrics["median_id_lv_dist"] = get_median_levenshtein_distance(pairs)
    else:
        metrics["median_id_lv_dist"] = None

    # 10. Conciseness & consistency violations (soft-words, unique)
    console.print(f"Calculating conciseness and consistency violations")
    names = [get_soft_words(name) for name in set(names)]
    consistency_violations, conciseness_violations = get_conciseness_and_consistency(names)
    metrics["num_consistency_violations"] = consistency_violations
    metrics["num_conciseness_violations"] = conciseness_violations

    return metrics