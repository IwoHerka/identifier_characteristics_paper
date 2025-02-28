import nltk
import statistics
import csv
import string
import casestyle
import random
import tempfile
import fasttext

from multiprocessing import Process
from itertools import combinations
from nltk.stem import PorterStemmer, LancasterStemmer, SnowballStemmer
from nltk.corpus import gutenberg
from collections import Counter, defaultdict
from rich.console import Console
from scipy.spatial.distance import cosine
from db.models import Function, Repo
import casestyle
from db.utils import init_local_session
from itertools import combinations
from scipy.spatial.distance import cosine

NUM_PROCESSES = 4
LANGS = [
    # "c",
    # "clojure",
    # "elixir",
    # "erlang",
    # "fortran",
    "haskell",
    # "java",
    "javascript",
    # "ocaml",
    # "python",
]


console = Console()

def all_pairs(strings):
    return list(combinations(strings, 2))


if __name__ == "__main__":
    session = init_local_session()
    model = fasttext.load_model("build/models/ft_19M_100x1000_5ws.bin")

    for lang in LANGS:
        for repo in Repo.all(session, lang=lang, selected=True):
            functions = Function.filter_by(session, repo_id=repo.id)

            for function in functions:
                if function.median_id_semantic_similarity is not None:
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

                    name_a = casestyle.camelcase(name1).lower()
                    name_b = casestyle.camelcase(name2).lower()
                    cos = cosine(model.get_word_vector(name_a), model.get_word_vector(name_b))

                    if cos != None:
                        prev_cosines[(name1, name2)] = cos
                        cosines.append(cos)
                    else:
                        console.print(f"Cosine is None for {name1} and {name2}")

                median = statistics.median(cosines)

                if median != None:
                    function.median_id_semantic_similarity = median
                    session.add(function)
                    try:
                        console.print(f"{function.name} = {median}")
                    except:
                        pass

            session.commit()

        
      # with tempfile.NamedTemporaryFile(delete=True) as f:
      #   for function in functions:
      #     f.write(f"{function.names}\n".encode('utf-8'))

      #   model = fasttext.train_unsupervised(f.name, "cbow", minCount=3, lr=0.1, ws=5, epoch=5, dim=100, thread=24)

      #   for function in functions:
      #     all_similarities = []

      #     for name in function.names.split():
      #       similar_words = model.get_nearest_neighbors(name, k=1)
      #       median_external_similarity = similar_words[0][0]
      #       all_similarities.append(median_external_similarity)

      #     function.median_external_similarity = statistics.median(all_similarities)
      #     console.print(function.median_external_similarity)
      #     session.add(function)

      #   session.commit()

