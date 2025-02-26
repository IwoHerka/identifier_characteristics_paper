import nltk
import statistics
import csv
import string
import casestyle
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

ABBREVIATIONS = {}
CONC_RATINGS = {}
WORD_TO_PROG_PROB = {}
WORD_TO_ENG_PROB = {}
R_SIM = None # 2
C_SIM = None # 5

porter = PorterStemmer()
lancaster = LancasterStemmer()
snowball = SnowballStemmer('english')


def get_r_similarity(word1, word2):
  return 1.0 - cosine(
    R_SIM.get_word_vector(word1),
    R_SIM.get_word_vector(word2)
  )


def get_c_similarity(word1, word2):
  return 1.0 - cosine(
    C_SIM.get_word_vector(word1),
    C_SIM.get_word_vector(word2)
  )


def initialize():
  global R_SIM, C_SIM, CONC_RATINGS, ABBREVIATIONS, WORD_TO_PROG_PROB, WORD_TO_ENG_PROB

  with open("build/frequency_distribution.csv", "r") as f:
    reader = csv.reader(f)
    for row in reader:
      WORD_TO_PROG_PROB[row[0]] = float(row[1])

  console.print("Loaded program probability distribution")

  with open("build/concretness_ratings.csv", "r") as f:
    reader = csv.reader(f, delimiter='\t')
    for row in reader:
      CONC_RATINGS[row[0]] = float(row[2])

  console.print("Loaded concreteness ratings")

  with open("build/abbreviations.csv", "r") as f:
    reader = csv.reader(f)
    for row in reader:
      ABBREVIATIONS[row[0]] = row[1]

  console.print("Loaded abbreviations")

  # Download Gutenberg corpus if not already downloaded
  nltk.download('gutenberg')
  nltk.download('punkt')

  # Load and tokenize the corpus
  corpus_words = []
  for file_id in gutenberg.fileids():
      words = nltk.word_tokenize(gutenberg.raw(file_id).lower())  # Convert to lowercase
      words = [word for word in words if word.isalpha()]  # Remove punctuation/numbers
      corpus_words.extend(words)

  # Count word frequencies
  word_counts = Counter(corpus_words)
  total_words = sum(word_counts.values())

  # Compute probability distribution
  WORD_TO_ENG_PROB = {word: count / total_words for word, count in word_counts.items()}

  console.print("Loaded English corpus")

  R_SIM = fasttext.load_model("build/models/ft_19M_100x1000_2ws.bin")
  C_SIM = fasttext.load_model("build/models/ft_19M_100x1000_5ws.bin")

  console.print("Loaded rSim and cSim models")


def justify_concreteness(word):
  code_prob = WORD_TO_PROG_PROB.get(word, 0.0)
  eng_prob = WORD_TO_ENG_PROB.get(word, 0.0)

  if code_prob > 0.0 and eng_prob > 0.0:
    return CONC_RATINGS.get(word, 0.0)

  return 0.0


def get_stem_concreteness(word):
  stems = [
    porter.stem(word),
    lancaster.stem(word),
    snowball.stem(word)
  ]

  for stem in stems:
    if stem in CONC_RATINGS:
      return CONC_RATINGS[stem]

  return None


def get_unigram_concreteness(word):
  if word in CONC_RATINGS:
    # console.print(f"Found {word} in concreteness ratings")
    return CONC_RATINGS[word]

  if word in ABBREVIATIONS:
    # console.print(f"Found {word} in abbreviations")
    return get_unigram_concreteness(ABBREVIATIONS[word])

  stem_conc = get_stem_concreteness(word)
  if stem_conc is not None:
    # console.print(f"Found {word} in stem concreteness")
    return stem_conc

  return 0.0


def get_pairs(words, n):
  return list(combinations(words, n))


def get_multigram_concreteness(word):
  soft_words = casestyle.casepreprocess(word.strip("_"))
  # console.print(soft_words)

  if len(soft_words) == 0:
    return None

  max_uni_conc = max([get_unigram_concreteness(word) for word in soft_words])
  # console.print(f"Max unigram concreteness: {max_uni_conc}")

  cgc = 0.0

  for word1, word2 in get_pairs(soft_words, 2):
    cgc += get_r_similarity(word1, word2) * (1 - get_c_similarity(word1, word2))

  # console.print(f"CGC: {cgc}")
  multigram_conc = max_uni_conc * (1 + cgc)
  # console.print(f"Multigram concreteness: {multigram_conc}")

  return multigram_conc


def process(lang):
  session = init_local_session()

  for repo in Repo.all(session, lang=lang):
    if repo.ntype is None or repo.ntype == "":
        continue

    if repo.ntype not in ['frontend', 'backend', 'infr', 'edu', 'db', 'cli', 'lang', 'ml', 'game', 'test', 'comp',
            'build', 'code', 'log', 'seman', 'struct', 'ui']:
      continue

    # if repo.lang in ["javascript", "haskell"]:
    #   continue

    functions = Function.filter_by(session, repo_id=repo.id)

    for function in functions:
      if function.median_word_concreteness is not None:
        continue

      names = function.names.split(' ')

      values = [get_multigram_concreteness(name) for name in names]
      values = [v for v in values if v is not None]

      if len(values) == 0:
        continue

      median_conc = statistics.median(values)
      console.print(f"Median concreteness: {median_conc}")
      function.median_word_concreteness = median_conc
      session.commit()

  session.close()


if __name__ == "__main__":
  initialize()
  processes = []

  for lang in LANGS:
      p = Process(target=process, args=(lang,))
      p.start()
      processes.append(p)

  for p in processes:
      p.join()
