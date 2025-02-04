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
from matplotlib.ticker import ScalarFormatter
from db.models import Repo
from scipy.spatial.distance import cosine
from db.utils import init_local_session, get_functions_for_repo
from scripts.utils import overall_median
from scripts.lang import LANGS
from rich.console import Console


console = Console()


CALC_PVALUE = False
MODEL_NAME = 'ft_19M_100x1000_5ws'
MODEL = f'build/models/{MODEL_NAME}.bin'
ATTR_KEY = ['median_similarity', MODEL_NAME]
VERBOSE = False


def draw_one_dimensional_scatter(values, lang):
    # Generate a fixed x-coordinate with slight random jitter
    x = np.ones(len(values))

    plt.figure(figsize=(3, 15))
    # Plotting the values
    plt.scatter(x, values)

    # Adding labels and title for clarity
    # plt.title('One-dimensional Scatter Plot')
    plt.yticks(values)  # Optionally, mark the values on the y-axis
    # plt.xlabel('Fixed Position with Slight Jitter')
    # plt.ylabel('Values')
    plt.savefig(f"build/stats/similarity_{lang}_scatter.png")

    # Show the plot
    plt.show()


def unique_pairs(strings):
    return list(combinations(set(strings), 2))


def all_pairs(strings):
    return list(combinations(strings, 2))


def get_median_dist(session, repos, model):
    medians = []

    for repo in repos:
        for function in get_functions_for_repo(repo.id, session):
            print(f"{function.name}")

            # if function.metrics and ATTR_KEY[0] in function.metrics and ATTR_KEY[1] in function.metrics[ATTR_KEY[0]]:
            #     continue
            if function.median_id_semantic_similarity is not None:
                medians.append(function.median_id_semantic_similarity)
                continue

            names = function.names.split(" ")

            if len(names) < 2:
                continue

            all_names = all_pairs(random.sample(names, min(50, len(names))))
            prev_cosines = {}
            cosines = []

            for name1, name2 in all_names:
                if (name1, name2) in prev_cosines:
                    cosines.append(prev_cosines[(name1, name2)])
                    continue

                if VERBOSE:
                    console.print(f"Calculating similarity for {name1} and {name2}")

                name_a = casestyle.camelcase(name1).lower()
                name_b = casestyle.camelcase(name2).lower()
                cos = cosine(model.get_word_vector(name_a), model.get_word_vector(name_b))

                if cos != None:
                    prev_cosines[(name1, name2)] = cos
                    cosines.append(cos)
                else:
                    console.print(f"Cosine is None for {name1} and {name2}")

            median = overall_median(cosines)
            if median != None:
                function.median_id_semantic_similarity = median
                session.commit()
                console.print(f"{function.name} = {median}")
                medians.append(median)
            else:
                console.print(f"Median is None for {function.name}, num names: {len(names)}")
    
    return medians


def plot_values(values, save_path, use_scatter=False, y_lim=None):
    plt.figure(figsize=(10, 6))
    x_values = range(1, len(values) + 1)  # Generating x-values starting from 1

    if use_scatter:
        plt.scatter(x_values, values)
    else:
        plt.plot(x_values, values, marker="o", linestyle="-")

    plt.ticklabel_format(style="sci", axis="y", scilimits=(0, 0))
    plt.gca().yaxis.set_major_formatter(ScalarFormatter(useMathText=True))

    if y_lim is not None:
        plt.ylim(y_lim)
    # Check if a save path is provided
    if save_path:
        plt.savefig(save_path)
        plt.close()  # Close the plot to free up memory
        print(f"Plot saved to {save_path}")
    else:
        plt.show()


# TODO:
# [ ] C is too similar? Count only words longer than ...
# [ ] Train model using equal words/LOC
# [ ] Remove duplicates from words, special symbols (eg _)
# [v] Check dist per project
# [ ] Languages like java have a lot of repetition? setters, getters, boilerplate = verbose langs
#     Calculate repetitions and similar strings
# [ ] Calculate how many words per function/file/project/language have high similairty/low (calculate extreme sets)


def plot_similarity(verbose: bool = False):
    global VERBOSE
    VERBOSE = verbose

    session = init_local_session()
    model = fasttext.load_model(MODEL)
    pvalues = []

    # for i in range(10, 30):
    all_distances = []

    # for lang in [
    #     "clojure",
    #     "elixir",
    #     "erlang",
    #     "java",
    #     "javascript",
    #     "ocaml",
    #     "python",
    # ]:
    for lang in LANGS:
        repos = Repo.all(session, lang=lang)
        print(f"Number of repos: {len(repos)}")

        series = get_median_dist(session, repos, model)
        # distances = list(itertools.islice(series, 250000))
        distances = list(series)
        console.print(f"Series length: {len(distances)}")
        # distances = [random.random() / 100 for _ in range(j)]

        all_distances.append(distances)
        # median = overall_median(distances)
        median = overall_median(distances)
        print(f"Median for {lang}: {median}")

        # draw_one_dimensional_scatter(distances, lang)
        # plot_values(distances, save_path=f"build/stats/similarity_{lang}.png")

        # Histogram
        plt.hist(distances, bins="auto")
        plt.title("Histogram of Cosine Distances")
        plt.savefig(f"build/stats/histogram_{lang}.png")
        plt.close()

        # Q-Q Plot
        stats.probplot(distances, dist="norm", plot=plt)
        plt.title("Q-Q Plot of Cosine Distances")
        plt.savefig(f"build/stats/q_plot_{lang}.png")
        plt.close()

        if CALC_PVALUE:

            # Shapiro-Wilk Test
            stat, p = stats.shapiro(distances)
            print("Shapiro-Wilk Test: Stat=%.3f, p=%.3f" % (stat, p))

            alpha = 0.05
            if p > alpha:
                print("Sample looks Gaussian (fail to reject H0)")
            else:
                print("Sample does not look Gaussian (reject H0)")

    if CALC_PVALUE:
        # Must pick at most 5000 samples
        anova_result = stats.f_oneway(all_distances[0], all_distances[1])
        print(
            f"ANOVA result: F={anova_result.statistic}, p-value={anova_result.pvalue}"
        )
        pvalues.append(anova_result.pvalue)

        plot_values(pvalues, save_path="build/stats/pvalue_plot.png")
