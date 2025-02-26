import nltk
import statistics
import csv
import string
import casestyle
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
from db.utils import init_local_session

NUM_PROCESSES = 4
LANGS = [
    "c",
    "clojure",
    "elixir",
    "erlang",
    "fortran",
    # "haskell",
    "java",
    # "javascript",
    "ocaml",
    "python",
]


console = Console()


if __name__ == "__main__":
  session = init_local_session()

  for lang in LANGS:
    for repo in Repo.all(session, lang=lang):
      if repo.ntype not in ['frontend', 'backend', 'infr', 'edu', 'db', 'cli', 'lang', 'ml', 'game', 'test', 'comp',
              'build', 'code', 'log', 'seman', 'struct', 'ui']:
        continue

      functions = Function.filter_by(session, repo_id=repo.id)

      if functions[0].median_external_similarity is not None:
        continue

      with tempfile.NamedTemporaryFile(delete=True) as f:
        for function in functions:
          f.write(f"{function.names}\n".encode('utf-8'))

        model = fasttext.train_unsupervised(f.name, "cbow", minCount=3, lr=0.1, ws=5, epoch=5, dim=100, thread=24)

        for function in functions:
          all_similarities = []

          for name in function.names.split():
            similar_words = model.get_nearest_neighbors(name, k=1)
            median_external_similarity = similar_words[0][0]
            all_similarities.append(median_external_similarity)

          function.median_external_similarity = statistics.median(all_similarities)

        session.commit()