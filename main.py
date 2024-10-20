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
from scripts.metrics.term_entropy import get_term_entropy
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
    - [ ] Syllable count\n
    - [ ] Soft word count\n
    - [ ] Number of unique/duplicate identifiers\n
    - [ ] Number of single letter identifiers\n
    - [ ] Most common casing style\n
    - [x] Percent of abbreviations\n
    - [x] Percent of dictionary words\n
    - [x] External similarity\n
    - [x] Grammatical patterns\n
    - [x] Term entropy\n
    - [?] Context coverage\n
    - [?] Conciseness & consistency violations\n
    - [?] Semantic similarity\n
    - [?] Word concreteness\n
    - [?] Levenshtein distance\n
    - [ ] Lexical bad smells\n
    - [ ] Flesch–Kincaid readability\n
    - [ ] Lexical diversity (TTR)\n
    """
    indir = indir or path.join(PROJECTS_DIR, lang.lower())
    # model = model or path.join(MODELS_DIR, 'default.bin')
    calc_basic(indir, model)


@app.command()
def calc_term_entropy():
    init_session()
    get_term_entropy(257787813)


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


@app.command()
def clean(lang: str):
    """
    Remove non-code files from project directories for a given language.
    Command will print summary of files to be removed and ask for confirmation. Example:

        python main.py clean elixir
    """
    exts = set(get_exts(lang))
    to_remove = []

    for root, _, files in os.walk(f"data/{lang}"):
        for file in files:
            name, ext = os.path.splitext(file)

            if not ext.lower() in exts and name != "README":
                file_path = os.path.join(root, file)
                to_remove.append(file_path)

    if not to_remove:
        console.print("No files to remove")
        return

    # Count files by extension
    ext_counts = {}
    for file_path in to_remove:
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()  # Normalize extensions to lowercase
        ext_counts[ext] = ext_counts.get(ext, 0) + 1

    console.print("\nSummary of files to be removed:")
    for ext, count in sorted(ext_counts.items(), key=lambda x: x[1]):
        console.print(f"{ext}: {count}")

    console.print(f"\nAccepted extensions: {exts}")
    console.print(f"\nTotal files to remove: {len(to_remove)}, continue? (Y/n)")

    if console.input() == 'Y':
        console.print("Removing files...")

        for file in to_remove:
            os.remove(file)

        console.print("Done")
    else:
        console.print("Aborting...")


if __name__ == "__main__":
    app()