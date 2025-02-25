# Simple script to test language parsing.
# To run:
# > poetry shell
# > python scripts/print -l clojure -i examples/clojure.clj

import argparse
import os
from collections import defaultdict

from tree_sitter import Language, Parser



def print_ast(node, depth=0):
    text = str(node.text[:20], encoding="utf-8")
    print("  " * depth + f"<{node.type}> {text}")

    for child in node.children:
        if child.type != "comment":
            print_ast(child, depth + 1)


def print_lang(node, extract_fn):
    acc = defaultdict(list)
    extract_fn(node, acc, unique_id())

    for fun, names in acc.items():
        print(f'{fun}: {", ".join(names)}')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--lang", help="language")
    parser.add_argument("-i", "--input", help="input file path")
    parser.add_argument("--ast", action="store_true")
    args = parser.parse_args()
    input_file = args.input

    if not os.path.exists(input_file):
        raise FileNotFoundError(f"File not found: {input_file}")

    with open(input_file, "r") as file:
        content = file.read()

    language = Language("build/parser_bindings.so", args.lang)
    parser = Parser()
    parser.set_language(language)
    tree = parser.parse(bytes(content, "utf-8"))

    if args.ast:
        print_ast(tree.root_node)
    else:
        print_lang(tree.root_node, globals()[f"extract_{args.lang}"])
