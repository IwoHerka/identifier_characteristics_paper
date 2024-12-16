import fasttext
import itertools
import csv
import os
import sys
import syllapy
import casestyle
from nltk.tokenize import RegexpTokenizer
from os import path
from statistics import median
from Levenshtein import distance as levenshtein_distance
from rich.console import Console

from ..utils import unique_pairs
from .utils import load_abbreviations, split_compound, is_dict_word
from .cc import get_conciseness_and_consistency
from .context_coverage import get_context_coverage
from .external_similarity import get_external_similarity
from .term_entropy import get_term_entropy

csv.field_size_limit(sys.maxsize)
console = Console()


def get_median_length(words):
    pass


def get_median_duplicates(words):
    pass


def get_single_letters(words):
    pass


def get_syllable_count(identifier):
    # Replace with casestyle
    softwords = wordninja.split(identifier)
    # TODO Deabbreviate
    syllables = sum([syllapy.count(word) for word in softwords])
    return syllables


# Function to tokenize based on uppercase letters
def tokenize_identifier(identifier):
    tokenizer = RegexpTokenizer("[A-Z][^A-Z]*")
    tokens = tokenizer.tokenize(identifier)
    return tokens


def get_soft_words(identifier):
    # Case style
    return len(casestyle.casepreprocess(identifier))


def get_casing_style(identifier):
    camelcase = casestyle.camelcase(identifier)
    pascalcase = casestyle.pascalcase(identifier)
    snakecase = casestyle.snakecase(identifier)
    kebabcase = casestyle.kebabcase(identifier)
    macrocase = casestyle.macrocase(identifier)

    if identifier == camelcase:
        return "camelcase"
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


def get_abbreviations(abbreviations, multigrams):
    count = 0

    for multigram in multigrams:
        for word in multigram:
            if word in abbreviations:
                count += 1

    return count


def get_dictionary_words(words):
    # Multigram or unigram?
    count = 0

    for word in words:
        if is_dict_word(word):
            count += 1

    return count / len(words)


def get_median_levenshtein_distance(word_pairs):
    distances = []

    for word1, word2 in word_pairs:
        distances.append(levenshtein_distance(word1, word2))

    return median(distances)


def get_basic_info(file, abbreviations, model, project):
    with open(file, newline="") as file:
        reader = csv.reader(file, delimiter=",")
        all_names = set()
        all_multigrams = set()
        all_pairs = set()
        all_func_names = set()

        # Per function
        for row in reader:
            func_name = row[0].split("#")[0]
            names = set(row[1].split(" "))
            pairs = unique_pairs(names)
            multigrams = [split_compound(name) for name in names]

            console.print(row[0])
            # console.print(f"Grammar for {func_name} -> {get_grammar(func_name)}", style="yellow")
            # console.print(f"Casing for {func_name} -> {get_casing_style(func_name)}", style="yellow")
            # console.print(f"Ext. similarity for {func_name} -> {get_external_similarity(names, model)}", style="yellow")
            # console.print(f"Num. of dict. words for {func_name} -> {get_dictionary_words(names)}", style="yellow")
            # console.print(f"Num. of abbreviations for {func_name} -> {get_abbreviations(abbreviations, multigrams)}", style="yellow")
            # conc_violations, cons_violations = get_conciseness_and_consistency(multigrams)
            # console.print(f"C&C for {func_name} -> {len(conc_violations)}, {len(cons_violations)}", style="yellow")
            console.print(f"Entropy for {func_name} -> {get_term_entropy(names)}", style="yellow")

            # TODO: Needs work, cannot be compute for a function in isolation

            # console.print(f"Median Levenshtein distance for {func_name} -> {get_median_levenshtein_distance(pairs)}", style="yellow")

            all_names.update(names)
            #all_multigrams.update(multigram)
            all_pairs.update(pairs)

            # return [
            #     get_median_length(names),
            #     get_median_unique(names),
            #     get_median_duplicates(names),
            #     get_casing_styles(names),
            #     get_abbreviations(multigram),
            #     get_dictionary_words(names), # TODO: Compound or raw?
            #     # get_similarity(names),
            # ]

            # names = unique_pairs(names)


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


def calculate(base_dir, model):
    """
    Given a directory with a list of CSV files with function names for each
    project, calculate basic naming stats.
    """
    results = []

    # Build a list project files (one CSV per project) for specified language
    files = [os.path.join(base_dir, file) for file in list(os.listdir(base_dir))]
    console.print(f"Detected {len(files)} files", style="red")

    abbreviations = load_abbreviations("build/abbreviations.csv")
    console.print(f"Loaded {len(abbreviations)} abbreviations", style="yellow")

    model = fasttext.load_model(model)
    #model = None

    # Check only for grammar
    for file in files:
        if ".grammar.csv" in file:
            continue

        console.print(f"Processing {file}", style="yellow")

        project_name = path.basename(file).replace(".csv", "")
        info = get_basic_info(file, abbreviations, model, project_name)
        #info = calc_context_coverage(file, abbreviations, model, project_name)

    # Write summary to language project report CSV
    # with open(f'build/projects/reports/{lang}.csv', 'w', newline="") as summary_file:
    #     writer = csv.writer(summary_file, delimiter=",")

    #     results = [(file, median) for (file, median) in results if median]
    #     for project, median in sorted(results, key=lambda x: x[1]):
    #         writer.writerow([project, median])
