from statistics import median
from collections import deque
import random
from itertools import combinations
import json
import casestyle
import fasttext
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats as stats

from scipy.stats import gaussian_kde
from matplotlib.ticker import ScalarFormatter
from scipy.spatial.distance import cosine
from db.utils import get_repos_by_lang, init_local_session, get_by_metric, get_repos_by_type
from scripts.utils import overall_mean, overall_median
from scripts.lang import LANGS
from rich.console import Console


console = Console()

VERBOSE = False


def plot_values(values, save_path, use_scatter=False, y_lim=None):
    plt.figure(figsize=(10, 6))
    x_values = range(1, len(values) + 1)  # Generating x-values starting from 1

    if use_scatter:
        plt.scatter(x_values, values)
    else:
        plt.plot(x_values, values, marker="o", linestyle="-")

    plt.ticklabel_format(style="sci", axis="y", scilimits=(0, 0))
    plt.gca().yaxis.set_major_formatter(ScalarFormatter(useMathText=True))

    # Set the y-axis limit to a maximum of 1000
    plt.ylim(0, 1000)

    # Check if a save path is provided
    if save_path:
        plt.savefig(save_path)
        plt.close()  # Close the plot to free up memory
        print(f"Plot saved to {save_path}")
    else:
        plt.show()


