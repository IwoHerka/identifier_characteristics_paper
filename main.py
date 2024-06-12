import os
from os import path

import typer
from rich.console import Console

# similarity():
import fasttext
from scipy.spatial.distance import cosine

from scripts.download import download_lang, clone_repos
from scripts.metrics.basic import calculate as calc_basic
from scripts.extract.extract_grammar import extract_grammar as _extract_grammar
from scripts.extract.extract_functions import extract_functions as _extract_functions
from scripts.classify_project import classify as _classify
from scripts.training.train_fasttext import train_fasttext
from scripts.exts import get_exts
from scripts.lang import LANGS

from db.utils import init_session

console = Console()
app = typer.Typer()

BUILD_DIR = path.basename('build')
DATA_DIR = path.basename('data')
MODELS_DIR = path.join(BUILD_DIR, 'models')
PROJECTS_DIR = path.join(BUILD_DIR, 'projects')
FASTTEXT_TRAINING_FILE = path.join(BUILD_DIR, 'training_file.txt')
FASTTEXT_MODEL_FILE = path.join(BUILD_DIR, 'fasttext.bin')

# TODO: Automate extract functions
# TODO: Automate prepare training data
# TODO: Automate training fasttext
# TODO: Automate calculate similarity
# TODO: Add function to build co-occurance matrix for all project corpus to 
# calculate LSI-derived conceptual/relational similarity

@app.command()
def prepare_training_data():
    corpus = train_fasttext(FASTTEXT_TRAINING_FILE, FASTTEXT_MODEL_FILE)
    


@app.command()
def similarity(a: str, b: str, model: str):
    """
    Calculate cosine distance for two words using specified model.
    """
    model = fasttext.load_model(f'build/models/{model}.bin')
    cos = cosine(model.get_word_vector(a), model.get_word_vector(b))
    console.print(cos)


@app.command()
def extract_functions():
    init_session()
    _extract_functions()


# Uses OpenAI
@app.command()
def classify(
    lang: str,
    outdir: str = 'build/classified/',
    limit: int = 200
):
    _classify(lang, outdir, limit)


# Extract grammar for each function, uses
@app.command()
def extract_grammar():
    init_session()
    _extract_grammar()


@app.command()
def calculate_metrics(
    lang: str,
    model: str,
    indir: str = None
):
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
    if lang == None:
        init_session()
        for lang in LANGS:
            outdir = path.join(DATA_DIR, lang.lower())
            download_lang(lang, outdir, num_projects)

    elif lang in LANGS:
        init_session()
        outdir = outdir or path.join(DATA_DIR, lang.lower())
        download_lang(lang, outdir, num_projects)


@app.command()
def clone():
    init_session()
    clone_repos(DATA_DIR)


# Tested and working?
@app.command()
def clean(lang: str):
    exts = set(get_exts(lang))
    to_remove = []

    for root, dirs, files in os.walk(f'data/{lang}'):
        for file in files:
            name, ext = os.path.splitext(file)

            if not ext.lower() in exts and name != 'README':
                file_path = os.path.join(root, file)
                to_remove.append(file_path)

    for file in to_remove:
        os.remove(file)


if __name__ == "__main__":
    app()
