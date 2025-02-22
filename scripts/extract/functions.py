import os
from multiprocessing import Pool
from itertools import repeat
import random
from tree_sitter import Language, Parser
from rich.console import Console

from scripts.parsing.parsers import *
from scripts.lang import LANGS, is_ext_valid
from db.utils import *
from db.engine import get_engine


POOL_SIZE = 4
MAX_FUNCTIONS = 10000

console = Console()

def extract_repo(repo, lang):
    repo_id, repo_name, repo_path = repo
    console.print(repo)
    successes = []
    errors = []
    extracted_functions = 0

    parser = Parser()
    parser.set_language(Language("build/parser_bindings.so", lang))
    console.print(f"Processing {repo_name} ({lang}) -> {repo_path}", style="bold red")
    session = new_session(get_engine())

    try:
        for file in list_files(repo_path):
            if ".git" in file:
                continue

            if "readme" in file.lower() or not is_ext_valid(lang, file):
                continue

            console.print(f"Processing file: {file}")

            file_order = 1
            try:
                fnames = extract(parser, file, globals()[f"extract_{lang}"])

                for fname, names in fnames.items():
                    names = " ".join(names)
                    if fname != None and 'test' in fname:
                        continue
                    add_function(session, fname, names, repo_id, file, lang, file_order)
                    file_order += 1
                    extracted_functions += 1

                    if extracted_functions >= MAX_FUNCTIONS:
                        break

                    successes.append(file)
            except Exception as e:
                console.print("Failed to parse")
                console.print(e)
                raise e
                continue

            if extracted_functions >= MAX_FUNCTIONS:
                break
    except Exception as e:
        raise e
        console.print(e)
        console.print(file)
        errors.append(file)
    finally:
        session.close()
        return [successes, errors]


def list_files(directory):
    console.print(directory)
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            yield os.path.join(dirpath, filename)


class Functions:
    @staticmethod
    def extract(langs):
        session = init_local_session()
        results = [[], []]

        for lang in langs:
            repos = Repo.get_without_functions(session, lang)
            random.shuffle(repos)
            console.print([repo.name for repo in repos])

            # for repo in repos:
            #     extract_repo((repo.id, repo.name, repo.path), lang)

            with Pool(POOL_SIZE) as p:
                result = p.starmap(extract_repo, [((repo.id, repo.name, repo.path), lang) for repo in repos])[0]
                results[0].extend(result[0])
                results[1].extend(result[1])

        console.print(f"Successes: {len(results[0])}, failures: {len(results[1])}")
        console.print(results[1])