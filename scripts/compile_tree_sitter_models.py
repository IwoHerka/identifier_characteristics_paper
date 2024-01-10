from tree_sitter import Language

Language.build_library(
    "build/parser_bindings.so", [
        # This expects tree sitter parsers in parent directory
        "../tree-sitter-javascript",
        "../tree-sitter-python",
        "../tree-sitter-cpp",
        "../tree-sitter-elixir",
        "../tree-sitter-erlang",
        "../tree-sitter-haskell",
        "../tree-sitter-clojure",
    ]
)
