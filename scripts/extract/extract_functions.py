import os
from multiprocessing import Pool
from itertools import repeat

from tree_sitter import Language, Parser
from rich.console import Console

from ..parsing.parsers import *
from ..exts import is_ext_valid
from ..lang import LANGS
from db.utils import *
from db.engine import get_engine

console = Console()


def list_files(directory):
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            yield os.path.join(dirpath, filename)


def extract_repo(repo, lang):
    session = new_session(get_engine())
    parser = Parser()
    parser.set_language(Language('build/parser_bindings.so', lang))
    console.print(f'Processing {repo.name} ({repo.lang}) -> {repo.path}', style='bold red')

    for file in list_files(repo.path):
        if 'README.md' in file or not is_ext_valid(lang, file):
            continue

        file_order = 1

        try:
            fnames = extract(parser, file, globals()[f'extract_{lang}'])
            
            for fname, names in fnames.items():
                names = ' '.join(names)
                add_function(session, fname, names, repo.id, file, lang, file_order)
                file_order += 1
        except RecursionError as e:
            pass
        except FileNotFoundError:
            pass
        except Exception as e: 
            # TODO: Fix extraction errors to uncomment this
            console.print(file)
            raise e


def extract_functions():
    for lang in ['c']:#LANGS:
        repos = get_repos_with_no_functions(lang=lang)

        with Pool(20) as p:
            p.starmap(extract_repo, zip(repos, repeat(lang)))
