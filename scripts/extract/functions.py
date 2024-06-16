import os
from multiprocessing import Pool
from itertools import repeat

from tree_sitter import Language, Parser
from rich.console import Console

from scripts.parsing.parsers import *
from scripts.lang import LANGS, is_ext_valid
from db.utils import *
from db.engine import get_engine


POOL_SIZE = 20

console = Console()


class Functions:
    @staticmethod
    def extract(langs):
        results = [[], []]

        for lang in langs:
            repos = get_repos_without_functions(lang=lang)[:1]
            console.print(repos)

            with Pool(POOL_SIZE) as p:
                result = p.starmap(__extract_repo, zip(repos, repeat(lang)))[0]
                results[0].extend(result[0])
                results[1].extend(result[1])

        console.print(f'Successes: {len(results[0])}, failures: {len(results[1])}')


    def __list_files(directory):
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                yield os.path.join(dirpath, filename)


    def __extract_repo(repo, lang):
        successes = []
        errors = []

        session = new_session(get_engine())
        parser = Parser()
        parser.set_language(Language('build/parser_bindings.so', lang))
        console.print(f'Processing {repo.name} ({repo.lang}) -> {repo.path}', style='bold red')

        for file in __list_files(repo.path):
            if 'README.md' in file or not is_ext_valid(lang, file):
                continue

            console.print(f'Processing file: {file}')
            file_order = 1

            try:
                fnames = extract(parser, file, globals()[f'extract_{lang}'])
                
                for fname, names in fnames.items():
                    names = ' '.join(names)
                    add_function(session, fname, names, repo.id, file, lang, file_order)
                    file_order += 1

                successes.append(file)
            except RecursionError as e:
                pass
            except FileNotFoundError:
                pass
            except Exception as e: 
                console.print(file)
                errors.append(file)

        return [successes, errors]
