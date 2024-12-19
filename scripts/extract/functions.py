import os
from multiprocessing import Pool
from itertools import repeat

from tree_sitter import Language, Parser
from rich.console import Console

from scripts.parsing.parsers import *
from scripts.lang import LANGS, is_ext_valid
from db.utils import *
from db.engine import get_engine


POOL_SIZE = 8
MAX_FUNCTIONS = 1000

console = Console()

def extract_repo(repo, lang):
    repo_id, repo_name, repo_path = repo
    console.print(repo)
    successes = []
    errors = []
    extracted_functions = 0

    parser = Parser()
    parser.set_language(Language("build/parser_bindings.so", lang))
    console.print(
        f"Processing {repo_name} ({lang}) -> {repo_path}", style="bold red"
    )

    for file in list_files(repo_path):
        if "README.md" in file or not is_ext_valid(lang, file):
            continue

        console.print(f"Processing file: {file}")
        file_order = 1

        try:
            session = new_session(get_engine())
            fnames = extract(parser, file, globals()[f"extract_{lang}"])

            for fname, names in fnames.items():
                names = " ".join(names)
                add_function(session, fname, names, repo_id, file, lang, file_order)
                file_order += 1
                extracted_functions += 1

                if extracted_functions >= MAX_FUNCTIONS:
                    break

            successes.append(file)
        except RecursionError as e:
            pass
        except FileNotFoundError:
            pass
        except Exception as e:
            # TODO: Log more info
            console.print(file)
            errors.append(file)

        if extracted_functions >= MAX_FUNCTIONS:
            break

    return [successes, errors]

def list_files(directory):
    console.print(directory)
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            yield os.path.join(dirpath, filename)


class Functions:
    @staticmethod
    def extract(langs):
        results = [[], []]

        for lang in langs:
            repos = get_repos_without_functions(lang=lang)
            console.print(repos)

            with Pool(POOL_SIZE) as p:
                result = p.starmap(extract_repo, [((repo.id, repo.name, repo.path), lang) for repo in repos])[0]
                results[0].extend(result[0])
                results[1].extend(result[1])

        console.print(f"Successes: {len(results[0])}, failures: {len(results[1])}")
        console.print(results[1])