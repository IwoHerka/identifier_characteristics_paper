# Script to calculate overall mean and median for a language
# based on a project report (median for each project).

import argparse
import fasttext

from utils import overall_mean, overall_median

MODEL = 'build/models/all.bin'


if __name__ == '__main__':
    model = fasttext.load_model(MODEL)

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-l', '--lang')
    args = arg_parser.parse_args()
    lang = args.lang

    medians = []
    means = []

    with open(f'build/projects/reports/{lang}.csv', 'r') as file:
        for line in file.read().splitlines():
            [project, median] = line.split(',')
            medians.append(median)
       

    median = overall_median(medians)
    mean = overall_mean(medians)

    print(mean)
    print(median)

