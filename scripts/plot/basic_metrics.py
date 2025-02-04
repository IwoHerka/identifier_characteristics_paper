from statistics import median
from collections import deque
import random
from itertools import combinations
from scipy.interpolate import interp1d
from scipy.stats import mannwhitneyu, ks_2samp, kruskal

import json
import casestyle
import fasttext
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import scipy.stats as stats
from sqlalchemy import func
import statsmodels.api as sm
from statsmodels.formula.api import ols
from collections import Counter

from scipy.stats import gaussian_kde
from matplotlib.ticker import ScalarFormatter
from scipy.spatial.distance import cosine
from db.models import Repo, Function
from db.utils import get_repos_by_lang, init_local_session, get_by_metric, get_repos_by_type, init_session
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
        LANGS.remove('fortran')

        for i, lang in enumerate(LANGS):
            console.print(f"Plotting {get_fn.__name__} for {lang}", style="yellow")
            repos = get_repos_fn(lang)
            repo_ids = [repo.id for repo in repos]
            console.print(f"Repos: {len(repos)}, lang: {lang}", style="yellow")
            series = []

            for metric in get_fn(repo_ids, session):
                if VERBOSE:
                    console.print(f"{metric}", style="yellow")
                series.append(metric[0])

            console.print(f"Series: {len(series)}", style="yellow")
            series.extend(range(0, num_bins))
            all_series.append(series)

        # min_length = min(len(series) for series in all_series)
        # print(f"Min length: {min_length}")
        # all_series = [series[:min_length] for series in all_series]

        # Determine the target size for interpolation
        target_size = 100000

        # Interpolate all series to the target size
        resized_series = []
        for series in all_series:
            if len(series) < target_size:
                x_original = np.linspace(0, 1, len(series))
                f = interp1d(x_original, series, kind='linear')
                x_new = np.linspace(0, 1, target_size)
                resized = f(x_new)
            else:
                x_original = np.linspace(0, 1, len(series))
                f = interp1d(x_original, series, kind='linear')
                x_new = np.linspace(0, 1, target_size)
                resized = f(x_new[:target_size])

            console.print(f"Resized series: {len(resized)}", style="yellow")
            resized_series.append(resized)

        all_series = resized_series

        # print(mannwhitneyu(all_series[0], all_series[1], alternative='two-sided'))
        # print(kruskal(all_series[0], all_series[1], all_series[2], all_series[3], all_series[4], all_series[5], all_series[6], all_series[7]))
        # print(ks_2samp(all_series[0], all_series[1]))
        # return

        for i, lang in enumerate(LANGS):
            series = all_series[i]
            bins = np.linspace(min(series), max(series), num_bins + 1)
            count, bins, ignored = plt.hist(series, bins=bins, alpha=0.7)

            density = gaussian_kde(series, bw_method=bw_method)
            xs = np.linspace(min(series), max(series), 200)
            density_values = density(xs) * len(series) * (bins[1] - bins[0])
            plt.plot(xs, density_values, color='red')

            all_xs.append(xs)
            all_densities.append(density_values)
            all_labels.append(lang.capitalize())

        plt.figure(figsize=(10, 6))
        for xs, density, label in zip(all_xs, all_densities, all_labels):
            plt.plot(xs, density, label=label)

        plt.ylim(1000, 10**5)  # Only display y values 1000 and up
        plt.yscale('symlog', linthresh=10)
        plt.xlim(0, num_bins + 5)
        plt.xticks(np.arange(0, num_bins + 6, 1))
        legend = plt.legend()
        for line in plt.gca().get_lines():
            line.set_linewidth(2.5)  # Set the line width to 2.5
        for line in legend.get_lines():
            line.set_linewidth(2.5)  # Set the legend line width to 2.5
        plt.savefig(f"build/stats/{name}_combined.png", dpi=300)
        plt.close()

    @staticmethod
    def __plot2(get_repos_fn, get_fn, scale_fn, name, ylim, xlim, num_bins, bw_method, verbose: bool = False):
        global VERBOSE
        VERBOSE = verbose

        session = init_local_session()
        all_series = []
        all_xs = []
        all_densities = []
        all_labels = []
        LANGS.remove('fortran')
        LANGS.remove('javascript')

        for i, lang in enumerate(LANGS):
            console.print(f"Plotting {get_fn.__name__} for {lang}", style="yellow")
            repos = get_repos_fn(lang)
            repo_ids = [repo.id for repo in repos]
            console.print(f"Repos: {len(repos)}, lang: {lang}", style="yellow")
            series = []

            for metric in get_fn(repo_ids, session):
                if VERBOSE:
                    console.print(f"{metric}", style="yellow")
                series.append(scale_fn(metric))

            console.print(f"Series: {len(series)}", style="yellow")
            series.extend(range(0, num_bins))
            all_series.append(series)

        # print(mannwhitneyu(all_series[0], all_series[1], alternative='two-sided'))
        # print(kruskal(all_series[0], all_series[1], all_series[2], all_series[3], all_series[4], all_series[5], all_series[6], all_series[7]))
        # print(ks_2samp(all_series[0], all_series[1]))

        # Interpolate all series to the target size
        target_size = 11000
        resized_series = []
        for series in all_series:
            if len(series) < target_size:
                x_original = np.linspace(0, 1, len(series))
                f = interp1d(x_original, series, kind='linear')
                x_new = np.linspace(0, 1, target_size)
                resized = f(x_new)
            else:
                x_original = np.linspace(0, 1, len(series))
                f = interp1d(x_original, series, kind='linear')
                x_new = np.linspace(0, 1, target_size)
                resized = f(x_new[:target_size])

            resized = np.append(resized, [0] * (num_bins - len(resized)))
            console.print(f"Resized series: {len(resized)}", style="yellow")
            resized_series.append(resized)

        all_series = resized_series

        plt.figure(figsize=(10, 6))
        markers = ['o']  # List of markers: circle, square, triangle, diamond, etc.
        line_handles = []  # To store line handles for the legend
        for idx, series in enumerate(all_series):
            counts, bins, patches = plt.hist(series, bins=range(num_bins + 1), histtype='step', fill=False, linewidth=0.0)
            bin_centers = 0.5 * (bins[:-1] + bins[1:])
            for patch in patches:
                color = patch.get_edgecolor()
            marker = markers[idx % len(markers)]  # Cycle through markers
            line_handle, = plt.plot(bin_centers, counts, marker=marker, markersize=2, linestyle='-', color=color)  # Use different markers for each series and set marker size to 4
            line_handles.append(line_handle)  # Store the line handle

        plt.xlabel('Value')
        plt.ylabel('Frequency')
        plt.title(f'Histogram of {name}')
        # plt.yscale('symlog', linthresh=10)  # Conditional
        plt.ylim(0, ylim)
        plt.xlim(0, num_bins)
        # plt.xticks(np.arange(0.5, num_bins + 1.5, 1), labels=np.arange(0, num_bins + 1, 1))  # Shift x ticks by 0.5
        plt.xticks(np.arange(0.5, num_bins + 1.5, 10), labels=np.arange(0, num_bins + 1, 10))  # Shift x ticks by 0.5

        for line in plt.gca().get_lines():
            line.set_linewidth(1.5)  # Set the line width to 2.5
        legend = plt.legend(line_handles, LANGS, loc='center left', bbox_to_anchor=(1, 0.5), frameon=False)  # Move legend outside and hide background/border

        plt.savefig(f"build/stats/{name}_combined.png", dpi=300, bbox_extra_artists=(legend,), bbox_inches='tight')
        plt.close()
        # return
        # from matplotlib.cm import get_cmap

        # plt.figure(figsize=(10, 6))
        # cmap = get_cmap('tab20', len(all_series))  # Use a colormap with a large number of distinct colors
        # for idx, series in enumerate(all_series):
        #     bin_counts, bin_edges = np.histogram(series, bins=range(num_bins + 1))
        #     bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
        #     plt.plot(bin_centers, bin_counts, marker='o', linestyle='-', linewidth=0.5, color=cmap(idx))

        # plt.xlabel('Value')
        # plt.ylabel('Frequency')
        # plt.title(f'Graph of {name}')
        # plt.xlim(0, num_bins)
        # for line in plt.gca().get_lines():
        #     line.set_linewidth(1.5)  # Set the line width to 1.0
        # plt.legend(LANGS, loc='upper right')

        # plt.savefig(f"build/stats/{name}_combined.png", dpi=300)
        # plt.close()

    @staticmethod
    def compare_factors():
        # Step 1: Initialize the session
        init_session()
        session = init_local_session()

        # Step 2: Define language-to-paradigm mapping
        lang_to_paradigm = {
            "c": "imperative",
            "clojure": "functional",
            "elixir": "functional",
            "erlang": "functional",
            "fortran": "imperative",
            "haskell": "functional",
            "java": "imperative",
            "javascript": "imperative",
            "ocaml": "functional",
            "python": "imperative",
        }
        other_domain = "WEB"

        # Step 3: Collect metrics for ALL and WEB categories
        metrics_by_lang = BasicMetrics.collect_metrics(session, other_domain)

        # Step 4: Build the DataFrame
        all_data = []
        for lang in LANGS:
            paradigm = lang_to_paradigm[lang]
            for value in metrics_by_lang["ALL"][lang]:
                all_data.append((value, lang, "ALL", paradigm))
            for value in metrics_by_lang[other_domain][lang]:
                all_data.append((value, lang, other_domain, paradigm))

        data_df = pd.DataFrame(all_data, columns=["value", "language", "type", "paradigm"])

        # Step 5: Perform Scheirer–Ray–Hare test
        BasicMetrics.perform_scheirer_ray_hare(data_df)

        # Step 6: Perform ART ANOVA
        # perform_art_anova(data_df)

    @staticmethod
    def collect_metrics(session, other_domain):
        metrics_by_lang = {"ALL": {}, other_domain: {}}

        for lang in LANGS:
            # ALL repos
            repos_all = get_repos_by_lang(lang)
            repo_ids_all = [repo.id for repo in repos_all]
            metrics_by_lang["ALL"][lang] = get_by_metric(repo_ids_all, "term_entropy", session)

            # WEB repos
            repos_web = get_repos_by_type(lang, "WEB")
            repo_ids_web = [repo.id for repo in repos_web]
            metrics_by_lang[other_domain][lang] = get_by_metric(repo_ids_web, "term_entropy", session)

        return metrics_by_lang

    @staticmethod
    def perform_scheirer_ray_hare(data_df):
        # Add ranked values for nonparametric tests
        data_df["rank"] = data_df["value"].rank()

        # Perform ANOVA on ranked data
        model = ols('rank ~ C(language) + C(type) + C(paradigm) + C(language):C(type)', data=data_df).fit()
        anova_table = sm.stats.anova_lm(model, typ=2)

        # Display results
        console.print("Scheirer–Ray–Hare Test Results:", style="yellow")
        console.print(anova_table, style="yellow")

    @staticmethod
    def __plot_percent_metric(metric, domain, verbose: bool = False):
        if domain == "ALL":
            get_repos_fn = lambda lang: get_repos_by_lang(lang)
        else:
            get_repos_fn = lambda lang: get_repos_by_type(lang, domain)
        get_fn = lambda repo_ids, session: get_by_metric(repo_ids, metric, session)
        BasicMetrics.__plot2(get_repos_fn, get_fn, lambda x: x * 100, f"{metric}_{domain}", 10000, 100, 100, 0.2, verbose)

    @staticmethod
    def __plot_unbounded_metric(metric, ylim, xlim, domain, verbose: bool = False):
        if domain == "ALL":
            get_repos_fn = lambda lang: get_repos_by_lang(lang)
        else:
            get_repos_fn = lambda lang: get_repos_by_type(lang, domain)
        get_fn = lambda repo_ids, session: get_by_metric(repo_ids, metric, session)
        BasicMetrics.__plot2(get_repos_fn, get_fn, lambda x: x, f"{metric}_{domain}", ylim, xlim, xlim, 0.2, verbose)

    @staticmethod
    def __plot_term_entropy(domain, verbose: bool = False):
        if domain == "ALL":
            get_repos_fn = lambda lang: get_repos_by_lang(lang)
        else:
            get_repos_fn = lambda lang: get_repos_by_type(lang, domain)
        get_fn = lambda repo_id, session: get_by_metric(repo_id, "term_entropy", session)
        max_entropy = 8.3387
        get_val_fn = lambda x: x / max_entropy * 100
        BasicMetrics.__plot2(get_repos_fn, get_fn, get_val_fn, f"term_entropy_{domain}", 6000, 100, 100, 0.15, verbose)

    @staticmethod
    def plot_median_id_semantic_similarity(domain, verbose: bool = False):
        BasicMetrics.__plot_percent_metric("median_id_semantic_similarity", domain, verbose)

    @staticmethod
    def plot_median_id_length(domain, verbose: bool = False):
        BasicMetrics.__plot_unbounded_metric("median_id_length", 4000, 25, domain, verbose)

    @staticmethod
    def plot_median_id_syllable_count(domain, verbose: bool = False):
        BasicMetrics.__plot_unbounded_metric("median_id_syllable_count", 80000, 10, domain, verbose)

    @staticmethod
    def plot_median_id_soft_word_count(domain, verbose: bool = False):
        BasicMetrics.__plot_unbounded_metric("median_id_soft_word_count", 60000, 10, domain, verbose)

    @staticmethod
    def plot_id_duplicate_percentage(domain, verbose: bool = False):
        BasicMetrics.__plot_percent_metric("id_duplicate_percentage", domain, verbose)

    @staticmethod
    def plot_num_single_letter_ids(domain, verbose: bool = False):
        BasicMetrics.__plot_unbounded_metric("num_single_letter_ids", 90000, 20, domain, verbose)

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
        BasicMetrics.__plot_unbounded_metric("median_id_lv_dist", 22000, 25, domain, verbose)

    @staticmethod
    def plot_num_consistency_violations(domain, verbose: bool = False):
        BasicMetrics.__plot_unbounded_metric("num_consistency_violations", 90000, 10, domain, verbose)

    @staticmethod
    def plot_num_conciseness_violations(domain, verbose: bool = False):
        BasicMetrics.__plot_unbounded_metric("num_conciseness_violations", 80000, 10, domain, verbose)

    @staticmethod
    def plot_term_entropy(domain, verbose: bool = False):
        # TODO: Must be normalized when plotting
        BasicMetrics.__plot_term_entropy(domain, verbose)

    @staticmethod
    def plot_context_coverage(domain, verbose: bool = False):
        BasicMetrics.__plot_percent_metric("context_coverage", domain, verbose)

    @staticmethod
    def plot_external_similarity(domain, verbose: bool = False):
        pass

    @staticmethod
    def plot_grammatical_patterns(domain, verbose: bool = False):
        pass

    @staticmethod
    def plot_word_concreteness(domain, verbose: bool = False):
        pass

    @staticmethod
    def verify_stat_significance():
        session = init_local_session()

    @staticmethod
    def plot_project_size():
        session = init_local_session()
        lang_project_sizes = {}

        # Perform a single query with a join to count functions per repository
        repo_function_counts = session.query(Repo.lang, Function.repo_id, func.count(Function.id).label('function_count')) \
                                      .join(Function, Repo.id == Function.repo_id) \
                                      .group_by(Repo.lang, Function.repo_id) \
                                      .all()

        for i, (lang, repo_id, num_functions) in enumerate(repo_function_counts):
            console.print(f"Repo #{i}", style="yellow")

            if lang not in lang_project_sizes:
                lang_project_sizes[lang] = []

            rounded_size = round(num_functions / 100) * 100
            lang_project_sizes[lang].append(rounded_size)

        plt.figure(figsize=(12, 8))

        for lang, sizes in lang_project_sizes.items():
            plt.hist(sizes, bins=range(0, max(sizes) + 100, 100), alpha=0.5, label=lang)

        plt.xlabel('Project size (function count)')
        plt.ylabel('Number of projects')
        plt.title('Distribution of function counts per project')
        plt.legend(loc='upper left')

        plt.savefig("build/plots/project_sizes_per_language.png")
        plt.close()
        print("Plot saved to build/plots/project_sizes_per_language.png")

    @staticmethod
    def __plot_stacked_bar(get_repos_fn, get_fn, scale_fn, name, num_bins, verbose: bool = False):
        global VERBOSE
        VERBOSE = verbose

        session = init_local_session()
        all_series = []
        all_labels = []
        # LANGS = ['java', 'python']

        for i, lang in enumerate(LANGS):
            console.print(f"Plotting {get_fn.__name__} for {lang}", style="yellow")
            repos = get_repos_fn(lang)
            console.print(f"Repos: {len(repos)}, lang: {lang}", style="yellow")
            series = []

            for repo in repos:
                for metric in get_fn(repo.id, session):
                    if VERBOSE:
                        console.print(f"{metric}", style="yellow")
                    series.append(int(scale_fn(metric[0])))

            console.print(f"Series: {len(series)}", style="yellow")
            series.extend(range(0, num_bins))
            all_series.append(series)
            all_labels.append(lang.capitalize())

        min_length = min(len(series) for series in all_series)
        print(f"Min length: {min_length}")
        all_series = [series[:min_length] for series in all_series]

        # Count occurrences of values in each list
        counts_per_category = [Counter(series) for series in all_series]
        print(counts_per_category)

        # Collect all unique values across all categories for consistency
        # all_values = sorted({int(value) for counts in counts_per_category for value in counts})
        all_values = range(0, num_bins + 1)

        # Prepare data for stacked bar plot
        heights = []
        for counts in counts_per_category:
            heights.append([counts.get(value, 0) for value in all_values])

        # Transpose to stack vertically
        heights = np.array(heights).T

        # Create a stacked bar graph
        x = range(len(all_series))  # Categories
        fig, ax = plt.subplots(figsize=(10, 6))

        bottom = np.zeros(len(all_series))
        for idx, value in enumerate(all_values):
            ax.bar(x, heights[idx], bottom=bottom, label=f"{value}")
            bottom += heights[idx]

        # Add labels, legend, and title
        ax.set_xlabel("Language")
        ax.set_ylabel("Count")
        ax.set_title("Stacked Bar Graph by Value Counts in Categories")
        ax.set_xticks(x)
        ax.set_yticks([])
        ax.set_xticklabels([f"{LANGS[i].capitalize()}" for i in x])
        handles, labels = ax.get_legend_handles_labels()
        legend = ax.legend(handles[::-1], labels[::-1], title="Syllable count", bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)

        # Make the background and border of the legend invisible
        legend.get_frame().set_facecolor('none')
        legend.get_frame().set_edgecolor('none')

        # Show the plot
        plt.tight_layout()
        plt.savefig(f"build/stats/{name}.png")
        plt.show()
