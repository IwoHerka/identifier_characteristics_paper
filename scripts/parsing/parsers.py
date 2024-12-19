import argparse
import os
import random
from collections import defaultdict
from rich.console import Console

from tree_sitter import Language, Parser

from .print import print_ast

EX_KEYWORDS = [b"def", b"defp", b"defmacro"]
CLJ_KEYWORDS = [b"defn", b"defn-", b"def", b"defmacro", b"defmethod"]

console = Console()


def unique_id():
    count = 1
    while True:
        yield count
        count += 1


def extract(parser, input_file, extract_fn):
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"file not found: {input_file}")

    content = None
    try:
        with open(input_file, "r") as file:
            content = file.read()
            content = bytes(content, "utf-8")
    except:
        with open(input_file, "rb") as file:
            content = file.read()

    tree = parser.parse(content)
    acc = defaultdict(list)
    extract_fn(tree.root_node, acc, unique_id())
    return acc


def extract_clojure(node, acc, ids, in_fun=False, name=None):
    is_defn = node.type == "list_lit" and node.children[1].text in CLJ_KEYWORDS

    if is_defn:
        name = f'{str(node.children[2].text, encoding="utf-8")}#{next(ids)}'

    if in_fun and node.type in ["sym_name", "sym_ns"] and node.text not in CLJ_KEYWORDS:
        acc[name].append(str(node.text, encoding="utf-8"))

    for child in node.children:
        extract_clojure(child, acc, ids, in_fun or is_defn, name)


def extract_haskell(node, acc, ids, in_fun=False, name=None):
    is_defn = node.type == "function"

    if is_defn:
        name = f'{str(node.children[0].text, encoding="utf-8")}#{next(ids)}'

    if in_fun and node.type in ["variable"]:
        acc[name].append(str(node.text, encoding="utf-8"))

    for child in node.children:
        extract_haskell(child, acc, ids, in_fun or is_defn, name)


def extract_elixir(node, acc, ids, in_fun=False, name=None):
    is_defn = node.type == "call" and node.children[0].text in [b"def", b"defp"]

    if is_defn:
        f_name = str(node.children[1].children[0].children[0].text, encoding="utf-8")

        if "(" in f_name:
            f_name = f_name.split("(")[0]

        name = f"{f_name}#{next(ids)}"

    if in_fun and node.type == "identifier" and node.text not in EX_KEYWORDS:
        acc[name].append(str(node.text, encoding="utf-8"))

    for child in node.children:
        extract_elixir(child, acc, ids, in_fun or is_defn, name)


def extract_erlang(node, acc, ids, in_fun=False, name=None):
    is_defn = node.type == "fun_decl"

    if is_defn:
        name = f'{str(node.children[0].children[0].text, encoding="utf-8")}#{next(ids)}'

    if in_fun and node.type in ["atom", "var"]:
        acc[name].append(str(node.text, encoding="utf-8"))

    for child in node.children:
        extract_erlang(child, acc, ids, in_fun or is_defn, name)


def extract_python(node, acc, ids, in_fun=False, name=None):
    is_defn = node.type == "function_definition"

    if is_defn:
        name = f'{str(node.children[1].text, encoding="utf-8")}#{next(ids)}'

    if in_fun and node.type == "identifier" and node.parent.type != "type":
        acc[name].append(str(node.text, encoding="utf-8"))

    for child in node.children:
        extract_python(child, acc, ids, in_fun or is_defn, name)


def extract_javascript(node, acc, ids, in_fun=False, name=None):
    is_defn = node.type in [
        "function",
        "function_declaration",
        "arrow_function",
        "method_definition",
        "generator_function_declaration",
    ]

    if is_defn:
        if (
            node.type in ["function", "arrow_function"]
            and node.parent.type == "variable_declarator"
        ):
            f_name = str(node.parent.children[0].text, encoding="utf-8")
            name = f"{f_name}#{next(ids)}"
            acc[name].append(f_name)
        elif node.type == "function_declaration":
            if node.children[0].type == "async":
                name = f'{str(node.children[2].text, encoding="utf-8")}#{next(ids)}'
            else:
                name = f'{str(node.children[1].text, encoding="utf-8")}#{next(ids)}'
        elif node.type == "method_definition":
            f_name = str(node.children[0].text, encoding="utf-8")
            name = f"{f_name}#{next(ids)}"
            acc[name].append(f_name)
        elif node.type == "generator_function_declaration":
            name = f'{str(node.children[2].text, encoding="utf-8")}#{next(ids)}'

    if in_fun and node.type == "identifier":
        acc[name].append(str(node.text, encoding="utf-8"))

    for child in node.children:
        extract_javascript(child, acc, ids, in_fun or is_defn, name)


def extract_c(node, acc, ids, in_fun=False, name=None):
    is_defn = node.type == "function_definition"

    if is_defn:
        decl = find_child(node.children, "function_declarator")
        if decl:
            name = f'{str(decl.children[0].text, encoding="utf-8")}'
        else:
            is_defn = False

    if in_fun and node.type == "identifier":
        acc[name].append(str(node.text, encoding="utf-8"))

    for child in node.children:
        try:
            extract_c(child, acc, ids, in_fun or is_defn, name)
        except:
            pass


def find_child(children, node_type, direct=False):
    for child in children:
        if child.type == node_type:
            return child
        elif not direct:
            found = find_child(child.children, node_type)

            if found:
                return found


def extract_fortran(node, acc, ids, in_fun=False, name=None):
    is_defn = (
        node.type == "function"
        and node.children
        and node.children[0].type == "function_statement"
    )
    is_defn = is_defn or (
        node.type == "subroutine"
        and node.children
        and node.children[0].type == "subroutine_statement"
    )

    if is_defn:
        name_node = find_child(node.children[0].children, "name", True)
        f_name = str(name_node.text, encoding="utf-8")
        name = f"{f_name}#{next(ids)}"
        acc[name].append(f_name)

    if in_fun and node.type in ["identifier"]:
        acc[name].append(str(node.text, encoding="utf-8"))

    for child in node.children:
        extract_fortran(child, acc, ids, in_fun or is_defn, name)


def extract_java(node, acc, ids, in_fun=False, name=None):
    is_defn = node.type == "method_declaration"

    if is_defn:
        name_node = find_child(node.children, "identifier", True)
        name = f'{str(name_node.text, encoding="utf-8")}#{next(ids)}'

    if in_fun and node.type == "identifier":
        acc[name].append(str(node.text, encoding="utf-8"))

    for child in node.children:
        extract_java(child, acc, ids, in_fun or is_defn, name)


def extract_ocaml(node, acc, ids, in_fun=False, name=None):
    is_defn = (
        not in_fun
        and node.type == "let_binding"
        and find_child(node.children, "parameter", True)
    )

    if is_defn:
        f_name = str(node.children[0].text, encoding="utf-8")
        name = f_name  # f'{f_name}#{next(ids)}'
        # acc[name].append(f_name)

    if in_fun and node.type == "value_name":
        acc[name].append(str(node.text, encoding="utf-8"))

    for child in node.children:
        extract_ocaml(child, acc, ids, in_fun or is_defn, name)
