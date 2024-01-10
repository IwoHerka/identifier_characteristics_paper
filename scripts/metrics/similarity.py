import json
import random
from collections import deque
from itertools import combinations

import casestyle
import fasttext
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats as stats
from matplotlib.ticker import ScalarFormatter
from rich.console import Console
from scipy.spatial.distance import cosine

from db.models import Repo
from db.utils import get_functions_for_repo, init_local_session
from scripts.lang import LANGS

console = Console()

MODEL_NAME = "ft_19M_100x1000_5ws"
MODEL = f"build/models/{MODEL_NAME}.bin"


def calc_median_dist(session, repos, model):
    medians = []

    for repo in repos:
        for function in get_functions_for_repo(repo.id, session):
            console.print(f"{function.name}")

            if function.median_id_semantic_similarity is not None:
                medians.append(function.median_id_semantic_similarity)
                continue

            names = function.names.split(" ")

            if len(names) < 2:
                continue

            all_names = list(combinations(random.sample(names, len(names)), 2))
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
                cos = cosine(
                    model.get_word_vector(name_a), model.get_word_vector(name_b)
                )

                if cos != None:
                    prev_cosines[(name1, name2)] = cos
                    cosines.append(cos)
                else:
                    console.print(f"Cosine is None for {name1} and {name2}")

            median = statistics.median(cosines)

            if median != None:
                function.median_id_semantic_similarity = median
                session.commit()
                console.print(f"{function.name} = {median}")
                medians.append(median)
            else:
                console.print(
                    f"Median is None for {function.name}, num names: {len(names)}"
                )

    return medians


def calculate_similarity():
    session = init_local_session()
    model = fasttext.load_model(MODEL)

    for lang in LANGS:
        repos = Repo.all(session, lang=lang, selected=True)
        calc_median_dist(session, repos, model)
