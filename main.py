import os
from os import path

import typer
from rich.console import Console

from scripts.download import download_all
from scripts.metrics.basic import calculate as calc_basic
from scripts.extract.extract_per_project import extract_project
from scripts.classify_project import classify as _classify

console = Console()

app = typer.Typer()

BUILD_DIR = path.basename('build')
DATA_DIR = path.basename('data')
MODELS_DIR = path.join(BUILD_DIR, 'models')
PROJECTS_DIR = path.join(BUILD_DIR, 'projects')

@app.command()
def extract(
    lang: str,
    outdir: str
):
    extract_project(lang, outdir)


@app.command()
def classify(
    lang: str,
    outdir: str = 'build/classified/',
    limit: int = 200
):
    _classify(lang, outdir, limit)


@app.command()
def calculate_metrics(
    lang: str,
    model: str,
    indir: str = typer.Argument(None, help=f'Project input directory, {PROJECTS_DIR}/<lang> by default')
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
    - [ ] Lexical bad smells\n
    - [^] Word concreteness\n
    """
    indir = indir or path.join(PROJECTS_DIR, lang.lower())
    # model = model or path.join(MODELS_DIR, 'default.bin')
    calc_basic(indir, model)



@app.command()
def download(
    lang: str, 
    ext: str, 
    outdir: str = None, 
    min_page: int=1, 
    max_page: int=10,
    per_page: int=100,
    sanitize: bool=False
):
    outdir = outdir or path.join(DATA_DIR, lang.lower())
    download_all(lang, ext, outdir, min_page, max_page, per_page)

    if sanitize:
        console.print('Sanitizing', style='bold red')
        os.system(f'find {outdir}/ -type f ! -name \'{ext}\' -exec rm -f -v {{}} +')
        os.system(f'find {outdir}/ -type d -empty -delete')
        console.print('Done', style='bold red')


if __name__ == "__main__":
    app()
