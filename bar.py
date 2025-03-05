import nltk
import statistics
import csv
import string
import casestyle
import random
import tempfile
import fasttext
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.cm import get_cmap

from multiprocessing import Process
from itertools import combinations
from nltk.stem import PorterStemmer, LancasterStemmer, SnowballStemmer
from nltk.corpus import gutenberg
from collections import Counter, defaultdict
from rich.console import Console
from scipy.spatial.distance import cosine
from db.models import Function, Repo, ANOVARun, ARTRun, MannWhitneyu
import casestyle
from db.utils import init_local_session
from itertools import combinations
from scipy.spatial.distance import cosine

NUM_PROCESSES = 4
LANGS = [
    "c",
    "clojure",
    "elixir",
    "erlang",
    # "fortran",
    "haskell",
    "java",
    "javascript",
    "ocaml",
    "python",
]


console = Console()

def all_pairs(strings):
    return list(combinations(strings, 2))


def calculate_number_of_function_domain():
    metric = "context_coverage"
    session = init_local_session()

    lang_to_dict = {}

    domains = [
        "ml",
        "infr",
        "db",
        "struct",
        "edu",
        "lang",
        "frontend",
        "backend",
        "build",
        "code",
        "cli",
        "comp",
        "game",
        "log",
        "test",
        "seman",
        "ui",
    ]

    for lang in LANGS:
        functions_by_domain = defaultdict(lambda: 0)

        for repo in Repo.all(session, lang=lang, selected=True):
            functions = Function.filter_by(session, repo_id=repo.id)

            for function in functions:
                print(function.name)
                if getattr(function, metric, None) is not None:
                    functions_by_domain[function.domain] += 1

        lang_to_dict[lang] = functions_by_domain

    min_value = 1000000
    for domain in domains:
        values = []
        for lang in LANGS:
            value = lang_to_dict[lang][domain]
            min_value = min(min_value, value)

            if value > 3000:
                values.append(str(value))
            else:
                values.append(f"\\underline{{{value}}}")

        console.print(f"{domain} & " + ' & '.join(values) + " \\\\")


def plot_dot_diagram(df):
    # Define the colors and labels for each effect size
    effect_sizes = {
        'language_effect_size': ('red', 'language'),
        'domain_effect_size': ('blue', 'domain'),
        'interact_effect_size': ('green', 'interaction')
    }

    # Create a scatter plot for each effect size
    plt.figure(figsize=(6, 4))  # Adjusted to provide more space for the legend
    for effect_size, (color, label) in effect_sizes.items():
        # Add a small random jitter to the x-values
        jitter = np.random.uniform(-100, 100, size=len(df['max_sample']))
        x_values = df['max_sample'] + jitter
        plt.scatter(x_values, df[effect_size], label=label, color=color, s=7)  # Set smaller dot size

    # Set the labels and title
    plt.xlabel('max sample size')
    plt.ylabel('effect sizes')

    # Set x-ticks to the specific possible values
    plt.xticks([6300, 8400, 10600])

    # Add a legend to differentiate the effect sizes, place it outside the plot, and remove the border
    plt.legend(loc='upper left', bbox_to_anchor=(1.05, 1), frameon=False)

    # Show the plot
    plt.savefig('anova_effect_sizes.png', dpi=500, bbox_inches='tight')  # Ensure the legend is not cut off


