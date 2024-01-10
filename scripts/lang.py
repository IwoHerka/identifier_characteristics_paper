import os

LANGS = [
    "c",
    "clojure",
    "elixir",
    "erlang",
    "fortran",
    "haskell",
    "java",
    "javascript",
    "ocaml",
    "python",
]

LANG_TO_EXT = dict(
    c=[".c"],
    clojure=[".clj"],
    elixir=[".ex", ".exs"],
    erlang=[".erl", ".es", ".escript"],
    fortran=[
        ".f",
        ".for",
        ".ftn",
        ".f90",
        ".f95",
        ".f03",
        ".f08",
        ".f15",
        ".f18",
        ".fpp",
    ],
    haskell=[".hs", ".lhs"],
    java=[".java"],
    javascript=[".js"],
    ocaml=[".ml", ".mli"],
    python=[".py"],
)


def get_exts(lang):
    return LANG_TO_EXT[lang]


def is_ext_valid(lang, file):
    # Extract the file extension from the filename
    _, file_ext = os.path.splitext(file)

    if lang in LANG_TO_EXT:
        return file_ext in LANG_TO_EXT[lang]
    else:
        return False
