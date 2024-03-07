import os
import csv

from parsing.parsers import *
from tree_sitter import Language, Parser


def list_files(directory):
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            yield os.path.join(dirpath, filename)

# Generates (function, names) CSV per language with all projects.

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-l', '--lang', help='language')
    arg_parser.add_argument('-o', '--output', help='output file path')
    args = arg_parser.parse_args()

    parser = Parser()
    parser.set_language(Language('build/parser_bindings.so', args.lang))
    
    with open(args.output, 'w', newline='', encoding='utf-8') as out_file:
        writer = csv.writer(out_file)

        for file in list_files(f'data/{args.lang}'):
            print(f'Writing names for {file}...')

            try:
                fnames = extract(parser, file, globals()[f'extract_{args.lang}'])

                for fname, names in fnames.items():
                    print(names)
                    writer.writerow([fname, ' '.join(names)]) 
            except Exception as e: 
                print(e)
                pass
