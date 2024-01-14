# Simple script to test language parsing.
# To run:
# > poetry shell
# > python scripts/print -l clojure -i examples/clojure.clj

import argparse
import os

from parsers import *
from collections import defaultdict
from tree_sitter import Language, Parser


def print_ast(node, depth=0):
    print(' ' * depth + f'{node.type} {node.text}')

    for child in node.children:
        print_ast(child, depth + 1)


def print_lang(node, extract_fn):
    acc = defaultdict(list)
    extract_fn(node, acc, unique_id())

    for (fun, names) in acc.items():
        print(f'{fun}: {", ".join(names)}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', required=True)
    parser.add_argument('-i', required=False)
    parser.add_argument('-ast', required=False)
    args = parser.parse_args()
    input_file = args.i

    if not os.path.exists(input_file):
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(input_file, 'r') as file:
        content = file.read()

    language = Language('build/parser_bindings.so', args.l)
    parser = Parser()
    parser.set_language(language)
    tree = parser.parse(bytes(content, "utf-8"))

    if args.ast:
        print_ast(tree.root_node)
    else:
        print_lang(tree.root_node, globals()[f'extract_{args.l}'])
