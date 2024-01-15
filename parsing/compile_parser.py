from tree_sitter import Language

Language.build_library(
    "build/parser_bindings.so", [
        "parsers/tree-sitter-c",
        "parsers/tree-sitter-clojure",
        "parsers/tree-sitter-elixir",
        "parsers/tree-sitter-fortran",
        "parsers/tree-sitter-haskell",
        "parsers/tree-sitter-java",
        "parsers/tree-sitter-javascript",
        "parsers/tree-sitter-ocaml/ocaml",
        "parsers/tree-sitter-python",
    ]
)
