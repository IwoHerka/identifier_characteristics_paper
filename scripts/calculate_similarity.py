import argparse
import fasttext
import itertools
import csv
import sys
import pandas as pd
import scipy.stats as stats
import numpy as np
import matplotlib.pyplot as plt
import random
from matplotlib.ticker import ScalarFormatter

from itertools import combinations
from scipy.spatial.distance import cosine

from collections import deque

csv.field_size_limit(sys.maxsize)


def overall_average(iterable):
    total_sum = 0
    count = 0
    i = 0
    for value in iterable:
        i += 1
        total_sum += value
        count += 1
        if i > 100000:
            break
    return total_sum / count if count else None


def overall_median(iterable):
    values = sorted(iterable)  # This requires storing the data temporarily
    n = len(values)
    i = 0
    if n == 0:
        return None
    if n % 2 == 1:
        return values[n//2]
    else:
        return (values[n//2 - 1] + values[n//2]) / 2.0


def unique_pairs(strings):
    return list(combinations(set(strings), 2))


def get_median_dist(file_path, model):
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        i = 0

        for row in reader:
            i += 1
            if i % 10 != 0:
                continue
            column1, column2 = row
            fname = column1.split('#')[0]
            names = column2.split(' ')
            names = unique_pairs(names)
            cosines = []

            for (name1, name2) in names:
                # if len(name1) > 2 and len(name2) > 2:
                cos = cosine(model.get_word_vector(name1), model.get_word_vector(name2))
                if cos != None:
                    cosines.append(cos)
                    # yield cos

            median = overall_median(cosines)
            if median != None:
                yield median


def plot_values(values, save_path, use_scatter=False, y_lim=None):
    plt.figure(figsize=(10, 6))
    x_values = range(1, len(values) + 1)  # Generating x-values starting from 1
    
    if use_scatter:
        plt.scatter(x_values, values)
    else:
        plt.plot(x_values, values, marker='o', linestyle='-')
    
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
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
# C is too similar? Count only words longer than ...
# Train model using equal words/LOC 
# Remove duplicates from words, special symbols (eg _)
# Check dist per project

CALC_PVALUE = False
MODEL = 'build/models/all.bin'
# MODEL = 'build/models/cc.en.300.bin'

if __name__ == '__main__':
    model = fasttext.load_model(MODEL)
    pvalues = []

    # for i in range(10, 30):
    all_distances = []

    for lang in ['clojure', 'elixir', 'erlang', 'java', 'javascript', 'ocaml', 'python']:
    # for lang in ['c', 'haskell']:
        file = f'build/sampled/{lang}.csv'

        series = get_median_dist(file, model)
        # distances = list(itertools.islice(series, 250000))
        distances = list(series)
        # distances = [random.random() / 100 for _ in range(j)]

        all_distances.append(distances)
        # median = overall_median(distances)
        median = overall_median(distances)
        print(f'Median for {lang}: {median}')

        if CALC_PVALUE:
            # Histogram
            plt.hist(distances, bins='auto')
            plt.title('Histogram of Cosine Distances')
            plt.savefig(f'build/stats/histogram_{lang}.png')
            plt.close()

            # Q-Q Plot
            stats.probplot(distances, dist="norm", plot=plt)
            plt.title('Q-Q Plot of Cosine Distances')
            plt.savefig(f'build/stats/q_plot_{lang}.png')
            plt.close()

            # Shapiro-Wilk Test
            stat, p = stats.shapiro(distances)
            print('Shapiro-Wilk Test: Stat=%.3f, p=%.3f' % (stat, p))

            alpha = 0.05
            if p > alpha:
                print('Sample looks Gaussian (fail to reject H0)')
            else:
                print('Sample does not look Gaussian (reject H0)')

    if CALC_PVALUE:
        anova_result = stats.f_oneway(all_distances[0], all_distances[1])
        print(f"ANOVA result: F={anova_result.statistic}, p-value={anova_result.pvalue}")
        pvalues.append(anova_result.pvalue)

        plot_values(
            pvalues, 
            save_path='build/stats/pvalue_plot.png'
        )
                    