def validate_anova_runs():
    session = init_local_session()

    METRICS = [
      "median_id_length", 
      "median_id_soft_word_count",
      "id_duplicate_percentage",
      "num_single_letter_ids",
      "id_percent_abbreviations",
      "id_percent_dictionary_words",
      "num_conciseness_violations",
      "num_consistency_violations",
      "term_entropy",
      "median_id_lv_dist",
      "median_id_semantic_similarity",
      "median_word_concreteness",
      "context_coverage",
      "grammar_hash"
    ]

    console.print("metric, median_lang_es, mean_lang_es, std_lang_es, median_domain_es, mean_domain_es, std_domain_es, median_interact_es, mean_interact_es, std_interact_es")

    for metric in METRICS:
        lang_es = []
        domain_es = []
        interact_es = []
        max_samples = []
        metrics = []

        for per_lang_limit in reversed([6300, 8400, 10600]):
            for run in ANOVARun.all(session, max_samples=per_lang_limit, metric=metric, typ=4, domains="ml infr db struct edu lang frontend backend build code cli comp game"):
                lang_es.append(run.lang_es)
                domain_es.append(run.domain_es)
                interact_es.append(run.interact_es)
                max_samples.append(run.max_samples)
                metrics.append(metric)

        median_lang_es = statistics.median(lang_es)
        median_domain_es = statistics.median(domain_es)
        median_interact_es = statistics.median(interact_es)
        mean_lang_es = statistics.mean(lang_es)
        mean_domain_es = statistics.mean(domain_es)
        mean_interact_es = statistics.mean(interact_es)
        std_lang_es = statistics.stdev(lang_es)
        std_domain_es = statistics.stdev(domain_es)
        std_interact_es = statistics.stdev(interact_es)

        # if (abs(median_lang_es - median_interact_es) <= 0.005 and median_lang_es > median_interact_es) or (abs(mean_lang_es - mean_interact_es) <= 0.005 and mean_lang_es > mean_interact_es):
        #     console.print(f"X")

        # if median_interact_es > median_lang_es or mean_interact_es > mean_lang_es:
        #     console.print(f"O")

        # console.print(f"{metric.replace('_', ' ')} & {median_lang_es:.4f}, {mean_lang_es:.4f}, {std_lang_es:.4f} & {median_domain_es:.4f}, {mean_domain_es:.4f}, {std_domain_es:.4f} & {median_interact_es:.4f}, {mean_interact_es:.4f}, {std_interact_es:.4f} \\\\")
        console.print(f"{metric.replace('_', ' ')}, {median_lang_es:.4f}, {mean_lang_es:.4f}, {std_lang_es:.4f}, {median_domain_es:.4f}, {mean_domain_es:.4f}, {std_domain_es:.4f}, {median_interact_es:.4f}, {mean_interact_es:.4f}, {std_interact_es:.4f}")

    return

    df = pd.DataFrame({
        'language_effect_size': lang_es,
        'domain_effect_size': domain_es,
        'interact_effect_size': interact_es,
        'metric': metrics,
        'max_sample': max_samples
    })

    plot_dot_diagram(df)
    return

    for metric in METRICS:
        metric_to_order = defaultdict(lambda: 0)
        metric_to_ratio = {}

        for per_lang_limit in reversed([6300, 8400, 10600]):
            for run in ANOVARun.all(session, max_samples=per_lang_limit, metric=metric):
                if run.lang_es > run.domain_es > run.interact_es:
                    metric_to_order['lang-domain-interact'] += 1
                elif run.lang_es > run.interact_es > run.domain_es:
                    metric_to_order['lang-interact-domain'] += 1

        keys = ['lang-interact-domain', 'lang-domain-interact']
        metric = metric.replace("_", " ")

        if len(metric_to_order) == 2:
            ratio = metric_to_order[keys[0]] / metric_to_order[keys[1]]
            console.print(f"{metric} & {metric_to_order['lang-domain-interact']} & {metric_to_order['lang-interact-domain']} & {ratio:.2f} \\\\")
        elif len(metric_to_order) == 1:
            console.print(f"{metric} & {metric_to_order['lang-domain-interact']} & {metric_to_order['lang-interact-domain']} & 0 \\\\")
        else:
            raise Exception(f"Unexpected number of keys: {len(metric_to_order)}")

