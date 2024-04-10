# Given a directory with a list of CSV files with function names for each project,
# calculate median for each project and write it to project language report CSV.

import argparse
import csv
import itertools
import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from itertools import combinations

import fasttext
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats as stats
from matplotlib.ticker import ScalarFormatter
from scipy.spatial.distance import cosine
from utils import overall_median

csv.field_size_limit(sys.maxsize)


def draw(values, lang):
    color = np.random.rand(3,)
    x = np.ones(len(values)) + np.random.uniform(-0.01, 0.01, len(values))
    plt.figure(figsize=(3, 6))
    plt.scatter(x, values, c=[color], s=5)
    plt.xticks([])
    plt.yticks(np.arange(0, 1.1, 0.1))
    plt.ylim(0.0, 1.0)
    plt.xlim(0.99, 1.01)
    plt.savefig(f"build/plots/{lang}_projects.svg")


def unique_pairs(strings):
    return list(combinations(set(strings), 2))


def get_median_dist(file_path, model):
    with open(file_path, newline="") as csvfile:
        reader = csv.reader(csvfile)
        i = 0

        for row in reader:
            i += 1
            if i % 10 != 0:
                continue
            column1, column2 = row
            fname = column1.split("#")[0]
            names = column2.split(" ")
            names = unique_pairs(names)
            cosines = []

            for name1, name2 in names:
                # if len(name1) > 2 and len(name2) > 2:
                cos = cosine(model.get_word_vector(name1), model.get_word_vector(name2))
                if cos != None:
                    cosines.append(cos)
                    # yield cos

            median = overall_median(cosines)
            if median != None:
                yield median


def worker_wrapper(file, f):
    try:
        return f(file)
    except Exception as e:
        print(e)
        # Handle or log the exception if necessary
        return None


MODEL = "build/models/all.bin"
CACHE = False

# Given a CSV file and a model, go over all function-names pair
# and yield cosine distance for each word pair within a function.

if __name__ == "__main__":
    model = fasttext.load_model(MODEL)
    results = []
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-l", "--lang")
    args = arg_parser.parse_args()

    print("Loaded model...")
    lang = args.lang
    jobs = []

    def f(file):
        print(f"Processing {file}...")
        series = get_median_dist(file, model)
        distances = list(series)
        median = overall_median(distances)
        project = file.split("/")[-1].replace(".csv", "")

        if median != None:
            print(f"{project}: {median}")
            return (project, median)
        else:
            return (project, None)

    base_dir = f"build/projects/{lang}"
    files = [os.path.join(base_dir, file) for file in list(os.listdir(base_dir))]

    with open(f"build/cache/{lang}.txt", "r+") as cache:
        processed = cache.read().splitlines()

        if CACHE:
            files = [
                f
                for f in files
                if not f.split("/")[-1].replace(".csv", "") in processed
            ]
            print(f"PROCESSING: {files}")

        with ProcessPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(f, file) for file in sorted(files)]

            for future in as_completed(futures):
                try:
                    result = future.result(timeout=10)
                    results.append(result)
                    print(f"Process completed successfully with result: {result}")
                    cache.write(result[0] + "\n")
                    cache.flush()
                except TimeoutError:
                    print(f"Process timed out.")
                except Exception as e:
                    print(f"Process raised an exception: {str(e)}")

    draw([median for (file, median) in results if median], lang)

    with open(f"build/projects/reports/{lang}.csv", "w", newline="") as summary_file:
        writer = csv.writer(summary_file, delimiter=",")

        results = [(file, median) for (file, median) in results if median]
        for project, median in sorted(results, key=lambda x: x[1]):
            writer.writerow([project, median])
