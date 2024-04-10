import os

from parsing.parsers import *
from tree_sitter import Language, Parser


def list_files(directory):
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            yield os.path.join(dirpath, filename)


# Go over each file (recursively) in directory with all project for a language
# and save all names (without functions) to a single file. Used to build training set
# for word embedding model.
# data/<lang>/** -> raw/<lang>.txt

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-l', '--lang', help='language')
    arg_parser.add_argument('-o', '--output', help='output file path')
    args = arg_parser.parse_args()
    input_file = args.output

    parser = Parser()
    parser.set_language(Language('build/parser_bindings.so', args.lang))
    
    with open(input_file, 'w') as f:
        for file in list_files(f'data/{args.lang}'):
            print(f'Writing names for {file}...')

            if os.path.exists(file):
                try:
                    fnames = extract(parser, file, globals()[f'extract_{args.lang}'])

                    for _, names in fnames.items():
                        print(len(names))
                        f.write(' '.join(names))
                except Exception as e: 
                    print(e)
                    pass