def validate_art_runs():
    session = init_local_session()

    METRICS = [
      "median_id_length", 
      "median_id_soft_word_count",
      "id_duplicate_percentage",
      "num_single_letter_ids",
      "id_percent_abbreviations",
      "id_percent_dictionary_words",
      "num_conciseness_violations",
      "num_consistency_violations",
      "term_entropy",
      "median_id_lv_dist",
      "median_id_semantic_similarity",
      "median_word_concreteness",
      "context_coverage",
      "grammar_hash"
    ]
    for metric in METRICS:
        lang_p = []
        domain_p = []
        interact_p = []
        max_samples = []

        for run in ARTRun.all(session, metric=metric):
            lang_p.append(run.lang_p)
            domain_p.append(run.domain_p)
            interact_p.append(run.interact_p)
            max_samples.append(run.max_samples)

        median_lang_p = statistics.median(lang_p)
        median_domain_p = statistics.median(domain_p)
        median_interact_p = statistics.median(interact_p)
        mean_lang_p = statistics.mean(lang_p)
        mean_domain_p = statistics.mean(domain_p)
        mean_interact_p = statistics.mean(interact_p)
        std_lang_p = statistics.stdev(lang_p)
        std_domain_p = statistics.stdev(domain_p)
        std_interact_p = statistics.stdev(interact_p)

        def fn_print(v):
            if f"{v:.4f}" == "0.0000":
                return "0"
            elif v >= 0.05:
                return f"\\underline{{{v:.4f}}}"
            else:
                return f"{v:.4f}"

        console.print(f"{metric.replace('_', ' ')} & {fn_print(median_lang_p)}, {fn_print(mean_lang_p)}, {fn_print(std_lang_p)} & {fn_print(median_domain_p)}, {fn_print(mean_domain_p)}, {fn_print(std_domain_p)} & {fn_print(median_interact_p)}, {fn_print(mean_interact_p)}, {fn_print(std_interact_p)} \\\\")


def validate_interaction_deviations():
    METRICS = [
      "median_id_length", 
      "median_id_soft_word_count",
      "id_duplicate_percentage",
      "num_single_letter_ids",
      "id_percent_abbreviations",
      "id_percent_dictionary_words",
      "num_conciseness_violations",
      "num_consistency_violations",
      "term_entropy",
      "median_id_lv_dist",
      "median_id_semantic_similarity",
      "median_word_concreteness",
      "context_coverage",
      "grammar_hash"
    ]

    session = init_local_session()
    metric_to_values = defaultdict(lambda: [])

    for metric in METRICS:
        for run in MannWhitneyu.all(session, metric=metric):
            if run.adj_p_value < 0.05:
                metric_to_values[metric].append((run.language, run.cliffs_delta))

    x = defaultdict(lambda: [])

    for metric, values in metric_to_values.items():
        lang_to_cliffs_delta = defaultdict(list)
        for lang, cliffs_delta in values:
            lang_to_cliffs_delta[lang].append(cliffs_delta)

        lang_to_mean_cliffs_delta = {lang: statistics.mean(cliffs_deltas) for lang, cliffs_deltas in lang_to_cliffs_delta.items()}
        # sorted_langs = sorted(lang_to_mean_cliffs_delta.items(), key=lambda x: x[1], reverse=True)

        for lang, mean in lang_to_mean_cliffs_delta.items():
            x[metric].append((lang, mean))

    plot_cliffs_spread(x)


