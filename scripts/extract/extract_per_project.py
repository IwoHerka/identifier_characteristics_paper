import csv
import os

from ..parsing.parsers import *
from tree_sitter import Language, Parser
from rich.console import Console

console = Console()


def list_files(directory):
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            yield os.path.join(dirpath, filename)

# Generates (function, names) CSV per project per language.
# Output typically in build/projects/<lang>/<project>.csv
# with format: <function name>, <names>
# 
# data/<lang>/** -> build/projects/<lang>/<project>.csv

def extract_project(lang, output_dir):
    parser = Parser()
    parser.set_language(Language('build/parser_bindings.so', lang))

    for directory in next(os.walk(f'data/{lang}'))[1]:
        out_file = os.path.join(output_dir, f'{directory}.csv')

        with open(out_file, 'w', newline='', encoding='utf-8') as out_file:
            writer = csv.writer(out_file)
            console.print(f'Extracting to {out_file}...', style='bold red')

            for file in list_files(f'data/{lang}/{directory}'):
                try:
                    fnames = extract(parser, file, globals()[f'extract_{lang}'])

                    for fname, names in fnames.items():
                        console.print(names, style='yellow')
                        writer.writerow([fname, ' '.join(names)]) 
                except Exception as e: 
                    print(e)
                    pass