class BasicMetrics:
    @staticmethod
    def __plot(get_repos_fn, get_fn, scale_fn, name, ylim, xlim, num_bins, bw_method, verbose: bool = False):
        global VERBOSE
        VERBOSE = verbose

        session = init_local_session()
        all_series = []
        all_xs = []
        all_densities = []
        all_labels = []

        for i, lang in enumerate(LANGS):
            console.print(f"Plotting {get_fn.__name__} for {lang}", style="yellow")
            repos = get_repos_fn(lang)
            console.print(f"Repos: {len(repos)}, lang: {lang}", style="yellow")
            series = []

            for repo in repos:
                for metric in get_fn(repo.id, session):
                    if VERBOSE:
                        console.print(f"{metric}", style="yellow")
                    series.append(scale_fn(metric[0]))

            if len(series) > 2000:
                random.shuffle(series)
                series = series[:2000]

            console.print(f"Series: {len(series)}", style="yellow")
            series.extend(range(0, num_bins))
            all_series.append(series)

        for i, lang in enumerate(LANGS):
            # Histogram
            series = all_series[i]
            # ylim = max([max(s) for s in all_series])
            bins = np.arange(0, num_bins + 1, 1)
            count, bins, ignored = plt.hist(series, bins=bins, alpha=0.7)

            density = gaussian_kde(series, bw_method=bw_method)
            xs = np.linspace(min(series), max(series), 200)
            plt.plot(xs, density(xs) * len(series) * (bins[1] - bins[0]), color='red')

            all_xs.append(xs)
            all_densities.append(density(xs) * len(series) * (bins[1] - bins[0]))
            all_labels.append(lang.capitalize())

            # plt.xticks(np.arange(min(series), max(series)+1, 5))
            # plt.ylim(0, ylim)
            # plt.xlim(0, num_bins)

            # plt.legend()
            # console.print(f"Saving plot to {f'build/stats/{name}_{lang}.png'}", style="yellow")
            # plt.savefig(f"build/stats/{name}_{lang}.png", dpi=300)
            # plt.close()

        plt.figure(figsize=(10, 6))
        for xs, density, label in zip(all_xs, all_densities, all_labels):
            plt.plot(xs, density, label=label)

        plt.ylim(0, ylim)
        plt.xlim(0, num_bins + 5)
        plt.xticks(np.arange(0, num_bins + 6, 1))
        plt.legend()
        plt.savefig(f"build/stats/{name}_combined.png", dpi=300)
        plt.close()

    @staticmethod
    def __plot_percent_metric(metric, domain, verbose: bool = False):
        if domain == "ALL":
            get_repos_fn = lambda lang: get_repos_by_lang(lang)
        else:
            get_repos_fn = lambda lang: get_repos_by_type(lang, domain)
        get_fn = lambda repo_id, session: get_by_metric(repo_id, metric, session)
        BasicMetrics.__plot(get_repos_fn, get_fn, lambda x: x * 100, f"{metric}_{domain}", 100, 100, 100, 0.15, verbose)

    @staticmethod
    def __plot_unbounded_metric(metric, ylim, xlim, domain, verbose: bool = False):
        if domain == "ALL":
            get_repos_fn = lambda lang: get_repos_by_lang(lang)
        else:
            get_repos_fn = lambda lang: get_repos_by_type(lang, domain)
        get_fn = lambda repo_id, session: get_by_metric(repo_id, metric, session)
        BasicMetrics.__plot(get_repos_fn, get_fn, lambda x: x, f"{metric}_{domain}", ylim, xlim, xlim, 0.2, verbose)

    @staticmethod
    def __plot_term_entropy(domain, verbose: bool = False):
        if domain == "ALL":
            get_repos_fn = lambda lang: get_repos_by_lang(lang)
        else:
            get_repos_fn = lambda lang: get_repos_by_type(lang, domain)
        get_fn = lambda repo_id, session: get_by_metric(repo_id, "term_entropy", session)
        max_entropy = 5.2826
        get_val_fn = lambda x: x / max_entropy * 100
        BasicMetrics.__plot(get_repos_fn, get_fn, get_val_fn, f"term_entropy_{domain}", 100, 100, 100, 0.15, verbose)
        

    @staticmethod
    def plot_id_semantic_similarity(domain, verbose: bool = False):
        BasicMetrics.__plot_percent_metric("median_id_semantic_similarity", domain, verbose)

    @staticmethod
    def plot_median_id_length(domain, verbose: bool = False):
        BasicMetrics.__plot_unbounded_metric("median_id_length", 500, 25, domain, verbose)

    @staticmethod
    def plot_median_id_syllable_count(domain, verbose: bool = False):
        BasicMetrics.__plot_unbounded_metric("median_id_syllable_count", 500, 10, domain, verbose)

    @staticmethod
    def plot_median_id_soft_word_count(domain, verbose: bool = False):
        BasicMetrics.__plot_unbounded_metric("median_id_soft_word_count", 500, 10, domain, verbose)

    @staticmethod
    def plot_id_duplicate_percentage(domain, verbose: bool = False):
        BasicMetrics.__plot_percent_metric("id_duplicate_percentage", domain, verbose)

    @staticmethod
    def plot_num_single_letter_ids(domain, verbose: bool = False):
        BasicMetrics.__plot_percent_metric("num_single_letter_ids", domain, verbose)

    @staticmethod
    def plot_id_most_common_casing_style(domain, verbose: bool = False):
        # TODO
        pass

    @staticmethod
    def plot_id_percent_abbreviations(domain, verbose: bool = False):
        BasicMetrics.__plot_percent_metric("id_percent_abbreviations", domain, verbose)

    @staticmethod
    def plot_id_percent_dictionary_words(domain, verbose: bool = False):
        BasicMetrics.__plot_percent_metric("id_percent_dictionary_words", domain, verbose)

    @staticmethod
    def plot_median_id_lv_dist(domain, verbose: bool = False):
        BasicMetrics.__plot_unbounded_metric("median_id_lv_dist", 500, 25, domain, verbose)

    @staticmethod
    def plot_num_consistency_violations(domain, verbose: bool = False):
        BasicMetrics.__plot_unbounded_metric("num_consistency_violations", 1500, 25, domain, verbose)

    @staticmethod
    def plot_num_conciseness_violations(domain, verbose: bool = False):
        BasicMetrics.__plot_unbounded_metric("num_conciseness_violations", 1500, 25, domain, verbose)

    @staticmethod
    def plot_term_entropy(domain, verbose: bool = False):
        # TODO: Must be normalized when plotting
        BasicMetrics.__plot_term_entropy(domain, verbose)

    @staticmethod
    def plot_context_coverage(domain, verbose: bool = False):
        pass

    @staticmethod
    def plot_external_similarity(domain, verbose: bool = False):
        pass

    @staticmethod
    def plot_grammatical_patterns(domain, verbose: bool = False):
        pass

    @staticmethod
    def plot_word_concreteness(domain, verbose: bool = False):
        pass
