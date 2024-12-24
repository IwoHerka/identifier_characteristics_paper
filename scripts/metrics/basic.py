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

from ..utils import unique_pairs
from .utils import load_abbreviations, split_compound, is_dict_word
from .cc import get_conciseness_and_consistency
from .context_coverage import get_context_coverage
from .external_similarity import get_external_similarity

csv.field_size_limit(sys.maxsize)
console = Console()

POOL_SIZE = 8


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


def calc_context_coverage(file, abbreviations, model, project):
    all_names = []

    with open(file, newline="") as file:
        reader = csv.reader(file, delimiter=",")
        # func_to_names = dict()
        word_to_contexts = dict()

        for row in reader:
            func_name = row[0].split("#")[0]
            names = set(row[1].split(" "))
            names = [list(split_compound(name)) for name in names]
            names = set(itertools.chain.from_iterable(names))

            all_names.append(names)

            for name in names:
                if name in word_to_contexts:
                    word_to_contexts[name].append(names)
                else:
                    word_to_contexts[name] = [names]

    # print(all_names)
    # for (name, _names) in word_to_contexts.items():
    names = word_to_contexts.keys()
    # print(_names)
    coverage = get_context_coverage(all_names, names)

    for name, c in coverage:
        console.print(f"Context coverage for {name} -> {c}", style="yellow")
        # break


def get_duplicate_percentage(names):
    from collections import Counter

    # Count occurrences of each word
    word_counts = Counter(names)

    # Count how many words have more than one occurrence
    duplicate_count = sum(1 for count in word_counts.values() if count > 1)

    # Calculate the percentage of duplicate words
    total_words = len(names)
    if total_words == 0:
        return 0.0

    return duplicate_count / total_words


def calculate_basic_metrics_for_repo(repo_id):
    session = init_local_session()
    abbreviations = load_abbreviations("build/abbreviations.csv")
    count = 0

    try:
        for function in get_functions_for_repo(repo_id, session):
            if function.median_id_length is not None:
                continue

            console.print(f"({count}) {function.name}", style="yellow")
            names = function.names.split(" ")
            metrics = get_basic_metrics(names, abbreviations)
            count += 1

            for key, value in metrics.items():
                setattr(function, key, value)

            session.commit()
    finally:
        session.close()


def calculate_basic_metrics():
    repo_ids = [repo.id for repo in get_repos().all()]

    with Pool(POOL_SIZE) as p:
        # Use the pool to map the function to the repo_ids with a specified chunk size
        p.map(calculate_basic_metrics_for_repo, repo_ids, chunksize=10)


def get_basic_metrics(names, abbreviations):
    metrics = {}

    # 1. Median identifier length (multigram, non-unique)
    metrics["median_id_length"] = get_median_length(names)

    # 2. Median syllable count (multigram, non-unique)
    syllable_counts = [get_syllable_count(name) for name in names]
    metrics["median_id_syllable_count"] = median(syllable_counts)

    # 3. Median soft word count (soft-words, non-unique)
    soft_word_counts = [len(get_soft_words(name)) for name in names]
    metrics["median_soft_word_count"] = median(soft_word_counts)

    # 4. Ratio of unique to duplicate identifiers (multigram, non-unique)
    metrics["id_duplicate_percentage"] = get_duplicate_percentage(names)

    # 5. Number of single letter identifiers (multigram, non-unique)
    single_letter_names = [name for name in names if len(name) == 1]
    metrics["num_single_letter_ids"] = len(single_letter_names)

    # 6. Most common casing style (multigram, non-unique)
    casing_styles = [get_casing_style(name) for name in names]
    metrics["id_most_common_casing_style"] = max(set(casing_styles), key=casing_styles.count)

    # 7. Percent of abbreviations (soft-words, non-unique)
    soft_words = [word for name in names for word in get_soft_words(name)]
    metrics["id_percent_abbreviations"] = get_num_abbreviations(abbreviations, soft_words) / len(soft_words)

    # 8. Percent of dictionary words (soft-words, non-unique)
    metrics["id_percent_dictionary_words"] = get_num_dictionary_words(soft_words) / len(soft_words)

    # 9. Levenshtein distance (multigram, non-unique)
    pairs = list(combinations(names, 2))
    if len(pairs) > 0:
        metrics["median_id_lv_dist"] = get_median_levenshtein_distance(pairs)
    else:
        metrics["median_id_lv_dist"] = None

    # 10. Conciseness & consistency violations (soft-words, unique)
    names = [get_soft_words(name) for name in set(names)]
    consistency_violations, conciseness_violations = get_conciseness_and_consistency(names)
    metrics["num_consistency_violations"] = consistency_violations
    metrics["num_conciseness_violations"] = conciseness_violations

    return metrics



# def calculate(base_dir, model):
#     """
#     Given a directory with a list of CSV files with function names for each
#     project, calculate basic naming stats.
#     """
#     results = []

#     # Build a list project files (one CSV per project) for specified language
#     files = [os.path.join(base_dir, file) for file in list(os.listdir(base_dir))]
#     console.print(f"Detected {len(files)} files", style="red")

#     abbreviations = load_abbreviations("build/abbreviations.csv")
#     console.print(f"Loaded {len(abbreviations)} abbreviations", style="yellow")

#     model = fasttext.load_model(model)
#     #model = None

#     # Check only for grammar
#     for file in files:
#         if ".grammar.csv" in file:
#             continue

#         console.print(f"Processing {file}", style="yellow")

#         project_name = path.basename(file).replace(".csv", "")
#         info = get_basic_info(file, abbreviations, model, project_name)
#         #info = calc_context_coverage(file, abbreviations, model, project_name)

#     # Write summary to language project report CSV
#     # with open(f'build/projects/reports/{lang}.csv', 'w', newline="") as summary_file:
#     #     writer = csv.writer(summary_file, delimiter=",")

#     #     results = [(file, median) for (file, median) in results if median]
#     #     for project, median in sorted(results, key=lambda x: x[1]):
#     #         writer.writerow([project, median])
