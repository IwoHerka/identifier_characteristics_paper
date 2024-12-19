import os
from os import path

# similarity():
import fasttext
import typer
from rich.console import Console
from scipy.spatial.distance import cosine

from db.utils import init_session
from scripts.metrics.llm.classify import classify as _classify
from scripts.download import clone_repos, download_repos
from scripts.extract.functions import Functions
from scripts.extract.grammar import Grammar
from scripts.lang import LANGS, get_exts
from scripts.training.train_fasttext import train as _train_fasttext
from scripts.similarity.calculate_similarity_per_project import calculate
from scripts.metrics.term_entropy import calculate_term_entropy
from scripts.metrics.llm.rate import rate_lexicon, rate_relevancy, classify_all_repos
from scripts.metrics.basic import calculate_basic_metrics
from scripts.similarity.calculate_similarity_from_sampled import plot_similarity as _plot_similarity

console = Console()
app = typer.Typer()

BUILD_DIR = path.basename("build")
DATA_DIR = path.basename("data")
MODELS_DIR = path.join(BUILD_DIR, "models")
PROJECTS_DIR = path.join(BUILD_DIR, "projects")
FASTTEXT_TRAINING_FILE = path.join(MODELS_DIR, "training_file.txt")
FASTTEXT_MODEL_FILE = path.join(MODELS_DIR, "fasttext.bin")
GENSIM_MODEL_FILE = path.join(MODELS_DIR, "gensim.model")

# Library
# TODO: Automatically discard suspicious functions (obsfucated, etc)
# TODO: Automate extract functions
# TODO: Automate prepare training data
# TODO: Automate training fasttext
# TODO: Automate calculate similarity (also for concreteness)
# TODO: Add function to build co-occurance matrix for all project corpus to
# TODO Use LLM to filter out functions that are not relevant for humans
# calculate LSI-derived conceptual/relational similarity
# TODO Check accuracy of LLM classifications (small sample, myself)

# Analysis
# TODO In analysis, give metric which is which lang has more < 0.2 similarity functions

# Threats to validity:
# - LLM rating is not a perfect measure of comprehensibility
# - Included functions are not discriminated (boilerplate functions are included)


@app.command()
def train_fasttext():
    """
    Generates training file based on function names in database and trains
    fasttext model.
    """
    init_session()
    _train_fasttext(FASTTEXT_TRAINING_FILE, MODELS_DIR)


@app.command()
def calc_basic_metrics():
    """
    - Median identifier length\n
    - Median syllable count\n
    - Median soft word count\n
    - Ratio of unique to duplicate identifiers\n
    - Number of single letter identifiers\n
    - Most common casing style\n
    - Percent of abbreviations\n
    - Percent of dictionary words\n
    - Levenshtein distance (within function)\n (add within identifiers?)
    - Conciseness & consistency violations\n

    - Term entropy\n
    - Semantic similarity\n (NTLK model) (add support for 2 context windows)
    - Grammatical patterns\n

    - [WIP] External similarity\n
    - [WIP] Context coverage\n
    - [WIP] Word concreteness\n
    """
    init_session()
    calculate_basic_metrics()


@app.command()
def calc_term_entropy():
    init_session()
    calculate_term_entropy()


@app.command()
def word_similarity(a: str, b: str, model: str):
    """
    Calculate cosine distance for two words using specified model.
    """
    model = fasttext.load_model(f"build/models/{model}.bin")
    cos = cosine(model.get_word_vector(a), model.get_word_vector(b))
    console.print(cos)


@app.command()
def extract_functions(lang=None):
    langs = None

    if lang != None:
        langs = [lang]
    else:
        langs = LANGS

    init_session()
    Functions.extract(langs)


@app.command()
def plot_similarity(verbose: bool = False):
    _plot_similarity(verbose)


@app.command()
def rate_lexicon_llm(repo_id: int):
    rate_lexicon(repo_id)


@app.command()
def rate_relevancy_llm(repo_id: int):
    rate_relevancy(repo_id)


@app.command()
def classify_repo_llm():
    classify_all_repos()


# Extract grammar for each function, uses
@app.command()
def extract_grammar():
    init_session()
    Grammar.extract()


# TODO: Only download repos that are not already downloaded
# TODO: Add option to download only missing up to given number of projects
# TODO: Rename to seed?
@app.command()
def download_repo_info(num_projects: int, lang: str = None):
    """
    Download repository information. Populates 'repos' table. Table must be
    empty for a given language before running this command to avoid integrity
    error. Command expects GITHUB_TOKEN env variable to contain valid Github's
    personal access token.  As of 09/24, current rate limit for repository
    search endpoint for authorized users is 30 requests per minute. In case of
    403's check if rate limit changed and adjust GITHUB_REQUEST_DELAY which
    specifies time in seconds to wait between requests (defaults to 2). Example:

        python main.py download-repo-info 100 --lang=elixir
    """
    init_session()

    if lang == None:
        for lang in LANGS:
            outdir = path.join(DATA_DIR, lang.lower())
            download_repos(lang, outdir, num_projects)

    elif lang in LANGS:
        outdir = path.join(DATA_DIR, lang.lower())
        download_repos(lang, outdir, num_projects)



# TODO: Check repos state, fix command
# TODO: Remove repos that failed to cloned and fix
@app.command()
def clone(force: bool = False, only_missing: bool = False):
    """
    Clone repositories from Github.
    """
    init_session()
    clone_repos(DATA_DIR, force, only_missing)


if __name__ == "__main__":
    app()