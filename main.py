import os
from os import path

# similarity():
import fasttext
import typer
from rich.console import Console
from scipy.spatial.distance import cosine

from db.utils import init_session
from scripts.classify import classify as _classify
from scripts.download import clone_repos, download_repos
from scripts.extract.functions import Functions
from scripts.extract.grammar import Grammar
from scripts.lang import LANGS, get_exts
from scripts.metrics.basic import calculate as calc_basic
from scripts.training.train_fasttext import train as _train_fasttext
from scripts.training.train_gensim import train as _train_gensim
from scripts.similarity.calculate_similarity_per_project import calculate

console = Console()
app = typer.Typer()

BUILD_DIR = path.basename("build")
DATA_DIR = path.basename("data")
MODELS_DIR = path.join(BUILD_DIR, "models")
PROJECTS_DIR = path.join(BUILD_DIR, "projects")
FASTTEXT_TRAINING_FILE = path.join(MODELS_DIR, "training_file.txt")
FASTTEXT_MODEL_FILE = path.join(MODELS_DIR, "fasttext.bin")
GENSIM_MODEL_FILE = path.join(MODELS_DIR, "gensim.model")

# TODO: Automate extract functions
# TODO: Automate prepare training data
# TODO: Automate training fasttext
# TODO: Automate calculate similarity
# TODO: Add function to build co-occurance matrix for all project corpus to
# calculate LSI-derived conceptual/relational similarity


@app.command()
def train_fasttext():
    init_session()
    _train_fasttext(FASTTEXT_TRAINING_FILE, FASTTEXT_MODEL_FILE)


@app.command()
def train_gensim():
    init_session()
    _train_gensim(GENSIM_MODEL_FILE)


@app.command()
def calc_similarity(lang: str, model: str = None):
    model = model or path.join(MODELS_DIR, 'default.bin')
    calculate(model, lang)


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


# Uses OpenAI
@app.command()
def classify(lang: str, outdir: str = "build/classified/", limit: int = 200):
    _classify(lang, outdir, limit)


# Extract grammar for each function, uses
@app.command()
def extract_grammar():
    init_session()
    Grammar.extract()


@app.command()
def calculate_metrics(lang: str, model: str, indir: str = None):
    """
    - [ ] Identifier length\n
    - [ ] Number of unique/duplicate identifiers\n
    - [ ] Number of single letter identifiers\n
    - [ ] Most common casing style\n
    - [x] Percent of abbreviations\n
    - [x] Percent of dictionary words\n
    - [x] Levenshtein distance\n
    - [x] Term entropy\n
    - [x] Conciseness & consistency violations\n
    - [x] Context coverage\n
    - [x] Semantic similarity\n
    - [x] External similarity\n
    - [x] Grammatical patterns\n
    - [^] Word concreteness\n
    - [ ] Lexical bad smells\n
    """
    indir = indir or path.join(PROJECTS_DIR, lang.lower())
    # model = model or path.join(MODELS_DIR, 'default.bin')
    calc_basic(indir, model)


# Example: python main.py elixir 1000
@app.command()
def download_repo_info(num_projects: int, lang: str = None):
    """
    Download repository information. Populates 'repos' table. Table must be
    empty before running this command to avoid integrity error. Command expects
    GITHUB_TOKEN env variable to contain valid Github's personal access token.
    As of 09/24, current rate limit for repository search endpoint for
    authorized users is 30 requests per minute. In case of 403's check if rate
    limit changed and adjust GITHUB_REQUEST_DELAY which specifies time in seconds
    to wait between requests (defaults to 2).
    """
    if lang == None:
        init_session()
        for lang in LANGS:
            outdir = path.join(DATA_DIR, lang.lower())
            download_repos(lang, outdir, num_projects)

    elif lang in LANGS:
        init_session()
        outdir = path.join(DATA_DIR, lang.lower())
        download_repos(lang, outdir, num_projects)


@app.command()
def clone(force: bool = False, missing: bool = False):
    init_session()
    clone_repos(DATA_DIR, force, missing)


@app.command()
def clean(lang: str):
    exts = set(get_exts(lang))
    to_remove = []

    for root, dirs, files in os.walk(f"data/{lang}"):
        for file in files:
            name, ext = os.path.splitext(file)

            if not ext.lower() in exts and name != "README":
                file_path = os.path.join(root, file)
                to_remove.append(file_path)

    for file in to_remove:
        os.remove(file)


if __name__ == "__main__":
    app()
