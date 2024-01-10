import os
from os import path

import fasttext
import typer
from rich.console import Console
from scipy.spatial.distance import cosine

from db.models import Repo
from db.utils import init_local_session, init_session
from scripts.statistics import Statistics
from scripts.download import clone_repos, download_repos
from scripts.extract.functions import Functions
from scripts.extract.grammar import Grammar
from scripts.lang import LANGS
from scripts.metrics.basic import calculate_basic_metrics, calculate_context_coverage
from scripts.metrics.concreteness import calculate_word_concreteness
from scripts.metrics.term_entropy import calculate_term_entropy
from scripts.metrics.similarity import calculate_similarity
from scripts.training.train_fasttext import train as _train_fasttext

console = Console()
app = typer.Typer()

BUILD_DIR = path.basename("build")
DATA_DIR = path.basename("data")
MODELS_DIR = path.join(BUILD_DIR, "models")
FASTTEXT_TRAINING_FILE = path.join(MODELS_DIR, "training_file.txt")


@app.command()
def train_fasttext():
    init_session()
    _train_fasttext(FASTTEXT_TRAINING_FILE, MODELS_DIR)


@app.command()
def calc_basic_metrics():
    init_session()
    calculate_basic_metrics()


@app.command()
def calc_context_coverage():
    calculate_context_coverage()


@app.command()
def calc_word_concreteness():
    calculate_word_concreteness()


@app.command()
def calc_term_entropy():
    calculate_term_entropy()


@app.command()
def calc_similarity():
    calculate_similarity()


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
def extract_grammar():
    init_session()
    Grammar.extract()


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


@app.command()
def clone(force: bool = False, only_missing: bool = False):
    """
    Clone repositories from Github.
    """
    init_session()
    clone_repos(DATA_DIR, force, only_missing)


@app.command()
def check_distribution():
    Statistics().check_distribution()


@app.command()
def art():
    Statistics().execute_art()


@app.command()
def anova():
    Statistics().execute_anova()


if __name__ == "__main__":
    app()