import os
import csv

from parsing.parsers import *
from tree_sitter import Language, Parser


def list_files(directory):
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            yield os.path.join(dirpath, filename)

# Generates (function, names) CSV per project per language.
# Output typically in build/projects/<lang>/<project>.csv
# with format: <function name>, <names>

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-l', '--lang')
    arg_parser.add_argument('-o', '--output_dir')
    args = arg_parser.parse_args()

    parser = Parser()
    parser.set_language(Language('build/parser_bindings.so', args.lang))

    for directory in next(os.walk(f'data/{args.lang}'))[1]:
        out_file = os.path.join(args.output_dir, f'{directory}.csv')

        with open(out_file, 'w', newline='', encoding='utf-8') as out_file:
            writer = csv.writer(out_file)
            print(f'Extracting to {out_file}...')

            for file in list_files(f'data/{args.lang}/{directory}'):
                try:
                    fnames = extract(parser, file, globals()[f'extract_{args.lang}'])

                    for fname, names in fnames.items():
                        writer.writerow([fname, ' '.join(names)]) 
                except Exception as e: 
                    print(e)
                    pass
