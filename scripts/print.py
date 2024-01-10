# Simple script to test language parsing.
# To run:
# > poetry shell
# > python scripts/print -l clojure -i examples/clojure.clj

import argparse
import os

from tree_sitter import Language, Parser


def print_haskell(node, depth=0):
    if node.type == 'function':
        print('  ' * depth + f"{node.type} {node.text}")
        
    for child in node.children:
        print_haskell(child, depth + 1)


def print_javascript(node, depth=0):
    if node.type == 'function_declaration':
        print('  ' * depth + f"{node.type} {node.text}")
        
    for child in node.children:
        print_javascript(child, depth + 1)


def print_python(node, depth=0):
    if node.type == 'function_definition':
        print('  ' * depth + f"{node.type} {node.text}")
        
    for child in node.children:
        print_python(child, depth + 1)


def print_clojure(node, depth=0):
    if node.text == b'defn' and node.parent.type == 'list_lit':
        print(node.parent.text)
        
    for child in node.children:
        print_clojure(child, depth + 1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', required=True)
    parser.add_argument('-i', required=True)
    args = parser.parse_args()

    if not os.path.exists(args.i):
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(args.i, 'r') as file:
        content = file.read()

    language = Language('build/parser_bindings.so', args.l)
    parser = Parser()
    parser.set_language(language)
    tree = parser.parse(bytes(content, "utf-8"))

    locals()[f'print_{args.l}'](tree.root_node)

