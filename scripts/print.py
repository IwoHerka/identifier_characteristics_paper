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
        print('  ' * depth + f'{node.type} {node.text}')
        
    for child in node.children:
        print_javascript(child, depth + 1)


def print_python(node, depth=0):
    if node.type == 'function_definition':
        print('  ' * depth + f"{node.type} {node.text}")
        
    for child in node.children:
        print_python(child, depth + 1)


clj_kwds = [b'defn', b'defn-', b'def', b'defmacro', b'defmethod']

def print_clojure(node, in_fun=False):
    is_defn = node.type == 'list_lit' and node.children[1].text in clj_kwds

    if is_defn:
        print(f'F: {str(node.children[2].text, encoding="utf-8")}', end=' ')

    if in_fun and node.type in ['sym_name', 'sym_ns'] and node.text not in clj_kwds:
        print(str(node.text, encoding='utf-8'), end=' ')

    for child in node.children:
        print_clojure(child, in_fun or is_defn)

    if is_defn:
        print('x')


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
    print()

