import csv
from collections import defaultdict

import casestyle

from db.models import Function
from db.utils import init_local_session


def get_soft_words(identifier):
    return casestyle.casepreprocess(identifier.strip("_"))


def get_frequency_distribution():
    total_count = 0
    word_to_num_occurrences = defaultdict(lambda: 0)
    word_to_prob = {}

    session = init_local_session()

    for names in Function.get_all_names(session):
        names = names[0].split(" ")
        for name in names:
            soft_words = get_soft_words(name)

            for word in soft_words:
                word_to_num_occurrences[word] += 1
                total_count += 1

    for word, num_occurrences in word_to_num_occurrences.items():
        word_to_prob[word] = num_occurrences / total_count

    with open("build/frequency_distribution.csv", "w") as f:
        writer = csv.writer(f)

        for word, prob in word_to_prob.items():
            writer.writerow([word, prob])