def plot_cliffs_spread(metric_to_values):
    """
    Plots the spread of Cliff's Delta for each language for each metric.

    Parameters:
    -----------
    metric_to_values : dict
        Dictionary where keys are metric names, and values are lists of tuples:
          [ (language, cliffs_delta), (language, cliffs_delta), ... ]

    Example:
    --------
    METRICS = [
        "median_id_length",
        "median_id_soft_word_count",
        "context_coverage"
    ]
    metric_to_values = {
        "median_id_length": [
            ("python", 0.2), ("java", -0.1), ("c++", 0.05)
        ],
        "median_id_soft_word_count": [
            ("python", 0.3), ("c++", -0.2)
        ],
        "context_coverage": [
            ("java", 0.15), ("c++", 0.25)
        ]
    }
    plot_cliffs_spread(metric_to_values)
    """

    # Collect all languages for color assignment
    languages = set()
    for metric, values in metric_to_values.items():
        print(f"----------------- {metric} -----------------")
        for lang, cliffs_delta in values:
            print(f"{lang}: {cliffs_delta}")
            languages.add(lang)
    languages = sorted(languages)

    # Assign a distinct color for each language using a colormap
    colormap = get_cmap('tab10')  # You can choose a different colormap if you prefer
    language_to_color = {}
    for i, lang in enumerate(languages):
        color = colormap(i % 10)  # cycle through up to 10 distinct colors in tab10
        language_to_color[lang] = color

    plt.figure(figsize=(10, 6))

    # Sort or simply list the metrics to have a consistent order on the y-axis
    metrics_list = sorted(metric_to_values.keys())
    
    # Plot each metric, enumerated starting from 1 (y=1, y=2, etc.)
    for i, metric in enumerate(metrics_list, start=1):
        # Retrieve the list of (language, delta) for this metric
        lang_delta_pairs = metric_to_values[metric]
        # For each pair, plot a dot at (delta, i)
        for (lang, cliffs_delta) in lang_delta_pairs:
            color = language_to_color[lang]
            plt.scatter(cliffs_delta, i, color=color, s=60)

    # Add vertical bars at specified x values
    for x_val in [0.14, 0.33, 0.47, -0.14, -0.33, -0.47]:
        plt.axvline(x=x_val, color='gray', linestyle='--', linewidth=1)

    # Create a legend by plotting an "invisible" point for each language
    for lang in languages:
        plt.scatter([], [], color=language_to_color[lang], s=60, label=lang)
    plt.legend(title="Language", bbox_to_anchor=(1.05, 1.0), loc='upper left')

    # Configure the y-axis ticks (one tick per metric)
    plt.yticks(range(1, len(metrics_list) + 1), metrics_list)

    # Set x-axis limits from -1 to 1 and custom x-ticks
    plt.xlim(-1, 1)
    plt.xticks([-1, -0.75, -0.47, -0.33, -0.14, 0, 0.14, 0.33, 0.47, 0.75, 1])

    # Labeling and title
    plt.xlabel("Cliff's Delta")
    plt.ylabel("Metrics")
    plt.title("Spread of Cliff's Delta by Language and Metric")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # calculate_number_of_function_domain()
    # validate_anova_runs()
    # validate_art_runs()
    validate_interaction_deviations()

    # session = init_local_session()
    # # model = fasttext.load_model("build/models/ft_19M_100x1000_5ws.bin")

    # grammar_to_index = {}
    # current_index = 0

    # for lang in LANGS:
    #     for repo in Repo.all(session, lang=lang, selected=True):
    #         functions = Function.filter_by(session, repo_id=repo.id)

    #         for function in functions:
    #             if function.grammar not in grammar_to_index:
    #                 grammar_to_index[function.grammar] = current_index
    #                 current_index += 1
    #             function.grammar_hash = grammar_to_index[function.grammar]
    #             session.add(function)
    
    #         session.commit()


    # for lang in LANGS:
    #     for repo in Repo.all(session, lang=lang, selected=True):
    #         functions = Function.filter_by(session, repo_id=repo.id)

    #         for function in functions:
    #             with tempfile.NamedTemporaryFile(delete=True) as f:
    #                 for function in functions:
    #                     f.write(f"{function.names}\n".encode('utf-8'))

    #                 model = fasttext.train_unsupervised(f.name, "cbow", minCount=3, lr=0.1, ws=5, epoch=5, dim=100, thread=24)

    #                 for function in functions:
    #                     all_similarities = []

    #                     for name in function.names.split():
    #                         similar_words = model.get_nearest_neighbors(name, k=1)
    #                         median_external_similarity = similar_words[0][0]
    #                         all_similarities.append(median_external_similarity)

    #                     function.median_external_similarity = statistics.median(all_similarities)
    #                     console.print(function.median_external_similarity)
    #                     session.add(function)

    #                 session.commit()
        #         if function.median_id_semantic_similarity is not None:
        #             continue

        #         names = function.names.split(" ")

        #         if len(names) < 2:
        #             continue

        #         all_names = all_pairs(random.sample(names, min(50, len(names))))
        #         prev_cosines = {}
        #         cosines = []

        #         for name1, name2 in all_names:
        #             if (name1, name2) in prev_cosines:
        #                 cosines.append(prev_cosines[(name1, name2)])
        #                 continue

        #             name_a = casestyle.camelcase(name1).lower()
        #             name_b = casestyle.camelcase(name2).lower()
        #             cos = cosine(model.get_word_vector(name_a), model.get_word_vector(name_b))

        #             if cos != None:
        #                 prev_cosines[(name1, name2)] = cos
        #                 cosines.append(cos)
        #             else:
        #                 console.print(f"Cosine is None for {name1} and {name2}")

        #         median = statistics.median(cosines)

        #         if median != None:
        #             function.median_id_semantic_similarity = median
        #             session.add(function)
        #             try:
        #                 console.print(f"{function.name} = {median}")
        #             except:
        #                 pass

        #     session.commit()

        

