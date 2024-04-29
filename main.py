import os
from os import path

import typer
from rich.console import Console

from scripts.download import download_lang, clone_repos
from scripts.metrics.basic import calculate as calc_basic, extract_grammar as _extract_grammar
from scripts.extract.extract_language import extract_language as _extract_language
from scripts.extract.extract_projects import extract_project as _extract_projects
from scripts.classify_project import classify as _classify
from scripts.exts import get_exts

from db.utils import init_session

console = Console()

app = typer.Typer()

BUILD_DIR = path.basename('build')
DATA_DIR = path.basename('data')
MODELS_DIR = path.join(BUILD_DIR, 'models')
PROJECTS_DIR = path.join(BUILD_DIR, 'projects')

@app.command()
def extract_language(
    lang: str,
    indir: str = typer.Argument(None, help=f'Input project directory'),
    outdir: str = typer.Argument(None, help=f'Output CSV')
):
    """
    Perform extraction for specified input project directory to a single
    file, typically:

    data/<lang>/** -> build/names/<lang>.csv
    """
    indir = indir or path.join(DATA_DIR, lang.lower())
    outdir = outdir or path.join(BUILD_DIR, 'names')
    _extract_language(lang, indir, outdir)


@app.command()
def extract_projects(
    lang: str,
    indir: str = typer.Argument(None, help=f'Input project directory'),
    outdir: str = typer.Argument(None, help=f'Output directory')
):
    indir = indir or path.join(DATA_DIR, lang.lower())
    outdir = outdir or path.join(PROJECTS_DIR, lang)
    _extract_projects(lang, indir, outdir)


@app.command()
def classify(
    lang: str,
    outdir: str = 'build/classified/',
    limit: int = 200
):
    _classify(lang, outdir, limit)


@app.command()
def extract_grammar(lang: str):
    _extract_grammar(path.join(PROJECTS_DIR, lang), lang)


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


@app.command()
def download_all(num_projects: int):
    init_session()
    langs = ['clojure', 'elixir', 'erlang', 'fortran', 'haskell', 'java',
             'javascript', 'ocaml', 'python', 'c']

    for lang in langs:
        outdir = path.join(DATA_DIR, lang.lower())
        download_lang(lang, outdir, num_projects)


@app.command()
def download(
    lang: str, 
    num_projects: int,
    outdir: str = None, 
    sanitize: bool = False
):
    init_session()
    outdir = outdir or path.join(DATA_DIR, lang.lower())
    download_lang(lang, outdir, num_projects)


@app.command()
def clone():
    init_session()
    clone_repos(DATA_DIR)


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
